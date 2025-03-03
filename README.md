# Audio Capture

一个跨平台的音频捕获库，可以捕获系统音频或特定应用程序的音频输出。该库提供了C/C++核心实现，以及Go和Python语言绑定。

## 功能特性

- **跨平台支持**：
  - Windows: 使用WASAPI (Windows Audio Session API)
  - Linux: 使用PulseAudio (计划中)
  - macOS: 使用CoreAudio (计划中)
- **多语言绑定**：
  - [Go语言绑定](./bindings/go/)
  - [Python语言绑定](./bindings/python/)
- **应用程序级别捕获**：可以选择捕获特定应用程序的音频输出
- **高性能**：使用底层音频API，低延迟，低CPU占用
- **简单易用的API**：提供简洁的接口，易于集成到各种应用中

## 系统要求

- **Windows**：Windows 10及以上版本
- **编译工具**：
  - Windows: MinGW-w64或Visual Studio
  - Go 1.21或更高版本（用于Go绑定）
  - Python 3.8或更高版本（用于Python绑定）
  - CMake 3.12或更高版本（用于Python绑定）

## 安装指南

### Python模块安装

#### 从GitHub Releases安装

最简单的方法是从GitHub Releases页面下载预编译的wheel文件：

1. 访问 [GitHub Releases](https://github.com/hewenyu/audio_capture/releases) 页面
2. 下载适合你的Python版本的wheel文件
3. 使用pip安装下载的wheel文件：

```bash
pip install audio_capture-0.1.0-cp39-cp39-win_amd64.whl
```

#### 从源代码构建

如果你想从源代码构建Python绑定，请按照以下步骤操作：

1. 克隆仓库：
```bash
git clone https://github.com/hewenyu/audio_capture.git
cd audio_capture
```

2. 构建并安装Python绑定：
```bash
cd bindings/python
python build_wheel.py
pip install dist/audio_capture-0.1.0-*.whl
```

详细的Python绑定文档请参阅[Python绑定README](./bindings/python/README.md)。

### Go模块安装

本库使用Go模块系统，可以直接通过`go get`命令安装：

```bash
# 安装最新版本
go get github.com/hewenyu/audio_capture/bindings/go@latest
```

#### 预编译二进制文件

为了简化安装过程，我们提供了预编译的二进制文件，包含在Go模块中：

- Windows (x64): 包含WASAPI捕获库的预编译二进制文件
- Linux (x64): 包含PulseAudio捕获库的预编译二进制文件（计划中）

这意味着大多数用户无需手动编译C/C++代码，可以直接使用Go模块。

#### 手动编译（可选）

如果预编译的二进制文件不适合你的环境，或者你想自定义编译选项，可以手动编译：

1. 克隆仓库：
```bash
git clone https://github.com/hewenyu/audio_capture.git
cd audio_capture
```

2. 编译C/C++库：
```bash
# Windows
cd c/windows
mingw32-make
```

3. 编译Go绑定：
```bash
cd ../../bindings/go
mingw32-make
```

### 在项目中使用

#### Python

```python
import audio_capture
import numpy as np
import time

# 定义音频回调函数
def audio_callback(buffer, user_data):
    # buffer是一个包含音频数据的NumPy数组
    if len(buffer) > 0:
        rms = np.sqrt(np.mean(np.square(buffer)))
        print(f"音频数据: RMS={rms:.4f}, 样本数={len(buffer)}")

# 初始化音频捕获
if audio_capture.init(audio_callback):
    # 开始捕获系统音频
    if audio_capture.start():
        print("开始捕获音频...")
        
        # 运行10秒
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("用户中断")
        
        # 停止捕获
        audio_capture.stop()
    
    # 清理资源
    audio_capture.cleanup()
```

#### Go

在你的`go.mod`文件中添加依赖：

```
require github.com/hewenyu/audio_capture/bindings/go v0.1.0
```

或者使用`go mod tidy`自动添加依赖。

## 快速开始

### 使用Python绑定

详细的Python绑定使用指南请参阅[Python绑定README](./bindings/python/README.md)。

### 使用Go绑定

1. **创建一个新项目**

```bash
mkdir my_audio_app
cd my_audio_app
go mod init my_audio_app
```

2. **添加依赖**

```bash
go get github.com/hewenyu/audio_capture/bindings/go
```

3. **基本用法示例**

创建`main.go`文件：

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

4. **运行程序**

```bash
go run main.go
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

### 完整示例应用

项目包含完整的示例应用，可以捕获特定应用程序的音频并保存为WAV文件：

- **Go示例**：`bindings/go/examples/app_capture`
- **Python示例**：`bindings/python/examples/capture_example.py`

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
│   └── python/             # Python语言绑定
│       ├── audio_capture/  # Python模块
│       └── examples/       # 示例应用
└── tests/                  # 测试代码
```

## 自动构建

本项目使用GitHub Actions自动构建：

- **Python绑定**：自动构建Windows平台的Python wheel包，支持Python 3.8-3.11
- **Go绑定**：自动构建Windows平台的Go模块

每当发布新版本（推送版本标签如`v0.1.0`）时，会自动构建并发布到GitHub Releases页面。

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

## 常见问题

### 安装问题

#### CGO编译错误

如果遇到CGO编译错误，请确保：

1. 已安装MinGW-w64（Windows）或GCC（Linux）
2. 环境变量中包含编译器路径
3. 使用正确的构建标签（如果需要）

#### 找不到预编译库

如果无法找到预编译的库文件：

1. 确保使用的是最新版本的模块
2. 尝试手动编译（见上文"手动编译"部分）
3. 检查是否有与你的操作系统/架构匹配的预编译库

### 运行问题

#### 没有检测到音频

- 确保应用程序正在播放音频
- 检查系统音量设置
- 尝试捕获系统音频而不是特定应用程序

#### 回调函数未被调用

- 确保正确设置了回调函数
- 检查是否成功调用了Start()方法
- 查看日志输出以获取更多信息

#### 权限问题

在某些系统上，可能需要管理员权限才能访问音频设备：

- Windows: 尝试以管理员身份运行程序
- Linux: 确保用户在audio组中

## 版本兼容性

我们遵循语义化版本控制（Semantic Versioning）：

- 主版本号（x.0.0）：不兼容的API更改
- 次版本号（0.x.0）：向后兼容的功能添加
- 修订号（0.0.x）：向后兼容的错误修复

## 许可证

本项目采用MIT许可证。详见[LICENSE](./LICENSE)文件。

## 贡献

欢迎贡献代码、报告问题或提出改进建议。请通过GitHub Issues或Pull Requests参与项目开发。 