package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

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

	// 获取音频格式
	format, err := capture.GetFormat()
	if err != nil {
		fmt.Printf("获取音频格式失败: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("音频格式: 采样率=%d Hz, 通道数=%d, 位深度=%d bit\n",
		format.SampleRate, format.Channels, format.BitsPerSample)

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

	// 选择要捕获的应用
	fmt.Print("\n请输入要捕获的应用PID: ")
	var pid uint32
	fmt.Scanf("%d", &pid)

	if _, ok := apps[pid]; !ok {
		fmt.Println("无效的PID")
		os.Exit(1)
	}

	// 创建输出目录
	outputDir := "recordings"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		fmt.Printf("创建输出目录失败: %v\n", err)
		os.Exit(1)
	}

	// 创建输出文件名
	timestamp := time.Now().Format("20060102_150405")
	appName := filepath.Base(apps[pid])
	outputFile := filepath.Join(outputDir, fmt.Sprintf("%s_%s.wav", appName, timestamp))

	// 创建 WAV 文件写入器
	wavWriter, err := audio.NewWavWriter(outputFile, int(format.SampleRate), int(format.Channels), int(format.BitsPerSample))
	if err != nil {
		fmt.Printf("创建 WAV 文件失败: %v\n", err)
		os.Exit(1)
	}
	defer wavWriter.Close()

	// 创建音频数据通道和控制通道
	audioChan := make(chan []float32, 1000) // 增大缓冲区
	stopChan := make(chan struct{})
	var wg sync.WaitGroup
	wg.Add(1)

	// 启动一个 goroutine 来处理音频数据
	go func() {
		defer wg.Done()

		var sampleCount int
		startTime := time.Now()

		for {
			select {
			case data, ok := <-audioChan:
				if !ok {
					// 通道已关闭，退出循环
					return
				}

				// 写入 WAV 文件
				if err := wavWriter.WriteFloat32(data); err != nil {
					fmt.Printf("\n写入 WAV 文件失败: %v\n", err)
					continue
				}

				sampleCount += len(data)
				elapsed := time.Since(startTime)

				// 显示进度
				fmt.Printf("\r已录制 %.1f 秒 (%d 个采样点)",
					elapsed.Seconds(), sampleCount)

			case <-stopChan:
				// 收到停止信号，但继续处理通道中的剩余数据
				fmt.Println("\n正在完成录制...")

				// 排空通道中的所有数据
				for data := range audioChan {
					if err := wavWriter.WriteFloat32(data); err != nil {
						fmt.Printf("\n写入 WAV 文件失败: %v\n", err)
					}
					sampleCount += len(data)
				}

				// 确保 WAV 文件正确关闭
				if err := wavWriter.Close(); err != nil {
					fmt.Printf("\n关闭 WAV 文件失败: %v\n", err)
				}

				fmt.Printf("\n\n录音已完成，文件已保存到: %s\n", outputFile)
				return
			}
		}
	}()

	// 设置音频回调
	capture.SetCallback(func(data []float32) {
		// 复制数据并发送到通道
		dataCopy := make([]float32, len(data))
		copy(dataCopy, data)

		select {
		case audioChan <- dataCopy:
			// 数据已发送
		default:
			// 通道已满，丢弃数据
			fmt.Print(".")
		}
	})

	// 开始捕获指定应用的音频
	if err := capture.StartCapturingProcess(pid); err != nil {
		fmt.Printf("\n开始捕获失败: %v\n", err)
		close(audioChan)
		wg.Wait()
		os.Exit(1)
	}

	fmt.Printf("\n开始捕获 [%d] %s 的音频，将保存到 %s\n", pid, apps[pid], outputFile)
	fmt.Println("录制将在 30 秒后自动停止...")

	// 等待 30 秒
	time.Sleep(30 * time.Second)

	// 停止录音
	capture.Stop()

	// 发送停止信号并关闭音频通道
	close(stopChan)
	close(audioChan)

	// 等待处理完成
	wg.Wait()
}
