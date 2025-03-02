@echo off
echo 准备发布包含预编译二进制文件的Go模块...

REM 创建目录结构
mkdir bindings\go\pkg\audio\lib\windows_amd64 2>nul

REM 编译C/C++库
echo 编译WASAPI捕获库...
cd c\windows
mingw32-make clean
mingw32-make
if %ERRORLEVEL% neq 0 (
    echo 编译失败！
    exit /b %ERRORLEVEL%
)

REM 复制预编译的二进制文件
echo 复制预编译的二进制文件...
copy libwasapi_capture.a ..\..\bindings\go\pkg\audio\lib\windows_amd64\
if %ERRORLEVEL% neq 0 (
    echo 复制失败！
    exit /b %ERRORLEVEL%
)

REM 返回项目根目录
cd ..\..

REM 编译Go绑定
echo 编译Go绑定...
cd bindings\go
mingw32-make
if %ERRORLEVEL% neq 0 (
    echo 编译失败！
    exit /b %ERRORLEVEL%
)

REM 提示下一步操作
echo.
echo 预编译二进制文件已准备就绪！
echo.
echo 接下来的步骤：
echo 1. 更新go.mod文件中的版本号
echo 2. 提交更改：git add . ^&^& git commit -m "Release vX.Y.Z with precompiled binaries"
echo 3. 创建标签：git tag vX.Y.Z
echo 4. 推送更改：git push origin master --tags
echo.
echo 完成！

cd ..\.. 