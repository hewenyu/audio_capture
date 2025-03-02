# Audio Capture

一个强大的跨平台音频捕获库，支持 Windows 和 Linux 系统，用于 Go 语言开发。该库允许捕获系统音频或特定应用程序的音频输出。

## 特性

- 零依赖安装：无需安装任何额外的开发环境或依赖
- 跨平台支持：
  - Windows: 使用 WASAPI (Windows Audio Session API)
  - Linux: 使用 PulseAudio
- 音频捕获功能：
  - 支持系统全局音频捕获
  - 支持特定应用程序音频捕获
  - 实时音频数据回调
  - 可配置的音频格式（采样率、声道数、位深度）
- 工具支持：
  - WAV 文件写入工具
  - 音频格式转换
- 应用程序管理：
  - 列出正在播放音频的应用程序
  - 按进程 ID 选择要捕获的应用程序

## 快速开始

### 安装

只需一行命令即可安装：

```bash
go get github.com/hewenyu/audio_capture@latest
```

### 基本用法

```go
package main

import (
    "fmt"
    "time"
    "github.com/hewenyu/audio_capture/api"
)

func main() {
    // 创建音频捕获实例
    capture := api.NewAudioCapture()
    
    // 初始化
    if err := capture.Initialize(); err != nil {
        panic(err)
    }
    defer capture.Cleanup()
    
    // 设置音频回调
    capture.SetCallback(func(data []float32) {
        // 在这里处理音频数据
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

### 录制到 WAV 文件

```go
package main

import (
    "fmt"
    "github.com/hewenyu/audio_capture/api"
    "github.com/hewenyu/audio_capture/utils"
)

func main() {
    // 创建音频捕获实例
    capture := api.NewAudioCapture()

    // 初始化
    if err := capture.Initialize(); err != nil {
        fmt.Printf("初始化失败: %v\n", err)
        return
    }
    defer capture.Cleanup()

    // 创建 WAV 文件写入器
    wavWriter, err := utils.NewWavWriter(
        "output.wav",
        16000,  // 采样率
        1,      // 单声道
        16,     // 16位深度
    )
    if err != nil {
        fmt.Printf("创建WAV文件失败: %v\n", err)
        return
    }
    defer wavWriter.Close()

    // 设置音频回调
    capture.SetCallback(func(data []float32) {
        wavWriter.WriteFloat32(data)
    })

    // 开始录音
    if err := capture.Start(); err != nil {
        fmt.Printf("开始录音失败: %v\n", err)
        return
    }

    fmt.Println("按回车键停止录音...")
    fmt.Scanln()

    // 停止录音
    capture.Stop()
}
```

### 捕获特定应用程序的音频

```go
package main

import (
    "fmt"
    "github.com/hewenyu/audio_capture/api"
)

func main() {
    capture := api.NewAudioCapture()
    if err := capture.Initialize(); err != nil {
        fmt.Printf("初始化失败: %v\n", err)
        return
    }
    defer capture.Cleanup()

    // 列出正在播放音频的应用
    apps := capture.ListApplications()
    fmt.Println("可用的应用程序:")
    for pid, name := range apps {
        fmt.Printf("  %d: %s\n", pid, name)
    }

    // 选择要捕获的应用程序
    var pid uint32
    fmt.Print("输入要捕获的应用程序PID: ")
    fmt.Scanf("%d", &pid)

    // 开始捕获特定应用程序的音频
    if err := capture.StartCapturingProcess(pid); err != nil {
        fmt.Printf("开始捕获失败: %v\n", err)
        return
    }

    fmt.Println("正在录制... 按回车键停止")
    fmt.Scanln()
    capture.Stop()
}
```

## 系统要求

- Go 1.21 或更高版本
- Windows 7+ 或支持 PulseAudio 的 Linux 系统

## API 文档

### AudioCapture 接口

```go
type AudioCapture interface {
    // Initialize 初始化音频捕获
    Initialize() error

    // Start 开始录音
    Start() error

    // Stop 停止录音
    Stop()

    // GetFormat 获取音频格式
    GetFormat() AudioFormat

    // SetCallback 设置音频数据回调
    SetCallback(callback AudioCallback)

    // ListApplications 列出正在播放音频的应用
    ListApplications() map[uint32]string

    // Cleanup 清理资源
    Cleanup()

    // StartCapturingProcess 开始录制指定进程的音频
    StartCapturingProcess(pid uint32) error
}
```

### AudioFormat 结构体

```go
type AudioFormat struct {
    SampleRate    int // 采样率
    Channels      int // 声道数
    BitsPerSample int // 位深度
}
```

### AudioCallback 回调函数

```go
type AudioCallback func([]float32)
```

## 贡献

欢迎提交 Pull Request 或创建 Issue。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
