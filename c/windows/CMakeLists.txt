cmake_minimum_required(VERSION 3.10)
project(wasapi_capture)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)



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

# 创建静态库
add_library(wasapi_capture STATIC wasapi_capture.cpp)

# 设置包含目录
target_include_directories(wasapi_capture PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# 链接 Windows 库
target_link_libraries(wasapi_capture PRIVATE 
    ole32      # COM 支持
    oleaut32   # COM 自动化
    winmm      # Windows 多媒体
    ksuser     # Kernel Streaming
    avrt       # Audio/Video Runtime
    uuid       # GUID 支持
)

# 安装规则
install(TARGETS wasapi_capture
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES wasapi_capture.h
    DESTINATION include
) 