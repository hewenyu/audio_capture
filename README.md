# Audio Capture

一个强大的跨平台音频捕获库，支持 Windows 和 Linux 系统，用于 Go 语言开发。该库允许捕获系统音频或特定应用程序的音频输出。

## 功能特性

- 跨平台支持
  - Windows: 使用 WASAPI (Windows Audio Session API)
  - Linux: 使用 PulseAudio
- 音频捕获功能
  - 支持系统全局音频捕获
  - 支持特定应用程序音频捕获
  - 实时音频数据回调
  - 可配置的音频格式（采样率、声道数、位深度）
- 工具支持
  - WAV 文件写入工具
  - 音频格式转换
- 应用程序管理
  - 列出正在播放音频的应用程序
  - 按进程 ID 选择要捕获的应用程序

## 系统要求

### Windows
- Windows 7 或更高版本
- Go 1.21 或更高版本
- C++ 编译器（支持 C++11）
- Windows SDK

### Linux
- PulseAudio
- Go 1.21 或更高版本
- GCC

## 安装

```bash
go get github.com/hewenyu/audio_capture
```

### Windows 依赖项
确保系统已安装：
- Visual Studio 或 MinGW（支持 C++11）
- Windows SDK

### Linux 依赖项
安装 PulseAudio 开发库：
```bash
# Ubuntu/Debian
sudo apt-get install libpulse-dev

# CentOS/RHEL
sudo yum install pulseaudio-libs-devel
```

## 使用示例

### 基本用法

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

    // 等待用户输入以停止录音
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

## API 文档

### AudioCapture 接口

```go
type AudioCapture interface {
    Initialize() error                    // 初始化音频捕获
    Start() error                        // 开始录音
    Stop()                               // 停止录音
    GetFormat() AudioFormat              // 获取音频格式
    SetCallback(callback AudioCallback)   // 设置音频数据回调
    ListApplications() map[uint32]string // 列出正在播放音频的应用
    Cleanup()                            // 清理资源
    StartCapturingProcess(pid uint32) error // 开始录制指定进程的音频
}
```

### AudioFormat 结构体

```go
type AudioFormat struct {
    SampleRate    int // 采样率
    Channels      int // 声道数
    BitsPerSample int // 采样位深
}
```

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 注意事项

1. Windows 平台需要管理员权限才能捕获其他应用程序的音频
2. 在 Linux 上需要确保 PulseAudio 服务正在运行
3. 高采样率和多声道可能会占用较多系统资源
4. 建议在处理音频数据时使用缓冲区，避免数据丢失
