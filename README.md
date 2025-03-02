# Audio Capture

一个跨平台的音频捕获库，可以捕获系统音频或特定应用程序的音频输出。该库提供了C/C++核心实现，以及Go和Python语言绑定。

## 功能特性

- **跨平台支持**：
  - Windows: 使用WASAPI (Windows Audio Session API)
  - Linux: 使用PulseAudio (计划中)
  - macOS: 使用CoreAudio (计划中)
- **多语言绑定**：
  - [Go语言绑定](./bindings/go/)
  - [Python语言绑定](./bindings/python/) (计划中)
- **应用程序级别捕获**：可以选择捕获特定应用程序的音频输出
- **高性能**：使用底层音频API，低延迟，低CPU占用
- **简单易用的API**：提供简洁的接口，易于集成到各种应用中

## 系统要求

- **Windows**：Windows 7及以上版本
- **编译工具**：
  - Windows: MinGW-w64或Visual Studio
  - Go 1.21或更高版本（用于Go绑定）

## 快速开始

### 使用Go绑定

1. **安装**

```bash
go get github.com/hewenyu/audio_capture/bindings/go
```

2. **基本用法**

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

3. **捕获特定应用程序的音频**

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

// 开始捕获特定应用程序的音频
if err := capture.StartCapturingProcess(targetPID); err != nil {
    panic(err)
}
```

4. **保存为WAV文件**

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

### 示例应用

项目包含一个完整的示例应用，可以捕获特定应用程序的音频并保存为WAV文件：

```bash
cd bindings/go/examples/app_capture
go run main.go
```

## 项目结构

```
audio_capture/
├── c/                      # C/C++核心实现
│   ├── common/             # 跨平台公共代码
│   ├── windows/            # Windows平台实现(WASAPI)
│   └── linux/              # Linux平台实现(PulseAudio)
├── bindings/               # 语言绑定
│   ├── go/                 # Go语言绑定
│   │   ├── pkg/audio/      # Go API
│   │   └── examples/       # 示例应用
│   └── python/             # Python语言绑定(计划中)
└── tests/                  # 测试代码
```

## 技术细节

### 音频格式

默认音频格式：
- 采样率：16000 Hz
- 通道数：1 (单声道)
- 位深度：16 bit

### 回调机制

库使用回调机制传递音频数据。当有新的音频数据可用时，会调用用户提供的回调函数。回调函数接收一个float32数组，表示音频采样点，范围在[-1.0, 1.0]之间。

### 线程安全

库内部使用互斥锁确保线程安全。用户可以在多线程环境中安全使用该库。

## 构建指南

### Windows

使用MinGW-w64构建：

```bash
cd c/windows
mingw32-make
```

构建Go绑定：

```bash
cd bindings/go
mingw32-make
```

## 常见问题

### 没有检测到音频

- 确保应用程序正在播放音频
- 检查系统音量设置
- 尝试捕获系统音频而不是特定应用程序

### 回调函数未被调用

- 确保正确设置了回调函数
- 检查是否成功调用了Start()方法
- 查看日志输出以获取更多信息

## 许可证

本项目采用MIT许可证。详见[LICENSE](./LICENSE)文件。

## 贡献

欢迎贡献代码、报告问题或提出改进建议。请通过GitHub Issues或Pull Requests参与项目开发。 