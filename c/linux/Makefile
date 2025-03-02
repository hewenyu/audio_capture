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

# Default target
all: $(BUILD_DIR)/$(TARGET)

# Build the shared library
$(BUILD_DIR)/$(TARGET): $(OBJS)
	@echo "Building $(TARGET)"
	@$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "Done building $(TARGET)"

# Compile source files
%.o: %.c
	@echo "Compiling $<"
	@$(CC) $(CFLAGS) -I$(INCLUDE_DIR) -c $< -o $@

# Clean build artifacts
clean:
	@echo "Cleaning Linux build artifacts"
	@rm -f $(OBJS)
	@rm -f $(BUILD_DIR)/$(TARGET)

.PHONY: all clean 