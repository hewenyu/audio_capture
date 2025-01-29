package api

// AudioFormat 表示音频格式
type AudioFormat struct {
	SampleRate    int
	Channels      int
	BitsPerSample int
}

// AudioCallback 音频数据回调函数
type AudioCallback func([]float32)

// AudioCapture 音频捕获接口
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
}

// NewAudioCapture 创建平台相关的音频捕获实例
func NewAudioCapture() AudioCapture {
	return newPlatformAudioCapture()
}
