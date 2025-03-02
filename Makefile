ifndef UNAME_S
UNAME_S := $(shell uname -s)
endif

ifndef UNAME_P
UNAME_P := $(shell uname -p)
endif

ifndef UNAME_M
UNAME_M := $(shell uname -m)
endif

# Platform detection
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

# Directories
BUILD_DIR := build
C_DIR := c
BINDINGS_DIR := bindings

# Default target
all: c-lib bindings examples

# Build C libraries
c-lib: mkdir
	@echo "Building C libraries for $(PLATFORM)"
ifeq ($(PLATFORM),windows)
	@${MAKE} -C $(C_DIR)/windows
else
	@${MAKE} -C $(C_DIR)/linux
endif

# Build language bindings
bindings: c-lib
	@echo "Building language bindings"
	@${MAKE} -C $(BINDINGS_DIR)/go

# Build examples
examples: bindings
	@echo "Building examples"
	@${MAKE} -C $(BINDINGS_DIR)/go examples

# Run tests
test: c-lib
	@echo "Running tests"
	@${MAKE} -C $(BINDINGS_DIR)/go test

# Create build directory
mkdir:
	@echo "Creating build directory"
	@install -d $(BUILD_DIR)
ifeq ($(PLATFORM),windows)
	@install -d $(BUILD_DIR)/windows
else
	@install -d $(BUILD_DIR)/linux
endif

# Clean everything
clean:
	@echo "Cleaning all build artifacts"
	@rm -rf $(BUILD_DIR)
ifeq ($(PLATFORM),windows)
	@${MAKE} -C $(C_DIR)/windows clean
else
	@${MAKE} -C $(C_DIR)/linux clean
endif
	@${MAKE} -C $(BINDINGS_DIR)/go clean

.PHONY: all c-lib bindings examples test mkdir clean 