import os
import sys
import subprocess
import shutil
import platform
import time
from pathlib import Path

def debug_print(msg):
    print(f"DEBUG: {msg}")

# 获取项目路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
WINDOWS_DIR = os.path.join(ROOT_DIR, "c", "windows")
BUILD_DIR = os.path.join(WINDOWS_DIR, "build")
DIST_DIR = os.path.join(SCRIPT_DIR, "dist")
PYTHON_BUILD_DIR = os.path.join(SCRIPT_DIR, "build")
PACKAGE_DIR = os.path.join(SCRIPT_DIR, "audio_capture")

debug_print(f"SCRIPT_DIR: {SCRIPT_DIR}")
debug_print(f"ROOT_DIR: {ROOT_DIR}")
debug_print(f"WINDOWS_DIR: {WINDOWS_DIR}")
debug_print(f"BUILD_DIR: {BUILD_DIR}")
debug_print(f"DIST_DIR: {DIST_DIR}")
debug_print(f"PYTHON_BUILD_DIR: {PYTHON_BUILD_DIR}")
debug_print(f"PACKAGE_DIR: {PACKAGE_DIR}")

# 获取Python和平台信息
python_version = platform.python_version()
python_major_minor = '.'.join(python_version.split('.')[:2])
system_platform = platform.system()
machine = platform.machine()
debug_print(f"Python version: {python_version}")
debug_print(f"Platform: {system_platform}")
debug_print(f"Machine: {machine}")

# 检查是否已安装必要的包
required_packages = ["wheel>=0.36.0", "build", "setuptools>=42", "cmake"]
for package in required_packages:
    package_name = package.split(">=")[0]
    try:
        __import__(package_name)
        debug_print(f"{package_name} is already installed")
    except ImportError:
        print(f"正在安装 {package} 包...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        try:
            __import__(package_name)
            debug_print(f"{package_name} version: {sys.modules[package_name].__version__}")
        except (ImportError, AttributeError):
            debug_print(f"Installed {package_name} but couldn't import or get version")

# 清理旧的构建文件
print("\n清理旧的构建文件...")
for dir_to_clean in [DIST_DIR, PYTHON_BUILD_DIR, PACKAGE_DIR]:
    if os.path.exists(dir_to_clean):
        print(f"删除目录: {dir_to_clean}")
        shutil.rmtree(dir_to_clean)

# 确保目录存在
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PYTHON_BUILD_DIR, exist_ok=True)
os.makedirs(PACKAGE_DIR, exist_ok=True)

# 构建C++库
print("\n构建C++库...")

# 1. 首先构建wasapi_capture库
if not os.path.exists(BUILD_DIR):
    os.makedirs(BUILD_DIR)

os.chdir(BUILD_DIR)
print(f"当前目录: {os.getcwd()}")

# 运行CMake配置
print("运行CMake配置wasapi_capture库...")
cmake_cmd = ["cmake", "..", "-G", "MinGW Makefiles"]
print(f"执行命令: {' '.join(cmake_cmd)}")
subprocess.check_call(cmake_cmd)

# 构建wasapi_capture库
print("构建wasapi_capture库...")
build_cmd = ["cmake", "--build", ".", "--config", "Release"]
print(f"执行命令: {' '.join(build_cmd)}")
subprocess.check_call(build_cmd)

# 2. 构建Python C接口
os.chdir(SCRIPT_DIR)
print(f"当前目录: {os.getcwd()}")

# 创建构建目录
if not os.path.exists(PYTHON_BUILD_DIR):
    os.makedirs(PYTHON_BUILD_DIR)

os.chdir(PYTHON_BUILD_DIR)
print(f"当前目录: {os.getcwd()}")

# 运行CMake配置
print("运行CMake配置Python C接口...")
cmake_cmd = ["cmake", "..", "-G", "MinGW Makefiles"]
print(f"执行命令: {' '.join(cmake_cmd)}")
subprocess.check_call(cmake_cmd)

# 构建Python C接口
print("构建Python C接口...")
build_cmd = ["cmake", "--build", ".", "--config", "Release"]
print(f"执行命令: {' '.join(build_cmd)}")
subprocess.check_call(build_cmd)

