# 快速入门指南

这个指南将帮助你快速开始使用audio_capture库来捕获音频。

## 安装

只需一行命令即可安装：

```bash
go get github.com/hewenyu/audio_capture/bindings/go@latest
```

## 基本用法

### 捕获系统音频

```go
package main

import (
	"fmt"
	"time"
	"github.com/hewenyu/audio_capture/bindings/go/pkg/audio"
)

func main() {
	// 创建音频捕获实例
	capture := audio.New()

	// 初始化
	if err := capture.Initialize(); err != nil {
		panic(err)
	}
	defer capture.Close()

	// 设置音频回调
	capture.SetCallback(func(data []float32) {
		fmt.Printf("收到音频数据: %d 个采样点\n", len(data))
	})

	// 开始录音
	if err := capture.Start(); err != nil {
		panic(err)
	}

	fmt.Println("正在录音，按Ctrl+C停止...")
	// 录制10秒
	time.Sleep(10 * time.Second)

	// 停止录音
	capture.Stop()
}
```

### 捕获特定应用程序的音频

```go
// 列出正在播放音频的应用
apps, err := capture.ListApplications()
if err != nil {
	panic(err)
}

fmt.Println("可用的应用程序:")
for pid, name := range apps {
	fmt.Printf("  %d: %s\n", pid, name)
}

// 假设我们要捕获第一个应用的音频
var targetPID uint32
for pid := range apps {
	targetPID = pid
	break
}

// 开始捕获特定应用程序的音频
if err := capture.StartCapturingProcess(targetPID); err != nil {
	panic(err)
}
```

### 保存为WAV文件

```go
// 获取音频格式
format, err := capture.GetFormat()
if err != nil {
	panic(err)
}

// 创建WAV文件写入器
wavWriter, err := audio.NewWavWriter("output.wav", format)
if err != nil {
	panic(err)
}
defer wavWriter.Close()

// 设置回调将音频数据写入WAV文件
capture.SetCallback(func(data []float32) {
	if err := wavWriter.WriteFloat32(data); err != nil {
		fmt.Printf("写入WAV文件失败: %v\n", err)
	}
})
```

## 更多信息

- 详细安装指南：[INSTALL.md](./INSTALL.md)
- API文档：[README.md#api-文档](./README.md#api-文档)
- 完整示例：[examples/app_capture](./examples/app_capture) 