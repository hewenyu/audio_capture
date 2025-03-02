# Platform detection
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
    LIB_EXT := .dll
    LIB_PREFIX :=
    TARGET := wasapi_capture
    MKDIR := mkdir
    RM := del /Q
    RMDIR := rmdir /s /q
    EXE := .exe
else
    PLATFORM := linux
    LIB_EXT := .so
    LIB_PREFIX := lib
    TARGET := pulse_capture
    MKDIR := mkdir -p
    RM := rm -f
    RMDIR := rm -rf
    EXE :=
endif

BUILD_DIR := build
INCLUDE_PATH := $(abspath ../../c/windows):$(abspath ../../c/linux)
LIBRARY_PATH := $(abspath ../../build/windows):$(abspath ../../build/linux)

all: clean examples

# Build examples
examples: mkdir modtidy
	@echo "Building examples"
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go build -o ${BUILD_DIR}/basic_capture$(EXE) ./examples/basic_capture
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go build -o ${BUILD_DIR}/app_capture$(EXE) ./examples/app_capture

# Run tests
test: modtidy
	@echo "Running tests"
	@C_INCLUDE_PATH=${INCLUDE_PATH} LIBRARY_PATH=${LIBRARY_PATH} go test -v ./...

# Create build directory
mkdir:
	@echo "Creating build directory"
ifeq ($(PLATFORM),windows)
	@if not exist "$(BUILD_DIR)" $(MKDIR) "$(BUILD_DIR)"
else
	@$(MKDIR) $(BUILD_DIR)
endif

# Update Go modules
modtidy:
	@echo "Updating Go modules"
	@go mod tidy

# Clean build artifacts
clean:
	@echo "Cleaning"
ifeq ($(PLATFORM),windows)
	@if exist "$(BUILD_DIR)" $(RM) "$(BUILD_DIR)"
else
	@$(RM) $(BUILD_DIR)
endif
	@go clean

.PHONY: all examples test mkdir modtidy clean 