# 检查DLL是否已生成
dll_path = os.path.join(PYTHON_BUILD_DIR, "audio_capture_c.dll")
if not os.path.exists(dll_path):
    print(f"错误: 未找到生成的DLL: {dll_path}")
    sys.exit(1)
else:
    debug_print(f"DLL已生成: {dll_path}")
    # 复制到脚本目录
    shutil.copy2(dll_path, SCRIPT_DIR)
    debug_print(f"已复制DLL到: {SCRIPT_DIR}")

# 检查依赖DLL
required_dlls = [
    "libgcc_s_seh-1.dll",
    "libstdc++-6.dll",
    "libwinpthread-1.dll"
]

for dll in required_dlls:
    dll_path = os.path.join(SCRIPT_DIR, dll)
    if not os.path.exists(dll_path):
        print(f"警告: 未找到依赖DLL: {dll_path}")
        # 尝试从系统路径复制
        try:
            # 使用where命令查找DLL
            where_cmd = ["where", dll]
            result = subprocess.check_output(where_cmd, text=True)
            system_dll_path = result.strip().split('\n')[0]
            if os.path.exists(system_dll_path):
                print(f"从系统路径复制DLL: {system_dll_path} -> {dll_path}")
                shutil.copy2(system_dll_path, dll_path)
            else:
                print(f"无法找到系统DLL: {dll}")
        except Exception as e:
            print(f"复制DLL时出错: {e}")
    else:
        debug_print(f"依赖DLL已存在: {dll_path}")

# 创建包结构
print("\n创建包结构...")

# 创建 __init__.py 文件
init_file = os.path.join(PACKAGE_DIR, "__init__.py")
with open(init_file, "w") as f:
    f.write("# Audio Capture Package\n")
    f.write("from .audio_capture import *\n")
    f.write("__version__ = '0.1.0'\n")
debug_print(f"Created __init__.py at {init_file}")

# 复制 audio_capture.py 到包目录
audio_capture_py = os.path.join(SCRIPT_DIR, "audio_capture.py")
shutil.copy2(audio_capture_py, PACKAGE_DIR)
debug_print(f"Copied {audio_capture_py} to {PACKAGE_DIR}")

# 复制DLL文件到包目录
dll_file = os.path.join(SCRIPT_DIR, "audio_capture_c.dll")
if os.path.exists(dll_file):
    shutil.copy2(dll_file, PACKAGE_DIR)
    debug_print(f"Copied {dll_file} to {PACKAGE_DIR}")
else:
    print(f"警告: 未找到DLL: {dll_file}")

# 复制依赖DLL到包目录
for dll in required_dlls:
    dll_path = os.path.join(SCRIPT_DIR, dll)
    if os.path.exists(dll_path):
        shutil.copy2(dll_path, PACKAGE_DIR)
        debug_print(f"Copied {dll_path} to {PACKAGE_DIR}")

# 构建wheel包
os.chdir(SCRIPT_DIR)
print(f"当前目录: {os.getcwd()}")

print("\n构建wheel包...")
# 使用bdist_wheel命令构建平台特定的wheel
wheel_cmd = [sys.executable, "setup.py", "bdist_wheel", "--plat-name", f"{system_platform.lower()}_{machine.lower()}", "--python-tag", f"cp{sys.version_info.major}{sys.version_info.minor}"]
print(f"执行命令: {' '.join(wheel_cmd)}")
subprocess.check_call(wheel_cmd)

# 列出生成的wheel文件
print("\n生成的wheel文件:")
for wheel_file in os.listdir(DIST_DIR):
    if wheel_file.endswith(".whl"):
        wheel_path = os.path.join(DIST_DIR, wheel_file)
        print(f"  - {wheel_file} ({os.path.getsize(wheel_path) / 1024:.1f} KB)")

print("\nwheel包构建完成!")
print(f"wheel包位置: {DIST_DIR}")
print("可以使用以下命令安装:")
print(f"pip install {os.path.join(DIST_DIR, os.listdir(DIST_DIR)[0] if os.listdir(DIST_DIR) else 'dist/*.whl')}") 