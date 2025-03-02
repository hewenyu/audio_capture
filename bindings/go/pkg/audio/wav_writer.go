package audio

import (
	"encoding/binary"
	"fmt"
	"os"
	"sync"
)

// WAV 文件头常量
const (
	riffChunkID    = "RIFF"
	waveFormatType = "WAVE"
	fmtChunkID     = "fmt "
	dataChunkID    = "data"
	pcmFormatCode  = 1  // PCM 格式
	headerSize     = 44 // WAV 文件头大小
)

// WavWriter 用于将音频数据写入 WAV 文件
type WavWriter struct {
	file          *os.File
	sampleRate    uint32
	channels      uint32
	bitsPerSample uint32
	dataSize      uint32
	mu            sync.Mutex
	closed        bool
	debug         bool // 是否启用调试输出
}

// NewWavWriter 创建一个新的 WAV 文件写入器
func NewWavWriter(filename string, format *AudioFormat) (*WavWriter, error) {
	file, err := os.Create(filename)
	if err != nil {
		return nil, fmt.Errorf("创建文件失败: %v", err)
	}

	writer := &WavWriter{
		file:          file,
		sampleRate:    format.SampleRate,
		channels:      format.Channels,
		bitsPerSample: format.BitsPerSample,
		dataSize:      0,
		closed:        false,
		debug:         true, // 启用调试输出
	}

	fmt.Printf("创建 WAV 文件: %s (采样率=%d Hz, 通道数=%d, 位深度=%d bit)\n",
		filename, format.SampleRate, format.Channels, format.BitsPerSample)

	// 写入 WAV 文件头
	if err := writer.writeHeader(); err != nil {
		file.Close()
		return nil, fmt.Errorf("写入 WAV 文件头失败: %v", err)
	}

	return writer, nil
}

// writeHeader 写入 WAV 文件头
func (w *WavWriter) writeHeader() error {
	// 预留文件头空间
	header := make([]byte, headerSize)

	// RIFF 块
	copy(header[0:4], riffChunkID)
	// 文件大小 (占位，稍后更新)
	binary.LittleEndian.PutUint32(header[4:8], 36) // 36 + 数据大小
	copy(header[8:12], waveFormatType)

	// fmt 块
	copy(header[12:16], fmtChunkID)
	binary.LittleEndian.PutUint32(header[16:20], 16) // fmt 块大小
	binary.LittleEndian.PutUint16(header[20:22], pcmFormatCode)
	binary.LittleEndian.PutUint16(header[22:24], uint16(w.channels))
	binary.LittleEndian.PutUint32(header[24:28], w.sampleRate)

	// 每秒字节数 = 采样率 * 通道数 * 位深度/8
	byteRate := w.sampleRate * w.channels * w.bitsPerSample / 8
	binary.LittleEndian.PutUint32(header[28:32], byteRate)

	// 块对齐 = 通道数 * 位深度/8
	blockAlign := w.channels * w.bitsPerSample / 8
	binary.LittleEndian.PutUint16(header[32:34], uint16(blockAlign))

	binary.LittleEndian.PutUint16(header[34:36], uint16(w.bitsPerSample))

	// data 块
	copy(header[36:40], dataChunkID)
	// 数据大小 (占位，稍后更新)
	binary.LittleEndian.PutUint32(header[40:44], 0)

	if w.debug {
		fmt.Printf("写入 WAV 文件头: 采样率=%d Hz, 通道数=%d, 位深度=%d bit, 每秒字节数=%d, 块对齐=%d\n",
			w.sampleRate, w.channels, w.bitsPerSample, byteRate, blockAlign)
	}

	_, err := w.file.Write(header)
	if err != nil {
		return fmt.Errorf("写入文件头失败: %v", err)
	}
	return nil
}

