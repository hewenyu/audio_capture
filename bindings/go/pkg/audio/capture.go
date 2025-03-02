package audio

// Capture represents the audio capture interface
type Capture interface {
	// Initialize initializes the audio capture system
	Initialize() error

	// Start begins the audio capture
	Start() error

	// Stop stops the audio capture
	Stop()

	// GetFormat returns the current audio format
	GetFormat() (*AudioFormat, error)

	// SetCallback sets the callback function for audio data
	SetCallback(callback AudioCallback)

	// ListApplications returns a map of PIDs to application names that are playing audio
	ListApplications() (map[uint32]string, error)

	// StartCapturingProcess starts capturing audio from a specific process
	StartCapturingProcess(pid uint32) error

	// Close cleans up resources
	Close()
}

// New creates a new platform-specific audio capture instance
func New() Capture {
	return newPlatformCapture()
}
