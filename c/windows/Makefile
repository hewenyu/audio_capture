# Compiler settings
CC := g++
CFLAGS := -Wall -Wextra -O2
STATIC_CFLAGS := -Wall -Wextra -O2 -c
LDFLAGS := -lole32 -loleaut32 -lwinmm -luuid -lstdc++
DLLTOOL := dlltool
AR := ar

# Directories
BUILD_DIR := ..\..\build\windows
INCLUDE_DIR := .

# Source files
SRCS := wasapi_capture.cpp
OBJS := $(SRCS:.cpp=.o)
TARGET := wasapi_capture.dll
LIB_TARGET := wasapi_capture.lib
STATIC_LIB := libwasapi_capture.a

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
all: $(BUILD_DIR)\$(TARGET) $(BUILD_DIR)\$(LIB_TARGET) $(BUILD_DIR)\$(STATIC_LIB)

# Build the DLL
$(BUILD_DIR)\$(TARGET): wasapi_capture.o
	@echo "Building $(TARGET)"
	@if not exist "$(BUILD_DIR)" $(MKDIR) "$(BUILD_DIR)"
	@$(CC) -shared -o $@ $^ $(LDFLAGS) -Wl,--out-implib,$(BUILD_DIR)\$(LIB_TARGET)
	@echo "Done building $(TARGET)"

# Build the static library
$(BUILD_DIR)\$(STATIC_LIB): wasapi_capture_static.o
	@echo "Building $(STATIC_LIB)"
	@if not exist "$(BUILD_DIR)" $(MKDIR) "$(BUILD_DIR)"
	@$(AR) rcs $@ $^
	@echo "Done building $(STATIC_LIB)"

# Compile source files for DLL
wasapi_capture.o: wasapi_capture.cpp wasapi_capture.h
	@echo "Compiling $< for DLL"
	@$(CC) $(CFLAGS) -DBUILDING_DLL -I$(INCLUDE_DIR) -c $< -o $@

# Compile source files for static library
wasapi_capture_static.o: wasapi_capture.cpp wasapi_capture.h
	@echo "Compiling $< for static library"
	@$(CC) $(STATIC_CFLAGS) -I$(INCLUDE_DIR) $< -o $@

# Clean build artifacts
clean:
	@echo "Cleaning Windows build artifacts"
	@$(RM) $(OBJS) wasapi_capture_static.o
	@if exist "$(BUILD_DIR)\$(TARGET)" $(RM) "$(BUILD_DIR)\$(TARGET)"
	@if exist "$(BUILD_DIR)\$(LIB_TARGET)" $(RM) "$(BUILD_DIR)\$(LIB_TARGET)"
	@if exist "$(BUILD_DIR)\$(STATIC_LIB)" $(RM) "$(BUILD_DIR)\$(STATIC_LIB)"

.PHONY: all clean 