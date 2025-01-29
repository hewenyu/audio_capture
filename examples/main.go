package main

import (
	"fmt"
	"time"

	"github.com/hewenyu/audio_capture/api"
)

func main() {
	capture := api.NewAudioCapture()

	err := capture.Initialize()
	if err != nil {
		fmt.Printf("Failed to initialize: %v\n", err)
		return
	}
	defer capture.Cleanup()

	capture.SetCallback(func(data []float32) {
		fmt.Printf("Received %d samples\n", len(data))
	})

	apps := capture.ListApplications()
	fmt.Println("Available applications:")
	for pid, name := range apps {
		fmt.Printf("PID: %d, Name: %s\n", pid, name)
	}

	err = capture.Start()
	if err != nil {
		fmt.Printf("Failed to start: %v\n", err)
		return
	}

	// 录制5秒
	time.Sleep(5 * time.Second)

	capture.Stop()
}
