import os
import sys
import platform
import shutil
from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
from wheel.bdist_wheel import bdist_wheel

# 调试信息
def debug_print(msg):
    print(f"DEBUG: {msg}")

# 获取 Python 版本信息
python_version = platform.python_version()
python_major_minor = '.'.join(python_version.split('.')[:2])  # 例如 3.11
debug_print(f"Python version: {python_version}")
debug_print(f"Python major.minor: {python_major_minor}")

# 获取平台信息
system_platform = platform.system()
machine = platform.machine()
platform_tag = f"{system_platform.lower()}_{machine.lower()}"
debug_print(f"Platform: {system_platform}")
debug_print(f"Machine: {machine}")
debug_print(f"Platform tag: {platform_tag}")

# 获取项目根目录的相对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))

debug_print(f"SCRIPT_DIR: {SCRIPT_DIR}")
debug_print(f"ROOT_DIR: {ROOT_DIR}")

# 检查 C 接口 DLL 是否存在
C_INTERFACE_DLL = os.path.join(SCRIPT_DIR, "audio_capture_c.dll")
if not os.path.exists(C_INTERFACE_DLL):
    raise RuntimeError(
        f"C interface DLL not found at {C_INTERFACE_DLL}. "
        "Please build the C interface DLL first."
    )
else:
    debug_print(f"Found C interface DLL at {C_INTERFACE_DLL}")

# 检查 audio_capture.py 是否存在
AUDIO_CAPTURE_PY = os.path.join(SCRIPT_DIR, "audio_capture.py")
if not os.path.exists(AUDIO_CAPTURE_PY):
    raise RuntimeError(f"audio_capture.py not found at {AUDIO_CAPTURE_PY}")
else:
    debug_print(f"Found audio_capture.py at {AUDIO_CAPTURE_PY}")

# 检查依赖 DLL 是否存在
required_dlls = [
    "libgcc_s_seh-1.dll",
    "libstdc++-6.dll",
    "libwinpthread-1.dll"
]

# 创建包目录结构
package_dir = os.path.join(SCRIPT_DIR, "audio_capture")
if not os.path.exists(package_dir):
    os.makedirs(package_dir)
    debug_print(f"Created package directory: {package_dir}")

# 创建 __init__.py 文件
init_file = os.path.join(package_dir, "__init__.py")
with open(init_file, "w") as f:
    f.write("# Audio Capture Package\n")
    f.write("from .audio_capture import *\n")
    f.write("__version__ = '0.1.0'\n")
debug_print(f"Created __init__.py at {init_file}")

# 复制 audio_capture.py 到包目录
shutil.copy2(AUDIO_CAPTURE_PY, package_dir)
debug_print(f"Copied {AUDIO_CAPTURE_PY} to {package_dir}")

# 复制 DLL 文件到包目录
if os.path.exists(C_INTERFACE_DLL):
    shutil.copy2(C_INTERFACE_DLL, package_dir)
    debug_print(f"Copied {C_INTERFACE_DLL} to {package_dir}")

# 复制依赖 DLL 到包目录
for dll in required_dlls:
    dll_path = os.path.join(SCRIPT_DIR, dll)
    if os.path.exists(dll_path):
        shutil.copy2(dll_path, package_dir)
        debug_print(f"Copied {dll_path} to {package_dir}")

# 定义包数据
package_data = {
    'audio_capture': ['*.dll'],
}

# 读取 README.md
with open(os.path.join(SCRIPT_DIR, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# 自定义bdist_wheel命令，设置平台特定的wheel
class BdistWheelPlatform(bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        # 标记为平台特定的wheel
        self.root_is_pure = False
        
    def get_tag(self):
        # 获取Python标签
        python_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
        # 获取ABI标签
        abi_tag = "none"
        # 获取平台标签
        if platform.system() == "Windows":
            plat_name = "win_amd64" if platform.machine().endswith('64') else "win32"
        elif platform.system() == "Linux":
            plat_name = "linux_x86_64" if platform.machine().endswith('64') else "linux_i686"
        elif platform.system() == "Darwin":
            plat_name = "macosx_10_9_x86_64" if platform.machine() == "x86_64" else "macosx_11_0_arm64"
        else:
            plat_name = "any"
        
        debug_print(f"Python tag: {python_tag}")
        debug_print(f"ABI tag: {abi_tag}")
        debug_print(f"Platform tag: {plat_name}")
        
        return python_tag, abi_tag, plat_name

setup(
    name="audio_capture",
    version="0.1.0",
    author="hewenyu",
    author_email="yuebanlaosiji@outlook.com",
    description="Python bindings for audio capture library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["audio_capture"],  # 使用包结构而不是单个模块
    package_data=package_data,
    include_package_data=True,
    zip_safe=False,
    python_requires=f">={python_major_minor}",
    install_requires=["numpy"],
    cmdclass={
        'bdist_wheel': BdistWheelPlatform,
    },
    classifiers=[
        f"Programming Language :: Python :: {python_major_minor}",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
) 