# Compiler settings
CC := gcc
CFLAGS := -Wall -Wextra -O2 -fPIC -shared
LDFLAGS := -lpulse -lpulse-simple

# Directories
BUILD_DIR := ../../build/linux
INCLUDE_DIR := .

# Source files
SRCS := pulse_capture.c
OBJS := $(SRCS:.c=.o)
TARGET := libpulse_capture.so

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
all: $(BUILD_DIR)/$(TARGET)

# Build the shared library
$(BUILD_DIR)/$(TARGET): $(OBJS)
	@echo "Building $(TARGET)"
	@$(MKDIR) $(BUILD_DIR)
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "Done building $(TARGET)"

# Compile source files
%.o: %.c
	@echo "Compiling $<"
	@$(CC) $(CFLAGS) -I$(INCLUDE_DIR) -c $< -o $@

# Clean build artifacts
clean:
	@echo "Cleaning Linux build artifacts"
	@$(RM) $(OBJS)
	@$(RM) $(BUILD_DIR)/$(TARGET)

.PHONY: all clean 