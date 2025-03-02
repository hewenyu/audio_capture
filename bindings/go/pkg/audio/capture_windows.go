package audio

/*
#cgo CFLAGS: -I${SRCDIR}
#cgo windows LDFLAGS: -l:libwasapi_capture.a -static -lole32 -loleaut32 -lwinmm -luuid -lstdc++

#include <stdlib.h>
#include "wasapi_capture.h"

extern void goAudioCallback(void* user_data, float* buffer, int frames);
*/
import "C"
import (
	"fmt"
	"runtime"
	"sync"
	"syscall"
	"unsafe"
)

// 全局回调映射表，用于存储回调函数
var (
	callbackMapMutex sync.RWMutex
	callbackMap      = make(map[uintptr]AudioCallback)
	nextCallbackID   uintptr
)

// 注册回调函数，返回一个唯一的ID
func registerCallback(callback AudioCallback) uintptr {
	callbackMapMutex.Lock()
	defer callbackMapMutex.Unlock()

	id := nextCallbackID
	nextCallbackID++
	callbackMap[id] = callback
	return id
}

// 获取回调函数
func getCallback(id uintptr) AudioCallback {
	callbackMapMutex.RLock()
	defer callbackMapMutex.RUnlock()

	return callbackMap[id]
}

// 取消注册回调函数
func unregisterCallback(id uintptr) {
	callbackMapMutex.Lock()
	defer callbackMapMutex.Unlock()

	delete(callbackMap, id)
}

type windowsCapture struct {
	handle     unsafe.Pointer
	callbackID uintptr
	mu         sync.Mutex
}

//export goAudioCallback
func goAudioCallback(userData unsafe.Pointer, buffer *C.float, frames C.int) {
	if userData == nil {
		return
	}

	// 从用户数据中获取回调ID
	callbackID := uintptr(userData)

	// 获取回调函数
	callback := getCallback(callbackID)
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
	return &windowsCapture{}
}

func (c *windowsCapture) Initialize() error {
	c.handle = C.wasapi_capture_create()
	if c.handle == nil {
		return fmt.Errorf("failed to create audio capture instance")
	}

	runtime.SetFinalizer(c, (*windowsCapture).Close)

	if C.wasapi_capture_initialize(c.handle) == 0 {
		return fmt.Errorf("failed to initialize audio capture")
	}

	return nil
}

func (c *windowsCapture) Start() error {
	if c.handle == nil {
		return fmt.Errorf("audio capture not initialized")
	}

	if C.wasapi_capture_start(c.handle) == 0 {
		return fmt.Errorf("failed to start audio capture")
	}

	return nil
}

func (c *windowsCapture) Stop() {
	if c.handle != nil {
		C.wasapi_capture_stop(c.handle)
	}
}

func (c *windowsCapture) GetFormat() (*AudioFormat, error) {
	if c.handle == nil {
		return nil, fmt.Errorf("audio capture not initialized")
	}

	var format C.AudioFormat
	if C.wasapi_capture_get_format(c.handle, &format) == 0 {
		return nil, fmt.Errorf("failed to get audio format")
	}

	return &AudioFormat{
		SampleRate:    uint32(format.sample_rate),
		Channels:      uint32(format.channels),
		BitsPerSample: uint32(format.bits_per_sample),
	}, nil
}

func (c *windowsCapture) SetCallback(callback AudioCallback) {
	c.mu.Lock()

	// 如果已经有回调，先取消注册
	if c.callbackID != 0 {
		unregisterCallback(c.callbackID)
		c.callbackID = 0
	}

	// 注册新的回调
	if callback != nil {
		c.callbackID = registerCallback(callback)
	}

	c.mu.Unlock()

	if c.handle != nil && c.callbackID != 0 {
		// 直接使用回调ID作为用户数据
		C.wasapi_capture_set_callback(c.handle, (*[0]byte)(C.goAudioCallback), unsafe.Pointer(c.callbackID))
	} else if c.handle != nil {
		// 清除回调
		C.wasapi_capture_set_callback(c.handle, nil, nil)
	}
}

func (c *windowsCapture) ListApplications() (map[uint32]string, error) {
	if c.handle == nil {
		return nil, fmt.Errorf("audio capture not initialized")
	}

	const maxApps = 32
	var apps [maxApps]C.AudioAppInfo
	count := C.wasapi_capture_get_applications(c.handle, &apps[0], C.int(maxApps))

	result := make(map[uint32]string)
	for i := 0; i < int(count); i++ {
		if apps[i].name[0] != 0 {
			namePtr := (*uint16)(unsafe.Pointer(&apps[i].name[0]))
			name := syscall.UTF16ToString((*[260]uint16)(unsafe.Pointer(namePtr))[:])
			result[uint32(apps[i].pid)] = name
		}
	}

	return result, nil
}

func (c *windowsCapture) StartCapturingProcess(pid uint32) error {
	if c.handle == nil {
		return fmt.Errorf("audio capture not initialized")
	}

	if C.wasapi_capture_start_process(c.handle, C.uint(pid)) == 0 {
		return fmt.Errorf("failed to start capturing process %d", pid)
	}

	return nil
}

func (c *windowsCapture) Close() {
	c.mu.Lock()
	defer c.mu.Unlock()

	// 取消注册回调
	if c.callbackID != 0 {
		unregisterCallback(c.callbackID)
		c.callbackID = 0
	}

	if c.handle != nil {
		C.wasapi_capture_destroy(c.handle)
		c.handle = nil
	}
}
