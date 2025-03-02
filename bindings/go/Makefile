ifndef UNAME_S
UNAME_S := $(shell uname -s)
endif

ifndef UNAME_P
UNAME_P := $(shell uname -p)
endif

ifndef UNAME_M
UNAME_M := $(shell uname -m)
endif

BUILD_DIR := build
INCLUDE_PATH := $(abspath ../../c/windows):$(abspath ../../c/linux)
LIBRARY_PATH := $(abspath ../../c/windows):$(abspath ../../c/linux)

# Windows specific settings
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
    LIB_EXT := .dll
    LIB_PREFIX :=
    TARGET := wasapi_capture
else
    PLATFORM := linux
    LIB_EXT := .so
    LIB_PREFIX := lib
    TARGET := pulse_capture
endif

all: clean audio examples

# Build the C library
audio: mkdir
	@echo "Building audio capture library for $(PLATFORM)"
ifeq ($(PLATFORM),windows)
	@${MAKE} -C ../../c/windows wasapi_capture.dll
else
	@${MAKE} -C ../../c/linux libpulse_capture.so
endif

# Build examples
examples: mkdir audio modtidy
	@echo "Building examples"
ifeq ($(PLATFORM),windows)
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go build -o ${BUILD_DIR}/basic_capture.exe ./examples/basic_capture
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go build -o ${BUILD_DIR}/app_capture.exe ./examples/app_capture
else
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go build -o ${BUILD_DIR}/basic_capture ./examples/basic_capture
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go build -o ${BUILD_DIR}/app_capture ./examples/app_capture
endif

# Run tests
test: audio modtidy
	@echo "Running tests"
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go test -v ./...

# Create build directory
mkdir:
	@echo "Creating build directory"
	@install -d ${BUILD_DIR}

# Update Go modules
modtidy:
	@echo "Updating Go modules"
	@go mod tidy

# Clean build artifacts
clean:
	@echo "Cleaning"
	@rm -rf $(BUILD_DIR)
	@go clean

.PHONY: all audio examples test mkdir modtidy clean 