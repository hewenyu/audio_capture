# Compiler settings
CC := gcc
CFLAGS := -Wall -Wextra -O2 -shared -DBUILDING_DLL
LDFLAGS := -lole32 -loleaut32 -lwinmm -luuid

# Directories
BUILD_DIR := ../../build/windows
INCLUDE_DIR := .

# Source files
SRCS := wasapi_capture.c
OBJS := $(SRCS:.c=.o)
TARGET := wasapi_capture.dll

# Default target
all: $(BUILD_DIR)/$(TARGET)

# Build the DLL
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
	@echo "Cleaning Windows build artifacts"
	@rm -f $(OBJS)
	@rm -f $(BUILD_DIR)/$(TARGET)

.PHONY: all clean 