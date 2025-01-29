@echo off
setlocal enabledelayedexpansion

:: 检查是否安装了Go
where go >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Go is not installed or not in PATH
    exit /b 1
)

:: 设置MSYS2环境变量
set MSYS2_PATH=D:\msys64
set MSYS2_UCRT64_PATH=%MSYS2_PATH%\ucrt64
set PATH=%MSYS2_UCRT64_PATH%\bin;%PATH%

:: 设置CGO环境变量
set CGO_ENABLED=1
set GOOS=windows
set GOARCH=amd64
set CC=%MSYS2_UCRT64_PATH%\bin\gcc.exe
set CXX=%MSYS2_UCRT64_PATH%\bin\g++.exe

:: 创建输出目录
if not exist "build" mkdir build

:: 编译C++代码
echo Building C++ code...
%CXX% -c -o build/wasapi_capture.o c/windows/wasapi_capture.cpp ^
    -I. -std=c++11 -DWIN32_LEAN_AND_MEAN ^
    -mwindows -municode ^
    -I%MSYS2_UCRT64_PATH%/include

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to compile C++ code
    exit /b 1
)

:: 创建静态库
echo Creating static library...
ar rcs build/libwasapi_capture.a build/wasapi_capture.o
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to create static library
    exit /b 1
)

:: 编译Go代码
echo Building Go code...
go build -o build/audio_capture.exe ./examples/main.go
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to build Go code
    exit /b 1
)

echo Build completed successfully!
echo Output files are in the 'build' directory

endlocal 