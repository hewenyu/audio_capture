//go:build windows

package audio

/*
#cgo CXXFLAGS: -std=c++11 -DWIN32_LEAN_AND_MEAN
#cgo LDFLAGS: -L${SRCDIR}/../build -lwasapi_capture -lole32 -loleaut32 -lwinmm -luuid -ladvapi32 -lstdc++
#include "../c/windows/wasapi_capture.h"
*/
import "C"
import (
	"fmt"
	"sync"
	"unsafe"

	"golang.org/x/sys/windows"
)

// 全局回调管理器
var (
	callbackMu   sync.RWMutex
	callbackMap  = make(map[unsafe.Pointer]*windowsAudioCapture)
	globalBuffer = make([]float32, 0, 4096)
)

// 添加新的结构体用于存储音频格式
type audioFormat struct {
	sampleRate    int
	channels      int
	bitsPerSample int
}

type windowsAudioCapture struct {
	handle   unsafe.Pointer
	callback AudioCallback
	format   audioFormat // 添加格式字段
}

func newPlatformAudioCapture() AudioCapture {
	return &windowsAudioCapture{}
}

//export goAudioCallback
func goAudioCallback(userData unsafe.Pointer, buffer *C.float, frames C.int) {
	callbackMu.RLock()
	capture, ok := callbackMap[userData]
	callbackMu.RUnlock()

	if !ok || capture.callback == nil {
		return
	}

	// 使用全局缓冲区
	callbackMu.Lock()
	if cap(globalBuffer) < int(frames) {
		globalBuffer = make([]float32, int(frames))
	}
	globalBuffer = globalBuffer[:int(frames)]

	// 复制数据
	src := unsafe.Slice((*float32)(unsafe.Pointer(buffer)), int(frames))
	copy(globalBuffer, src)

	// 创建数据副本用于回调
	dataCopy := make([]float32, len(globalBuffer))
	copy(dataCopy, globalBuffer)
	callbackMu.Unlock()

	// 调用回调
	capture.callback(dataCopy)
}

func (w *windowsAudioCapture) Initialize() error {
	handle := C.wasapi_capture_create()
	if handle == nil {
		return fmt.Errorf("failed to create wasapi capture")
	}
	w.handle = handle

	if C.wasapi_capture_initialize(handle) == 0 {
		return fmt.Errorf("failed to initialize wasapi capture")
	}

	// 获取格式信息
	var format C.AudioFormat
	if C.wasapi_capture_get_format(handle, &format) == 0 {
		return fmt.Errorf("failed to get audio format")
	}

	w.format = audioFormat{
		sampleRate:    int(format.sample_rate),
		channels:      int(format.channels),
		bitsPerSample: int(format.bits_per_sample),
	}

	// 注册到全局回调映射
	callbackMu.Lock()
	callbackMap[w.handle] = w
	callbackMu.Unlock()

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

func (w *windowsAudioCapture) SetCallback(callback AudioCallback) {
	w.callback = callback
	C.wasapi_capture_set_callback(w.handle, C.audio_callback(C.goAudioCallback), w.handle)
}

func (w *windowsAudioCapture) GetFormat() AudioFormat {
	return AudioFormat{
		SampleRate:    w.format.sampleRate,
		Channels:      w.format.channels,
		BitsPerSample: w.format.bitsPerSample,
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
		// 从全局回调映射中移除
		callbackMu.Lock()
		delete(callbackMap, w.handle)
		callbackMu.Unlock()

		C.wasapi_capture_destroy(w.handle)
		w.handle = nil
	}
}

func (w *windowsAudioCapture) StartCapturingProcess(pid uint32) error {
	if C.wasapi_capture_start_process(w.handle, C.uint(pid)) == 0 {
		return fmt.Errorf("failed to start capturing process %d", pid)
	}
	return nil
}
