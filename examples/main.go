package main

import (
	"fmt"
	"os"
	"os/signal"
	"sync"
	"time"

	"github.com/hewenyu/audio_capture/api"
	"github.com/hewenyu/audio_capture/utils"
)

func main() {
	capture := api.NewAudioCapture()

	err := capture.Initialize()
	if err != nil {
		fmt.Printf("Failed to initialize: %v\n", err)
		return
	}
	defer capture.Cleanup()

	// 列出正在播放音频的应用
	apps := capture.ListApplications()
	fmt.Println("Available applications:")
	for pid, name := range apps {
		fmt.Printf("  %d: %s\n", pid, name)
	}

	// 查找Edge进程
	var edgePID uint32
	for pid, name := range apps {
		if name == `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` {
			edgePID = pid
			break
		}
	}

	if edgePID == 0 {
		fmt.Println("Microsoft Edge is not playing audio")
		return
	}

	fmt.Printf("Found Microsoft Edge (PID: %d)\n", edgePID)

	// 创建WAV文件写入器
	wavWriter, err := utils.NewWavWriter(
		fmt.Sprintf("edge_audio_%d.wav", time.Now().Unix()),
		16000, // 采样率固定为16kHz
		1,     // 单声道
		16,    // 16位深度
	)
	if err != nil {
		fmt.Printf("Failed to create WAV file: %v\n", err)
		return
	}
	defer wavWriter.Close()

	// 创建音频数据通道
	audioChan := make(chan []float32, 100)
	var wg sync.WaitGroup

	// 启动写入协程
	wg.Add(1)
	go func() {
		defer wg.Done()
		for data := range audioChan {
			if err := wavWriter.WriteFloat32(data); err != nil {
				fmt.Printf("Failed to write audio data: %v\n", err)
			}
		}
	}()

	// 设置音频回调
	capture.SetCallback(func(data []float32) {
		// 创建数据副本
		dataCopy := make([]float32, len(data))
		copy(dataCopy, data)
		// 通过通道发送数据
		select {
		case audioChan <- dataCopy:
		default:
			// 如果通道已满，丢弃数据
			fmt.Println("Warning: Audio buffer full, dropping samples")
		}
	})

	// 开始录制Edge的音频
	err = capture.StartCapturingProcess(edgePID)
	if err != nil {
		fmt.Printf("Failed to start capturing Edge audio: %v\n", err)
		return
	}

	// 设置Ctrl+C处理
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt)

	fmt.Println("Recording Edge audio... Press Ctrl+C to stop")

	// 等待Ctrl+C或超时
	select {
	case <-sigChan:
		fmt.Println("\nStopping recording...")
	case <-time.After(30 * time.Second):
		fmt.Println("\nRecording complete")
	}

	// 停止录音
	capture.Stop()
	close(audioChan)

	// 等待写入完成
	wg.Wait()

	fmt.Println("Audio saved to edge_audio.wav")
}
