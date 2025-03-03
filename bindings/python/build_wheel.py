#!/usr/bin/env python
import os
import sys
import subprocess
import shutil
import platform

def main():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取项目根目录
    root_dir = os.path.abspath(os.path.join(script_dir, '../..'))
    
    # 创建 dist 目录
    dist_dir = os.path.join(script_dir, 'dist')
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # 创建 build 目录
    build_dir = os.path.join(root_dir, 'build')
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    # 获取 Python 可执行文件路径
    python_executable = os.environ.get('PYTHON_PATH', sys.executable)
    
    # 使用 CMake 构建
    print(f"Building with CMake using Python: {python_executable}")
    
    # 确定 CMake 生成器
    generator = "MinGW Makefiles" if platform.system() == "Windows" else "Unix Makefiles"
    
    # 构建命令
    cmake_cmd = [
        "cmake",
        "-S", root_dir,
        "-B", build_dir,
        "-G", generator,
        "-DBUILD_PYTHON_BINDINGS=ON",
        f"-DPYTHON_EXECUTABLE={python_executable}",
        "-DCMAKE_CXX_STANDARD=17"
    ]
    
    # 执行 CMake 配置
    print("Configuring with CMake...")
    subprocess.check_call(cmake_cmd)
    
    # 执行 CMake 构建
    print("Building with CMake...")
    build_cmd = ["cmake", "--build", build_dir]
    subprocess.check_call(build_cmd)
    
    # 构建 wheel
    print("Building wheel...")
    cmd = [python_executable, 'setup.py', 'bdist_wheel']
    subprocess.check_call(cmd, cwd=script_dir)
    
    print("Wheel built successfully!")
    
    # 列出生成的 wheel 文件
    wheel_files = os.listdir(os.path.join(script_dir, 'dist'))
    print("Generated wheel files:")
    for wheel in wheel_files:
        print(f"  - {wheel}")
    
    print("\nTo install the wheel, run:")
    print(f"{python_executable} -m pip install {os.path.join('dist', wheel_files[0])}")

if __name__ == "__main__":
    main() 