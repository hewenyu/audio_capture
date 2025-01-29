//go:build windows

package api

/*
#cgo CXXFLAGS: -std=c++11 -DWIN32_LEAN_AND_MEAN
#cgo LDFLAGS: -L${SRCDIR}/../build -lwasapi_capture -lole32 -loleaut32 -lwinmm -luuid -ladvapi32 -lstdc++
#include "../c/windows/wasapi_capture.h"
*/
import "C"
import (
	"fmt"
	"unsafe"

	"golang.org/x/sys/windows"
)

type windowsAudioCapture struct {
	handle   unsafe.Pointer
	callback AudioCallback
}

func newPlatformAudioCapture() AudioCapture {
	return &windowsAudioCapture{}
}

func (w *windowsAudioCapture) Initialize() error {
	w.handle = C.wasapi_capture_create()
	if w.handle == nil {
		return fmt.Errorf("failed to create wasapi capture")
	}
	if C.wasapi_capture_initialize(w.handle) == 0 {
		return fmt.Errorf("failed to initialize wasapi capture")
	}
	return nil
}

func (w *windowsAudioCapture) Start() error {
	if C.wasapi_capture_start(w.handle) == 0 {
		return fmt.Errorf("failed to start capture")
	}
	return nil
}

func (w *windowsAudioCapture) Stop() {
	C.wasapi_capture_stop(w.handle)
}

//export goAudioCallback
func goAudioCallback(userData unsafe.Pointer, buffer *C.float, frames C.int) {
	capture := (*windowsAudioCapture)(userData)
	if capture.callback != nil {
		data := unsafe.Slice((*float32)(unsafe.Pointer(buffer)), int(frames))
		capture.callback(data)
	}
}

func (w *windowsAudioCapture) SetCallback(callback AudioCallback) {
	w.callback = callback
	C.wasapi_capture_set_callback(w.handle, C.audio_callback(C.goAudioCallback), unsafe.Pointer(w))
}

func (w *windowsAudioCapture) GetFormat() AudioFormat {
	return AudioFormat{
		SampleRate:    44100,
		Channels:      2,
		BitsPerSample: 32,
	}
}

func (w *windowsAudioCapture) ListApplications() map[uint32]string {
	const maxApps = 32
	apps := make([]C.AudioAppInfo, maxApps)
	count := int(C.wasapi_capture_get_applications(w.handle, &apps[0], C.int(maxApps)))

	result := make(map[uint32]string)
	for i := 0; i < count; i++ {
		pid := uint32(apps[i].pid)
		nameBytes := C.GoBytes(unsafe.Pointer(&apps[i].name[0]), C.int(260*2))
		name := windows.UTF16ToString(*(*[]uint16)(unsafe.Pointer(&nameBytes)))
		if name != "" {
			result[pid] = name
		}
	}

	return result
}

func (w *windowsAudioCapture) Cleanup() {
	if w.handle != nil {
		C.wasapi_capture_destroy(w.handle)
		w.handle = nil
	}
}
