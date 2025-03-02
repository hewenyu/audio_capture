package main

import (
	"fmt"
	"os"

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
}
