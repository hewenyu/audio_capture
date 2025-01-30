# Go parameters
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
GOMOD=$(GOCMD) mod

# Output binary names
BINARY_NAME_WIN=wasapi_capture.dll
BINARY_NAME_LINUX=libpulse_capture.so
GO_BINARY=audio_capture

# Build directory
BUILD_DIR=build

# C++ compiler settings
CXX=g++
CXXFLAGS=-std=c++11 -DWIN32_LEAN_AND_MEAN -DINITGUID
LDFLAGS_WIN=-shared -lole32 -loleaut32 -lwinmm -luuid -ladvapi32 -lstdc++
LDFLAGS_LINUX=-shared -lpulse -lpulse-simple

# Detect OS
ifeq ($(OS),Windows_NT)
	PLATFORM=windows
	BINARY_NAME=$(BINARY_NAME_WIN)
	CXXFLAGS+=-mwindows -municode
	LDFLAGS=$(LDFLAGS_WIN)
else
	PLATFORM=linux
	BINARY_NAME=$(BINARY_NAME_LINUX)
	LDFLAGS=$(LDFLAGS_LINUX)
endif

.PHONY: all build clean test deps windows linux install uninstall

# Default target
all: deps build

# Build target
build: $(BUILD_DIR)/$(BINARY_NAME)

# Windows specific build
windows: PLATFORM=windows
windows: BINARY_NAME=$(BINARY_NAME_WIN)
windows: LDFLAGS=$(LDFLAGS_WIN)
windows: build

# Linux specific build
linux: PLATFORM=linux
linux: BINARY_NAME=$(BINARY_NAME_LINUX)
linux: LDFLAGS=$(LDFLAGS_LINUX)
linux: build

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Build the C++ library
$(BUILD_DIR)/$(BINARY_NAME): $(BUILD_DIR)
ifeq ($(PLATFORM),windows)
	$(CXX) $(CXXFLAGS) -c -o $(BUILD_DIR)/wasapi_capture.o c/windows/wasapi_capture.cpp
	$(CXX) -shared -o $(BUILD_DIR)/$(BINARY_NAME) $(BUILD_DIR)/wasapi_capture.o $(LDFLAGS)
else
	$(CXX) $(CXXFLAGS) -c -o $(BUILD_DIR)/pulse_capture.o c/linux/pulse_capture.c
	$(CXX) -shared -o $(BUILD_DIR)/$(BINARY_NAME) $(BUILD_DIR)/pulse_capture.o $(LDFLAGS)
endif

# Build Go example
example: build
	$(GOBUILD) -o $(BUILD_DIR)/$(GO_BINARY) ./examples/main.go

# Clean build files
clean:
	$(GOCLEAN)
	rm -rf $(BUILD_DIR)

# Run tests
test:
	$(GOTEST) -v ./...

# Get dependencies
deps:
	$(GOMOD) download
	$(GOMOD) tidy

# Install the library and binary
install: build
ifeq ($(PLATFORM),windows)
	cp $(BUILD_DIR)/$(BINARY_NAME) $(GOPATH)/bin/
else
	sudo cp $(BUILD_DIR)/$(BINARY_NAME) /usr/lib/
	sudo ldconfig
endif

# Uninstall the library and binary
uninstall:
ifeq ($(PLATFORM),windows)
	rm -f $(GOPATH)/bin/$(BINARY_NAME)
else
	sudo rm -f /usr/lib/$(BINARY_NAME)
	sudo ldconfig
endif

# Help target
help:
	@echo "Available targets:"
	@echo "  all        - Download dependencies and build the library (default)"
	@echo "  build      - Build the library for current platform"
	@echo "  windows    - Build specifically for Windows"
	@echo "  linux      - Build specifically for Linux"
	@echo "  example    - Build the example program"
	@echo "  clean      - Remove build artifacts"
	@echo "  test       - Run tests"
	@echo "  deps       - Download and update dependencies"
	@echo "  install    - Install the library to system"
	@echo "  uninstall  - Remove the library from system"
	@echo "  help       - Show this help message" 