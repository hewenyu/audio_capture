# Compiler settings
CC := g++
CFLAGS := -Wall -Wextra -O2 -shared -DBUILDING_DLL
LDFLAGS := -lole32 -loleaut32 -lwinmm -luuid -lstdc++
DLLTOOL := dlltool

# Directories
BUILD_DIR := ..\..\build\windows
INCLUDE_DIR := .

# Source files
SRCS := wasapi_capture.cpp
OBJS := $(SRCS:.cpp=.o)
TARGET := wasapi_capture.dll
LIB_TARGET := wasapi_capture.lib

# Commands
ifeq ($(OS),Windows_NT)
    MKDIR := mkdir
    RM := del /Q
    RMDIR := rmdir /s /q
else
    MKDIR := mkdir -p
    RM := rm -f
    RMDIR := rm -rf
endif

# Default target
all: $(BUILD_DIR)\$(TARGET) $(BUILD_DIR)\$(LIB_TARGET)

# Build the DLL
$(BUILD_DIR)\$(TARGET): wasapi_capture.o
	@echo "Building $(TARGET)"
	@if not exist "$(BUILD_DIR)" $(MKDIR) "$(BUILD_DIR)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS) -Wl,--out-implib,$(BUILD_DIR)\$(LIB_TARGET)
	@echo "Done building $(TARGET)"

# Compile source files
wasapi_capture.o: wasapi_capture.cpp wasapi_capture.h
	@echo "Compiling $<"
	@$(CC) $(CFLAGS) -I$(INCLUDE_DIR) -c $< -o $@

# Clean build artifacts
clean:
	@echo "Cleaning Windows build artifacts"
	@$(RM) $(OBJS)
	@if exist "$(BUILD_DIR)\$(TARGET)" $(RM) "$(BUILD_DIR)\$(TARGET)"
	@if exist "$(BUILD_DIR)\$(LIB_TARGET)" $(RM) "$(BUILD_DIR)\$(LIB_TARGET)"

.PHONY: all clean 