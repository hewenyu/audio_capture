//go:build windows

package api

/*
#cgo CXXFLAGS: -std=c++11
#cgo LDFLAGS: -L${SRCDIR}/../build -lwasapi_capture -lole32 -loleaut32 -lwinmm -luuid
#include "../c/windows/wasapi_capture.h"
*/
import "C"
import (
	"fmt"
	"unsafe"
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
