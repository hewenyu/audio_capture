cmake_minimum_required(VERSION 3.12)
project(audio_capture VERSION 0.1.0)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 选项
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)

# 添加子目录
add_subdirectory(c/windows)

# Python 绑定
if(BUILD_PYTHON_BINDINGS)
    add_subdirectory(bindings/python)
endif() 