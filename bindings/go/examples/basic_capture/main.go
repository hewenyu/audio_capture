package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/hewenyu/audio_capture/bindings/go/pkg/audio"
)

func main() {
	// 创建音频捕获实例
	capture := audio.New()

	// 初始化
	if err := capture.Initialize(); err != nil {
		fmt.Printf("初始化失败: %v\n", err)
		os.Exit(1)
	}
	defer capture.Close()

	// 获取音频格式
	format, err := capture.GetFormat()
	if err != nil {
		fmt.Printf("获取音频格式失败: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("音频格式:\n")
	fmt.Printf("  采样率: %d Hz\n", format.SampleRate)
	fmt.Printf("  声道数: %d\n", format.Channels)
	fmt.Printf("  位深度: %d bits\n", format.BitsPerSample)

	// 设置音频回调
	var sampleCount int
	startTime := time.Now()

	capture.SetCallback(func(data []float32) {
		sampleCount += len(data)
		duration := time.Since(startTime).Seconds()
		fmt.Printf("\r已录制 %.2f 秒音频 (%d 个采样点)", duration, sampleCount)
	})

	// 开始录音
	if err := capture.Start(); err != nil {
		fmt.Printf("\n开始录音失败: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("\n开始录音... 按 Ctrl+C 停止")

	// 等待中断信号
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	// 停止录音
	capture.Stop()
	fmt.Printf("\n\n录音已停止\n")
}