// WriteFloat32 将 float32 格式的音频数据写入 WAV 文件
func (w *WavWriter) WriteFloat32(data []float32) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	if w.closed {
		return fmt.Errorf("文件已关闭")
	}

	if len(data) == 0 {
		if w.debug {
			fmt.Println("警告: 尝试写入空数据")
		}
		return nil
	}

	// 将 float32 转换为 PCM 格式
	var samples []byte
	var bytesPerSample int

	if w.bitsPerSample == 16 {
		// 转换为 16 位 PCM
		bytesPerSample = 2
		samples = make([]byte, len(data)*bytesPerSample)
		for i, sample := range data {
			// 将 float32 [-1.0, 1.0] 转换为 int16 [-32768, 32767]
			// 确保值在有效范围内
			if sample > 1.0 {
				sample = 1.0
			} else if sample < -1.0 {
				sample = -1.0
			}
			pcm := int16(sample * 32767)
			binary.LittleEndian.PutUint16(samples[i*bytesPerSample:], uint16(pcm))
		}
	} else if w.bitsPerSample == 32 {
		// 转换为 32 位 PCM
		bytesPerSample = 4
		samples = make([]byte, len(data)*bytesPerSample)
		for i, sample := range data {
			// 将 float32 [-1.0, 1.0] 转换为 int32
			// 确保值在有效范围内
			if sample > 1.0 {
				sample = 1.0
			} else if sample < -1.0 {
				sample = -1.0
			}
			pcm := int32(sample * 2147483647)
			binary.LittleEndian.PutUint32(samples[i*bytesPerSample:], uint32(pcm))
		}
	} else {
		return fmt.Errorf("不支持的位深度: %d", w.bitsPerSample)
	}

	// 写入数据
	n, err := w.file.Write(samples)
	if err != nil {
		return fmt.Errorf("写入音频数据失败: %v", err)
	}

	w.dataSize += uint32(n)

	if w.debug && (w.dataSize%(w.sampleRate*uint32(bytesPerSample)) == 0) {
		// 每秒数据打印一次
		seconds := float64(w.dataSize) / float64(w.sampleRate*uint32(bytesPerSample)*w.channels)
		fmt.Printf("已写入 %.2f 秒的音频数据 (%d 字节)\n", seconds, w.dataSize)
	}

	return nil
}

// updateHeader 更新 WAV 文件头
func (w *WavWriter) updateHeader() error {
	if w.debug {
		fmt.Printf("更新 WAV 文件头: 数据大小=%d 字节\n", w.dataSize)
	}

	// 更新文件头中的数据大小
	_, err := w.file.Seek(40, 0)
	if err != nil {
		return fmt.Errorf("定位到数据大小位置失败: %v", err)
	}
	err = binary.Write(w.file, binary.LittleEndian, w.dataSize)
	if err != nil {
		return fmt.Errorf("写入数据大小失败: %v", err)
	}

	// 更新文件头中的文件大小
	_, err = w.file.Seek(4, 0)
	if err != nil {
		return fmt.Errorf("定位到文件大小位置失败: %v", err)
	}
	err = binary.Write(w.file, binary.LittleEndian, uint32(36+w.dataSize))
	if err != nil {
		return fmt.Errorf("写入文件大小失败: %v", err)
	}

	return nil
}

// GetDataSize 返回已写入的数据大小
func (w *WavWriter) GetDataSize() uint32 {
	w.mu.Lock()
	defer w.mu.Unlock()
	return w.dataSize
}

// GetDuration 返回已写入的音频时长（秒）
func (w *WavWriter) GetDuration() float64 {
	w.mu.Lock()
	defer w.mu.Unlock()

	bytesPerSample := uint32(w.bitsPerSample / 8)
	return float64(w.dataSize) / float64(w.sampleRate*bytesPerSample*w.channels)
}

// Close 关闭 WAV 文件并更新文件头
func (w *WavWriter) Close() error {
	w.mu.Lock()
	defer w.mu.Unlock()

	if w.closed || w.file == nil {
		return nil
	}

	// 标记为已关闭
	w.closed = true

	if w.debug {
		bytesPerSample := uint32(w.bitsPerSample / 8)
		seconds := float64(w.dataSize) / float64(w.sampleRate*bytesPerSample*w.channels)
		fmt.Printf("关闭 WAV 文件: 总数据大小=%d 字节, 时长=%.2f 秒\n", w.dataSize, seconds)
	}

	// 更新文件头
	if err := w.updateHeader(); err != nil {
		w.file.Close()
		return fmt.Errorf("更新文件头失败: %v", err)
	}

	// 关闭文件
	return w.file.Close()
}
