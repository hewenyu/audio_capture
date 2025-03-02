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

	// 列出正在播放音频的应用
	apps, err := capture.ListApplications()
	if err != nil {
		fmt.Printf("获取应用列表失败: %v\n", err)
		os.Exit(1)
	}

	if len(apps) == 0 {
		fmt.Println("没有找到正在播放音频的应用")
		os.Exit(1)
	}

	fmt.Println("正在播放音频的应用:")
	for pid, name := range apps {
		fmt.Printf("  [%d] %s\n", pid, name)
	}

	// 选择要捕获的应用
	fmt.Print("\n请输入要捕获的应用PID: ")
	var pid uint32
	fmt.Scanf("%d", &pid)

	if _, ok := apps[pid]; !ok {
		fmt.Println("无效的PID")
		os.Exit(1)
	}

	// 设置音频回调
	var sampleCount int
	startTime := time.Now()

	capture.SetCallback(func(data []float32) {
		sampleCount += len(data)
		duration := time.Since(startTime).Seconds()
		fmt.Printf("\r已录制 %.2f 秒音频 (%d 个采样点)", duration, sampleCount)
	})

	// 开始捕获指定应用的音频
	if err := capture.StartCapturingProcess(pid); err != nil {
		fmt.Printf("\n开始捕获失败: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("\n开始捕获 [%d] %s 的音频... 按 Ctrl+C 停止\n", pid, apps[pid])

	// 等待中断信号
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	// 停止录音
	capture.Stop()
	fmt.Printf("\n\n录音已停止\n")
}
