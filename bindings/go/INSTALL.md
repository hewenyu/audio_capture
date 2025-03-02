# 安装指南

本文档提供了详细的安装说明，帮助你在项目中使用audio_capture库。

## 使用Go模块安装（推荐）

### 前提条件

- Go 1.21或更高版本
- Windows 7+（目前仅支持Windows平台）

### 安装步骤

1. **在你的项目中初始化Go模块**（如果尚未初始化）：

```bash
cd your_project
go mod init your_project_name
```

2. **添加audio_capture依赖**：

```bash
go get github.com/hewenyu/audio_capture/bindings/go@latest
```

3. **更新依赖**：

```bash
go mod tidy
```

## 验证安装

创建一个简单的测试程序来验证安装是否成功：

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
		fmt.Printf("初始化失败: %v\n", err)
		return
	}
	defer capture.Close()

	fmt.Println("音频捕获初始化成功！")

	// 获取音频格式
	format, err := capture.GetFormat()
	if err != nil {
		fmt.Printf("获取音频格式失败: %v\n", err)
		return
	}

	fmt.Printf("音频格式: 采样率=%d Hz, 通道数=%d, 位深度=%d bit\n",
		format.SampleRate, format.Channels, format.BitsPerSample)

	fmt.Println("安装验证成功！")
}
```

保存为`test.go`并运行：

```bash
go run test.go
```

如果看到"安装验证成功！"的消息，说明库已正确安装。

## 常见问题

### CGO编译错误

如果遇到类似以下错误：

```
exec: "gcc": executable file not found in %PATH%
```

这表示你需要安装GCC编译器。在Windows上，推荐使用MinGW-w64：

1. 下载并安装[MinGW-w64](https://www.mingw-w64.org/downloads/)
2. 将MinGW-w64的bin目录添加到系统PATH环境变量
3. 重新打开命令提示符或PowerShell
4. 重试安装

### 找不到预编译库

如果遇到类似以下错误：

```
cannot find -l:libwasapi_capture.a
```

这可能是因为预编译库与你的系统不兼容。请尝试手动编译：

1. 克隆仓库：
```bash
git clone https://github.com/hewenyu/audio_capture.git
cd audio_capture
```

2. 编译C/C++库和Go绑定：
```bash
cd c/windows
mingw32-make
cd ../../bindings/go
mingw32-make
```

3. 在你的项目中使用本地版本：
```bash
go mod edit -replace github.com/hewenyu/audio_capture/bindings/go=../path/to/audio_capture/bindings/go
go mod tidy
```

## 更多信息

- [项目主页](https://github.com/hewenyu/audio_capture)
- [API文档](https://github.com/hewenyu/audio_capture/blob/master/bindings/go/README.md#api-文档)
- [示例应用](https://github.com/hewenyu/audio_capture/tree/master/bindings/go/examples) 