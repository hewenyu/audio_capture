cmake_minimum_required(VERSION 3.10)
project(audio_capture_c_interface)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置静态链接
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libgcc -static-libstdc++ -static")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -static-libgcc -static-libstdc++ -static")

# 设置 wasapi_capture 库路径
set(WASAPI_CAPTURE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../c/windows")
set(WASAPI_CAPTURE_BUILD_DIR "${WASAPI_CAPTURE_DIR}/build")
set(WASAPI_CAPTURE_LIB "${WASAPI_CAPTURE_BUILD_DIR}/libwasapi_capture.a")

# 检查库是否存在
if(NOT EXISTS "${WASAPI_CAPTURE_LIB}")
    message(FATAL_ERROR "Static library not found at ${WASAPI_CAPTURE_LIB}. Please build the C++ library first using CMake.")
endif()

# 添加编译选项
add_definitions(
    -DWASAPI_STATIC_LIB
    -DWIN32_LEAN_AND_MEAN
    -DUNICODE
    -D_UNICODE
    -DCOBJMACROS
    -DNOMINMAX
    -D_WIN32_WINNT=0x0A00
    -DWINVER=0x0A00
)

# 创建动态库
add_library(audio_capture_c SHARED
    c_interface.cpp
)

# 设置输出名称
set_target_properties(audio_capture_c PROPERTIES
    OUTPUT_NAME "audio_capture_c"
    PREFIX ""
    LINK_FLAGS "-static-libgcc -static-libstdc++ -static"
)

# 设置包含目录
target_include_directories(audio_capture_c PRIVATE
    ${WASAPI_CAPTURE_DIR}
)

# 链接库
target_link_libraries(audio_capture_c PRIVATE
    ${WASAPI_CAPTURE_LIB}
    ole32
    oleaut32
    winmm
    uuid
)

# 安装规则 - 修改为安装动态库
install(TARGETS audio_capture_c
    RUNTIME DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}"
) 