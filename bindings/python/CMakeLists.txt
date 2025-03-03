cmake_minimum_required(VERSION 3.12)
project(audio_capture_python)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Python configuration

# 使用系统环境中的Python
set(PYTHON_EXECUTABLE ${Python_EXECUTABLE})

# 允许用户通过CMake参数覆盖Python路径
if(DEFINED CUSTOM_PYTHON_EXECUTABLE AND EXISTS "${CUSTOM_PYTHON_EXECUTABLE}")
    set(PYTHON_EXECUTABLE "${CUSTOM_PYTHON_EXECUTABLE}")
    message(STATUS "Using custom Python executable: ${PYTHON_EXECUTABLE}")
    
    # 从自定义路径派生其他Python路径
    get_filename_component(PYTHON_ROOT_DIR "${PYTHON_EXECUTABLE}" DIRECTORY)
    
    # 检测Python版本以确定正确的库名
    execute_process(
        COMMAND "${PYTHON_EXECUTABLE}" -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"
        OUTPUT_VARIABLE PYTHON_VERSION_NO_DOT
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    
    set(PYTHON_INCLUDE_DIR "${PYTHON_ROOT_DIR}/include")
    set(PYTHON_LIBRARY "${PYTHON_ROOT_DIR}/libs/python${PYTHON_VERSION_NO_DOT}.lib")
    
    # 告诉pybind11使用我们指定的Python
    set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
    set(Python_INCLUDE_DIRS "${PYTHON_INCLUDE_DIR}")
    set(Python_LIBRARIES "${PYTHON_LIBRARY}")
endif()

# Determine Python site-packages directory
execute_process(
    COMMAND "${PYTHON_EXECUTABLE}" -c "import site; print(site.getsitepackages()[0])"
    OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

# 添加 pybind11
include(FetchContent)
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG        v2.11.1
)
FetchContent_MakeAvailable(pybind11)

# 包含目录
include_directories(${CMAKE_SOURCE_DIR}/c/windows)

# 平台检测
if(WIN32)
    set(PLATFORM_DIR "windows")
    set(PLATFORM_LIB "wasapi_capture")
    add_definitions(
        -DWIN32_LEAN_AND_MEAN
        -DUNICODE
        -D_UNICODE
    )
elseif(UNIX AND NOT APPLE)
    set(PLATFORM_DIR "linux")
    set(PLATFORM_LIB "pulse_capture")
endif()

# 创建 Python 模块
pybind11_add_module(audio_capture MODULE 
    audio_capture.cpp
)

# 链接库
target_link_libraries(audio_capture PRIVATE ${PLATFORM_LIB})

# Windows 平台特定设置
if(WIN32)
    # 链接 Windows 库
    target_link_libraries(audio_capture PRIVATE 
        ole32      # COM 支持
        oleaut32   # COM 自动化
        winmm      # Windows 多媒体
        ksuser     # Kernel Streaming
        avrt       # Audio/Video Runtime
        uuid       # GUID 支持
    )
    
    # 设置运行时库为 MD (多线程 DLL)
    set_target_properties(audio_capture PROPERTIES 
        MSVC_RUNTIME_LIBRARY "MultiThreadedDLL"
    )
    
    # 禁用增量链接，避免一些 DLL 加载问题
    if(MSVC)
        set_target_properties(audio_capture PROPERTIES 
            LINK_FLAGS "/INCREMENTAL:NO"
        )
    endif()
endif()

# 安装规则
install(TARGETS audio_capture 
    LIBRARY DESTINATION "${PYTHON_SITE_PACKAGES}"
    RUNTIME DESTINATION "${PYTHON_SITE_PACKAGES}"
) 