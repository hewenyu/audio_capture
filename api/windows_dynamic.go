//go:build windows

package api

import (
	"fmt"
	"sync"
	"syscall"
	"unsafe"

	"golang.org/x/sys/windows"
)

// 函数原型定义
type (
	wasapiCaptureCreate          func() uintptr
	wasapiCaptureInitialize      func(handle uintptr) int32
	wasapiCaptureStart           func(handle uintptr) int32
	wasapiCaptureStop            func(handle uintptr)
	wasapiCaptureDestroy         func(handle uintptr)
	wasapiCaptureSetCallback     func(handle uintptr, callback uintptr, userData uintptr)
	wasapiCaptureGetFormat       func(handle uintptr, format *AudioFormat) int32
	wasapiCaptureGetApplications func(handle uintptr, apps *AudioAppInfo, maxCount int32) int32
	wasapiCaptureStartProcess    func(handle uintptr, pid uint32) int32
)

// 动态库函数
var (
	procCreate          wasapiCaptureCreate
	procInitialize      wasapiCaptureInitialize
	procStart           wasapiCaptureStart
	procStop            wasapiCaptureStop
	procDestroy         wasapiCaptureDestroy
	procSetCallback     wasapiCaptureSetCallback
	procGetFormat       wasapiCaptureGetFormat
	procGetApplications wasapiCaptureGetApplications
	procStartProcess    wasapiCaptureStartProcess
)

// AudioAppInfo 应用程序信息
type AudioAppInfo struct {
	PID  uint32
	Name [260]uint16
}

// 全局回调管理器
var (
	callbackMu   sync.RWMutex
	callbackMap  = make(map[uintptr]*windowsAudioCapture)
	globalBuffer = make([]float32, 0, 4096)
)

type windowsAudioCapture struct {
	handle   uintptr
	callback AudioCallback
	format   AudioFormat
	lib      *windows.LazyDLL
}

func newPlatformAudioCapture() AudioCapture {
	return &windowsAudioCapture{}
}

func (w *windowsAudioCapture) Initialize() error {
	// 加载动态库
	libPath, err := ensureLibraryLoaded()
	if err != nil {
		return fmt.Errorf("failed to load library: %v", err)
	}

	// 加载DLL
	w.lib = windows.NewLazyDLL(libPath)
	if err := w.lib.Load(); err != nil {
		return fmt.Errorf("failed to load DLL: %v", err)
	}

	// 加载所有函数
	create := w.lib.NewProc("wasapi_capture_create")
	initialize := w.lib.NewProc("wasapi_capture_initialize")
	start := w.lib.NewProc("wasapi_capture_start")
	stop := w.lib.NewProc("wasapi_capture_stop")
	destroy := w.lib.NewProc("wasapi_capture_destroy")
	setCallback := w.lib.NewProc("wasapi_capture_set_callback")
	getFormat := w.lib.NewProc("wasapi_capture_get_format")
	getApplications := w.lib.NewProc("wasapi_capture_get_applications")
	startProcess := w.lib.NewProc("wasapi_capture_start_process")

	// 设置函数指针
	procCreate = func() uintptr {
		ret, _, _ := create.Call()
		return ret
	}
	procInitialize = func(handle uintptr) int32 {
		ret, _, _ := initialize.Call(handle)
		return int32(ret)
	}
	procStart = func(handle uintptr) int32 {
		ret, _, _ := start.Call(handle)
		return int32(ret)
	}
	procStop = func(handle uintptr) {
		stop.Call(handle)
	}
	procDestroy = func(handle uintptr) {
		destroy.Call(handle)
	}
	procSetCallback = func(handle uintptr, callback uintptr, userData uintptr) {
		setCallback.Call(handle, callback, userData)
	}
	procGetFormat = func(handle uintptr, format *AudioFormat) int32 {
		ret, _, _ := getFormat.Call(handle, uintptr(unsafe.Pointer(format)))
		return int32(ret)
	}
	procGetApplications = func(handle uintptr, apps *AudioAppInfo, maxCount int32) int32 {
		ret, _, _ := getApplications.Call(handle, uintptr(unsafe.Pointer(apps)), uintptr(maxCount))
		return int32(ret)
	}
	procStartProcess = func(handle uintptr, pid uint32) int32 {
		ret, _, _ := startProcess.Call(handle, uintptr(pid))
		return int32(ret)
	}

	// 创建实例
	w.handle = procCreate()
	if w.handle == 0 {
		return fmt.Errorf("failed to create wasapi capture")
	}

	// 初始化
	if procInitialize(w.handle) == 0 {
		return fmt.Errorf("failed to initialize wasapi capture")
	}

	// 获取格式信息
	var format AudioFormat
	if procGetFormat(w.handle, &format) == 0 {
		return fmt.Errorf("failed to get audio format")
	}

	w.format = format

	// 注册到全局回调映射
	callbackMu.Lock()
	callbackMap[w.handle] = w
	callbackMu.Unlock()

	return nil
}

func (w *windowsAudioCapture) Start() error {
	if procStart(w.handle) == 0 {
		return fmt.Errorf("failed to start capture")
	}
	return nil
}

func (w *windowsAudioCapture) Stop() {
	procStop(w.handle)
}

func (w *windowsAudioCapture) SetCallback(callback AudioCallback) {
	w.callback = callback
	// TODO: Implement callback mechanism
}

func (w *windowsAudioCapture) GetFormat() AudioFormat {
	return w.format
}

func (w *windowsAudioCapture) ListApplications() map[uint32]string {
	const maxApps = 32
	apps := make([]AudioAppInfo, maxApps)
	count := procGetApplications(w.handle, &apps[0], maxApps)

	result := make(map[uint32]string)
	for i := 0; i < int(count); i++ {
		pid := apps[i].PID
		name := syscall.UTF16ToString(apps[i].Name[:])
		if name != "" {
			result[pid] = name
		}
	}

	return result
}

func (w *windowsAudioCapture) Cleanup() {
	if w.handle != 0 {
		// 从全局回调映射中移除
		callbackMu.Lock()
		delete(callbackMap, w.handle)
		callbackMu.Unlock()

		procDestroy(w.handle)
		w.handle = 0
	}
}

func (w *windowsAudioCapture) StartCapturingProcess(pid uint32) error {
	if procStartProcess(w.handle, pid) == 0 {
		return fmt.Errorf("failed to start capturing process %d", pid)
	}
	return nil
}
