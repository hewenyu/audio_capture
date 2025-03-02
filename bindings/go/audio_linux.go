//go:build linux

package go

/*
#cgo LDFLAGS: -lpulse -lpulse-simple
#include "../c/linux/pulse_capture.h"
*/
import "C"
import "unsafe"

type linuxAudioCapture struct {
	handle   unsafe.Pointer
	callback AudioCallback
}

func newPlatformAudioCapture() AudioCapture {
	return &linuxAudioCapture{}
}

// ... Linux实现类似Windows的方式
