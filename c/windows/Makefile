# 使用 CMake 构建 Windows 平台上的 C 库

# 设置 CMake 生成器
CMAKE_GENERATOR := "MinGW Makefiles"

# 设置 CMake 生成器
CMAKE_BUILD_TYPE := "Release"

# 设置 CMake 生成器
CMAKE_INSTALL_PREFIX := "install"

# 设置 CMake 生成器
CMAKE_CXX_COMPILER := "g++"

# 设置 CMake 生成器
CMAKE_C_COMPILER := "gcc"

# build 目录
BUILD_DIR := build


# 开始构建
all: mkdir build
	cd $(BUILD_DIR) && cmake .. -G $(CMAKE_GENERATOR) -DCMAKE_BUILD_TYPE=$(CMAKE_BUILD_TYPE) -DCMAKE_INSTALL_PREFIX=$(CMAKE_INSTALL_PREFIX) -DCMAKE_CXX_COMPILER=$(CMAKE_CXX_COMPILER) -DCMAKE_C_COMPILER=$(CMAKE_C_COMPILER)
	cd $(BUILD_DIR) && cmake --build . --config $(CMAKE_BUILD_TYPE) --target install


mkdir:
	mkdir $(BUILD_DIR)

build: mkdir
	@echo "Building C libraries for $(PLATFORM)"
	cd $(BUILD_DIR) && cmake .. -G $(CMAKE_GENERATOR) -DCMAKE_BUILD_TYPE=$(CMAKE_BUILD_TYPE) -DCMAKE_INSTALL_PREFIX=$(CMAKE_INSTALL_PREFIX) -DCMAKE_CXX_COMPILER=$(CMAKE_CXX_COMPILER) -DCMAKE_C_COMPILER=$(CMAKE_C_COMPILER)
	cd $(BUILD_DIR) && cmake --build . --config $(CMAKE_BUILD_TYPE)



clean:
	@if exist "$(BUILD_DIR)" rmdir /s /q $(BUILD_DIR)


install:
	cd $(BUILD_DIR) && cmake --build . --config $(CMAKE_BUILD_TYPE) --target install
