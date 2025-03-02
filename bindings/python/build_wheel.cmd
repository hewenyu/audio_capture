@echo off
setlocal enabledelayedexpansion

:: 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 检查是否安装了Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

:: 检查是否安装了必要的包
python -m pip install --upgrade pip wheel setuptools build
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install build dependencies
    exit /b 1
)

:: 复制动态库
if not exist "audio_capture\binaries\windows" mkdir audio_capture\binaries\windows
copy /Y "..\api\binaries\windows\wasapi_capture.dll" "audio_capture\binaries\windows\"
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to copy DLL file
    exit /b 1
)

:: 构建wheel
python -m build --wheel
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to build wheel
    exit /b 1
)

echo Build completed successfully!
echo Wheel file is in the 'dist' directory

endlocal 