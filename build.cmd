@echo off
setlocal enabledelayedexpansion

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 检查是否安装了Go
where go >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Go is not installed or not in PATH
    exit /b 1
)

:: 设置MSYS2环境变量
set MSYS2_PATH=C:\msys64
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
if not exist "api\binaries\windows" mkdir api\binaries\windows

:: 检查源文件是否存在
if not exist "c\windows\wasapi_capture.cpp" (
    echo Error: Source file c\windows\wasapi_capture.cpp not found
    echo Current directory: %CD%
    exit /b 1
)

:: 编译C++代码
echo Building C++ code...
%CXX% -c -o "%SCRIPT_DIR%build/wasapi_capture.o" "%SCRIPT_DIR%c/windows/wasapi_capture.cpp" ^
    -I"%SCRIPT_DIR%" ^
    -I"%MSYS2_UCRT64_PATH%/include" ^
    -std=c++11 ^
    -DWIN32_LEAN_AND_MEAN ^
    -DINITGUID ^
    -mwindows -municode

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to compile C++ code
    exit /b 1
)

:: 创建动态库
echo Creating dynamic library...
%CXX% -shared -static -o "%SCRIPT_DIR%build/wasapi_capture.dll" "%SCRIPT_DIR%build/wasapi_capture.o" ^
    -Wl,--out-implib,"%SCRIPT_DIR%build/libwasapi_capture.a" ^
    -lole32 -loleaut32 -lwinmm -luuid -lstdc++ -ladvapi32

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to create dynamic library
    exit /b 1
)

:: 复制动态库到 binaries 目录
echo Copying dynamic library to binaries directory...
copy /Y "%SCRIPT_DIR%build\wasapi_capture.dll" "%SCRIPT_DIR%api\binaries\windows\"

if %ERRORLEVEL% neq 0 (
    echo Error: Failed to copy dynamic library
    exit /b 1
)

:: 编译Go代码
echo Building Go code...
go build -o "%SCRIPT_DIR%build/audio_capture.exe" ./examples/main.go
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to build Go code
    exit /b 1
)

echo Build completed successfully!
echo Output files are in the 'build' and 'api/binaries' directories

endlocal 