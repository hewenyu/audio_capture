package utils

import (
	"encoding/binary"
	"fmt"
	"os"
)

type WavWriter struct {
	file       *os.File
	sampleRate int
	channels   int
	bitsDepth  int
	dataSize   int
	headerSize int
}

func NewWavWriter(filename string, sampleRate, channels, bitsDepth int) (*WavWriter, error) {
	file, err := os.Create(filename)
	if err != nil {
		return nil, err
	}

	w := &WavWriter{
		file:       file,
		sampleRate: sampleRate,
		channels:   channels,
		bitsDepth:  bitsDepth,
		headerSize: 44,
	}

	// 写入WAV头部，先用0填充
	header := make([]byte, w.headerSize)
	_, err = file.Write(header)
	return w, err
}

func (w *WavWriter) WriteFloat32(samples []float32) error {
	// 根据位深度选择转换方法
	var pcmData []byte
	switch w.bitsDepth {
	case 16:
		pcmData = make([]byte, len(samples)*2)
		for i, sample := range samples {
			value := int16(sample * 32767)
			binary.LittleEndian.PutUint16(pcmData[i*2:], uint16(value))
		}
	case 24:
		pcmData = make([]byte, len(samples)*3)
		for i, sample := range samples {
			value := int32(sample * 8388607)
			pcmData[i*3] = byte(value)
			pcmData[i*3+1] = byte(value >> 8)
			pcmData[i*3+2] = byte(value >> 16)
		}
	case 32:
		pcmData = make([]byte, len(samples)*4)
		for i, sample := range samples {
			value := int32(sample * 2147483647)
			binary.LittleEndian.PutUint32(pcmData[i*4:], uint32(value))
		}
	default:
		return fmt.Errorf("unsupported bits depth: %d", w.bitsDepth)
	}

	_, err := w.file.Write(pcmData)
	if err != nil {
		return err
	}
	w.dataSize += len(pcmData)
	return nil
}

func (w *WavWriter) Close() error {
	if w.file == nil {
		return nil
	}

	// 写入WAV文件头
	w.file.Seek(0, 0)

	// RIFF header
	w.writeString("RIFF")
	w.writeUint32(uint32(w.dataSize + 36)) // File size - 8
	w.writeString("WAVE")

	// Format chunk
	w.writeString("fmt ")
	w.writeUint32(16) // Chunk size
	w.writeUint16(1)  // Audio format (PCM)
	w.writeUint16(uint16(w.channels))
	w.writeUint32(uint32(w.sampleRate))
	w.writeUint32(uint32(w.sampleRate * w.channels * w.bitsDepth / 8)) // Byte rate
	w.writeUint16(uint16(w.channels * w.bitsDepth / 8))                // Block align
	w.writeUint16(uint16(w.bitsDepth))                                 // Bits per sample

	// Data chunk
	w.writeString("data")
	w.writeUint32(uint32(w.dataSize))

	return w.file.Close()
}

func (w *WavWriter) writeString(s string) {
	w.file.Write([]byte(s))
}

func (w *WavWriter) writeUint16(v uint16) {
	binary.LittleEndian.PutUint16([]byte{0, 0}, v)
	w.file.Write([]byte{byte(v), byte(v >> 8)})
}

func (w *WavWriter) writeUint32(v uint32) {
	binary.LittleEndian.PutUint32([]byte{0, 0, 0, 0}, v)
	w.file.Write([]byte{byte(v), byte(v >> 8), byte(v >> 16), byte(v >> 24)})
}
