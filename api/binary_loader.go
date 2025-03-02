package api

import (
	"embed"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
)

//go:embed binaries
var binaryFiles embed.FS

// ensureLibraryLoaded 确保动态库文件存在并返回其路径
func ensureLibraryLoaded() (string, error) {
	// 获取临时目录
	tempDir := os.TempDir()

	// 根据操作系统选择正确的动态库文件
	var libName string
	switch runtime.GOOS {
	case "windows":
		libName = "wasapi_capture.dll"
	case "linux":
		libName = "libpulse_capture.so"
	case "darwin":
		return "", fmt.Errorf("mac platform is not supported")
	default:
		return "", fmt.Errorf("unsupported platform: %s", runtime.GOOS)
	}

	// 创建目标路径
	libPath := filepath.Join(tempDir, "audio_capture_"+libName)

	// 检查文件是否已存在
	if _, err := os.Stat(libPath); err == nil {
		return libPath, nil
	}

	// 从嵌入的文件系统中读取动态库
	srcPath := filepath.Join("binaries", runtime.GOOS, libName)
	data, err := binaryFiles.ReadFile(srcPath)
	if err != nil {
		return "", fmt.Errorf("failed to read embedded library: %v", err)
	}

	// 写入到临时目录
	if err := os.WriteFile(libPath, data, 0755); err != nil {
		return "", fmt.Errorf("failed to write library to temp dir: %v", err)
	}

	return libPath, nil
}
