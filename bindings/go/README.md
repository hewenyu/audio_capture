# Audio Capture for Go

这是 [audio_capture](https://github.com/hewenyu/audio_capture) 的 Go 语言绑定，提供了简单易用的 Go API 来捕获系统音频或特定应用程序的音频输出。

## 特性

- 跨平台支持：
  - Windows: 使用 WASAPI (Windows Audio Session API)
  - Linux: 使用 PulseAudio
- 高性能：使用 CGO 直接调用底层音频 API
- 支持捕获特定应用程序的音频

## 安装

```bash
go get github.com/hewenyu/audio_capture/bindings/go
```

## 快速开始

### 基本用法

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

    // 录制5秒
    time.Sleep(5 * time.Second)

    // 停止录音
    capture.Stop()
}
```

### 捕获特定应用程序的音频

```go
package main

import (
    "fmt"
    "github.com/hewenyu/audio_capture/bindings/go/pkg/audio"
)

func main() {
    capture := audio.New()
    if err := capture.Initialize(); err != nil {
        panic(err)
    }
    defer capture.Close()

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

    // 设置音频回调
    capture.SetCallback(func(data []float32) {
        fmt.Printf("捕获到应用程序音频: %d 个采样点\n", len(data))
    })

    // 开始捕获特定应用程序的音频
    if err := capture.StartCapturingProcess(targetPID); err != nil {
        panic(err)
    }

    // 等待用户输入
    fmt.Println("按回车键停止录音...")
    fmt.Scanln()

    // 停止录音
    capture.Stop()
}
```

## API 文档

### AudioFormat 结构体

音频格式信息：

```go
type AudioFormat struct {
    SampleRate    uint32 // 采样率
    Channels      uint32 // 声道数
    BitsPerSample uint32 // 位深度
}
```

### AudioCallback 类型

音频数据回调函数类型：

```go
type AudioCallback func([]float32)
```

### Capture 接口

主要的音频捕获接口：

```go
type Capture interface {
    // Initialize 初始化音频捕获系统
    Initialize() error

    // Start 开始录音
    Start() error

    // Stop 停止录音
    Stop()

    // GetFormat 获取音频格式
    GetFormat() (*AudioFormat, error)

    // SetCallback 设置音频数据回调
    SetCallback(callback AudioCallback)

    // ListApplications 列出正在播放音频的应用
    ListApplications() (map[uint32]string, error)

    // StartCapturingProcess 开始捕获指定进程的音频
    StartCapturingProcess(pid uint32) error

    // Close 清理资源
    Close()
}
```

## 系统要求

- Go 1.21 或更高版本
- Windows 7+ 或支持 PulseAudio 的 Linux 系统
- GCC 编译器（用于 CGO）

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../../LICENSE) 文件。 