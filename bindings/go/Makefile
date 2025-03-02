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
    # Windows specific environment variable setting
    SET_ENV := set
else
    PLATFORM := linux
    LIB_EXT := .so
    LIB_PREFIX := lib
    TARGET := pulse_capture
    MKDIR := mkdir -p
    RM := rm -f
    RMDIR := rm -rf
    EXE :=
    # Unix specific environment variable setting
    SET_ENV := export
endif

BUILD_DIR := build

ifeq ($(PLATFORM),windows)
INCLUDE_PATH := $(abspath ../../c/windows)
LIBRARY_PATH := $(abspath ../../build/windows)
else
INCLUDE_PATH := $(abspath ../../c/linux)
LIBRARY_PATH := $(abspath ../../build/linux)
endif

all: clean examples

# Build examples
examples: mkdir modtidy
	@echo "Building examples"
ifeq ($(OS),Windows_NT)
	@cmd /C "set C_INCLUDE_PATH=$(INCLUDE_PATH) && set LIBRARY_PATH=$(LIBRARY_PATH) && set CGO_LDFLAGS=-L$(LIBRARY_PATH) && go build -o $(BUILD_DIR)/basic_capture$(EXE) ./examples/basic_capture"
	@cmd /C "set C_INCLUDE_PATH=$(INCLUDE_PATH) && set LIBRARY_PATH=$(LIBRARY_PATH) && set CGO_LDFLAGS=-L$(LIBRARY_PATH) && go build -o $(BUILD_DIR)/app_capture$(EXE) ./examples/app_capture"
else
	@C_INCLUDE_PATH=$(INCLUDE_PATH) LIBRARY_PATH=$(LIBRARY_PATH) CGO_LDFLAGS="-L$(LIBRARY_PATH)" go build -o $(BUILD_DIR)/basic_capture$(EXE) ./examples/basic_capture
	@C_INCLUDE_PATH=$(INCLUDE_PATH) LIBRARY_PATH=$(LIBRARY_PATH) CGO_LDFLAGS="-L$(LIBRARY_PATH)" go build -o $(BUILD_DIR)/app_capture$(EXE) ./examples/app_capture
endif

# Run tests
test: modtidy
	@echo "Running tests"
ifeq ($(OS),Windows_NT)
	@cmd /C "set C_INCLUDE_PATH=$(INCLUDE_PATH) && set LIBRARY_PATH=$(LIBRARY_PATH) && set CGO_LDFLAGS=-L$(LIBRARY_PATH) && go test -v ./..."
else
	@C_INCLUDE_PATH=$(INCLUDE_PATH) LIBRARY_PATH=$(LIBRARY_PATH) CGO_LDFLAGS="-L$(LIBRARY_PATH)" go test -v ./...
endif

# Create build directory
mkdir:
	@echo "Creating build directory"
ifeq ($(PLATFORM),windows)
	@if not exist "$(BUILD_DIR)" mkdir "$(BUILD_DIR)" 2>NUL
	@copy ..\..\c\windows\wasapi_capture.h pkg\audio\ >NUL
else
	@$(MKDIR) $(BUILD_DIR)
	@cp ../../c/linux/pulse_capture.h pkg/audio/
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