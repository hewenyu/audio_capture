package audio

// AudioFormat represents the audio format configuration
type AudioFormat struct {
	SampleRate    uint32
	Channels      uint32
	BitsPerSample uint32
}

// AudioAppInfo represents information about an audio application
type AudioAppInfo struct {
	PID  uint32
	Name string
}

// AudioCallback is the function type for audio data callbacks
type AudioCallback func([]float32)
