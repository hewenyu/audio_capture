//go:build linux
// +build linux

package audio

/*
#cgo CFLAGS: -I${SRCDIR}/../../../c/linux
#cgo LDFLAGS: -L${SRCDIR}/../../../c/linux -lpulse_capture

#include <stdlib.h>
#include "pulse_capture.h"

extern void goAudioCallback(void* user_data, float* buffer, int frames);
*/
import "C"
import (
	"fmt"
	"runtime"
	"sync"
	"unsafe"
)

type linuxCapture struct {
	handle   unsafe.Pointer
	callback AudioCallback
	mu       sync.Mutex
}

//export goAudioCallback
func goAudioCallback(userData unsafe.Pointer, buffer *C.float, frames C.int) {
	if userData == nil {
		return
	}

	capture := (*linuxCapture)(userData)
	capture.mu.Lock()
	callback := capture.callback
	capture.mu.Unlock()

	if callback == nil {
		return
	}

	// Convert C array to Go slice
	data := unsafe.Slice((*float32)(unsafe.Pointer(buffer)), int(frames))

	// Make a copy of the data to avoid race conditions
	dataCopy := make([]float32, len(data))
	copy(dataCopy, data)

	// Call the user callback
	callback(dataCopy)
}

func newPlatformCapture() Capture {
	return &linuxCapture{}
}

func (c *linuxCapture) Initialize() error {
	c.handle = C.pulse_capture_create()
	if c.handle == nil {
		return fmt.Errorf("failed to create audio capture instance")
	}

	runtime.SetFinalizer(c, (*linuxCapture).Close)

	if C.pulse_capture_initialize(c.handle) == 0 {
		return fmt.Errorf("failed to initialize audio capture")
	}

	return nil
}

func (c *linuxCapture) Start() error {
	if c.handle == nil {
		return fmt.Errorf("audio capture not initialized")
	}

	if C.pulse_capture_start(c.handle) == 0 {
		return fmt.Errorf("failed to start audio capture")
	}

	return nil
}

func (c *linuxCapture) Stop() {
	if c.handle != nil {
		C.pulse_capture_stop(c.handle)
	}
}

func (c *linuxCapture) GetFormat() (*AudioFormat, error) {
	if c.handle == nil {
		return nil, fmt.Errorf("audio capture not initialized")
	}

	var format C.AudioFormat
	if C.pulse_capture_get_format(c.handle, &format) == 0 {
		return nil, fmt.Errorf("failed to get audio format")
	}

	return &AudioFormat{
		SampleRate:    uint32(format.sample_rate),
		Channels:      uint32(format.channels),
		BitsPerSample: uint32(format.bits_per_sample),
	}, nil
}

func (c *linuxCapture) SetCallback(callback AudioCallback) {
	c.mu.Lock()
	c.callback = callback
	c.mu.Unlock()

	if c.handle != nil {
		C.pulse_capture_set_callback(c.handle, (*[0]byte)(C.goAudioCallback), unsafe.Pointer(c))
	}
}

func (c *linuxCapture) ListApplications() (map[uint32]string, error) {
	if c.handle == nil {
		return nil, fmt.Errorf("audio capture not initialized")
	}

	const maxApps = 32
	apps := make([]C.AudioAppInfo, maxApps)
	count := C.pulse_capture_get_applications(c.handle, unsafe.Pointer(&apps[0]), C.int(maxApps))

	result := make(map[uint32]string)
	for i := 0; i < int(count); i++ {
		if apps[i].name[0] != 0 {
			result[uint32(apps[i].pid)] = C.GoString((*C.char)(unsafe.Pointer(&apps[i].name[0])))
		}
	}

	return result, nil
}

func (c *linuxCapture) StartCapturingProcess(pid uint32) error {
	if c.handle == nil {
		return fmt.Errorf("audio capture not initialized")
	}

	if C.pulse_capture_start_process(c.handle, C.uint(pid)) == 0 {
		return fmt.Errorf("failed to start capturing process %d", pid)
	}

	return nil
}

func (c *linuxCapture) Close() {
	if c.handle != nil {
		C.pulse_capture_destroy(c.handle)
		c.handle = nil
	}
}
