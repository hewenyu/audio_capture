@echo off
chcp 65001 > nul
echo 准备发布包含预编译二进制文件的Go模块...

:: 创建目录结构
echo 创建目录结构...
if not exist pkg\audio\lib\windows_amd64 mkdir pkg\audio\lib\windows_amd64

:: 编译C/C++库
echo 编译WASAPI捕获库...
pushd ..\..\c\windows
mingw32-make clean
mingw32-make -C ..\..\c\windows
if errorlevel 1 (
    echo 编译失败！
    popd
    exit /b 1
)

:: 返回bindings\go
pushd ..\..\bindings\go

:: 复制预编译的二进制文件
echo 复制预编译的二进制文件...
copy /Y ..\..\build\windows\*.a pkg\audio\lib\windows_amd64\
if errorlevel 1 (
    echo 复制失败！
    popd
    exit /b 1
)

:: 编译Go绑定
echo 编译Go绑定...
pushd
mingw32-make
if errorlevel 1 (
    echo 编译失败！
    popd
    exit /b 1
)
popd

:: 提示下一步操作
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