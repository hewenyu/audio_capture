# Audio Capture for Go

这是 [audio_capture](https://github.com/hewenyu/audio_capture) 的 Go 语言绑定，提供了简单易用的 Go API 来捕获系统音频或特定应用程序的音频输出。

## 特性

- 跨平台支持：
  - Windows: 使用 WASAPI (Windows Audio Session API)
  - Linux: 使用 PulseAudio (计划中)
- 高性能：使用 CGO 直接调用底层音频 API
- 支持捕获特定应用程序的音频
- **开箱即用**：包含预编译的二进制文件，无需手动编译C/C++代码

## 安装

### 使用Go模块（推荐）

```bash
go get github.com/hewenyu/audio_capture/bindings/go@latest
```

### 手动安装

1. 克隆仓库：
```bash
git clone https://github.com/hewenyu/audio_capture.git
cd audio_capture
```

2. 编译C/C++库和Go绑定：
```bash
# Windows
cd c/windows
mingw32-make
cd ../../bindings/go
mingw32-make
```

## 发布指南（项目维护者）

为了确保用户可以通过`go get`命令开箱即用，我们需要在Go模块中包含预编译的二进制文件。

### 1. 准备预编译二进制文件

为每个支持的平台编译静态库：

#### Windows (x64)

```bash
cd c/windows
mingw32-make clean
mingw32-make
```

编译完成后，将生成的`libwasapi_capture.a`文件复制到`bindings/go/pkg/audio/lib/windows_amd64/`目录。

#### Linux (x64)

```bash
cd c/linux
make clean
make
```

编译完成后，将生成的`libpulseaudio_capture.a`文件复制到`bindings/go/pkg/audio/lib/linux_amd64/`目录。

### 2. 更新Go绑定代码

确保Go绑定代码能够正确加载预编译的二进制文件。在`bindings/go/pkg/audio/capture_windows.go`和其他平台特定文件中，使用类似以下的CGO指令：

```go
/*
#cgo CFLAGS: -I${SRCDIR}
#cgo windows,amd64 LDFLAGS: -L${SRCDIR}/lib/windows_amd64 -l:libwasapi_capture.a -static -lole32 -loleaut32 -lwinmm -luuid -lstdc++
#cgo linux,amd64 LDFLAGS: -L${SRCDIR}/lib/linux_amd64 -l:libpulseaudio_capture.a -static -lpulse -lpulse-simple
*/
import "C"
```

### 3. 目录结构

确保以下目录结构存在：

```
bindings/go/
├── pkg/
│   └── audio/
│       ├── lib/
│       │   ├── windows_amd64/
│       │   │   └── libwasapi_capture.a
│       │   └── linux_amd64/
│       │       └── libpulseaudio_capture.a
│       ├── capture.go
│       ├── capture_windows.go
│       ├── capture_linux.go
│       └── wav_writer.go
├── examples/
│   └── app_capture/
│       └── main.go
├── go.mod
├── go.sum
└── README.md
```

### 4. 发布新版本

1. 更新版本号：
   - 在`go.mod`文件中更新版本号
   - 遵循语义化版本控制（Semantic Versioning）

2. 提交更改并创建新的Git标签：
```bash
git add .
git commit -m "Release vX.Y.Z with precompiled binaries"
git tag vX.Y.Z
git push origin master --tags
```

3. 验证发布：
```bash
# 在一个新目录中测试安装
mkdir test_install
cd test_install
go mod init test
go get github.com/hewenyu/audio_capture/bindings/go@vX.Y.Z
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

## 常见问题

### 编译错误

如果遇到CGO编译错误，请确保：

1. 已安装MinGW-w64（Windows）或GCC（Linux）
2. 环境变量中包含编译器路径
3. 使用正确的构建标签（如果需要）

### 找不到预编译库

如果Go无法找到预编译的库文件：

1. 确保使用的是最新版本的模块
2. 尝试手动编译（见上文"手动安装"部分）
3. 检查是否有与你的操作系统/架构匹配的预编译库

## 系统要求

- Go 1.21 或更高版本
- Windows 7+ 或支持 PulseAudio 的 Linux 系统
- 如果需要手动编译：GCC 编译器（用于 CGO）

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../../LICENSE) 文件。 