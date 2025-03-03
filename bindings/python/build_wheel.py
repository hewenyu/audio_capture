import os
import sys
import subprocess
import shutil
import platform
import time
from pathlib import Path

def debug_print(msg):
    print(f"DEBUG: {msg}")

# Get project paths
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

# Get Python and platform information
python_version = platform.python_version()
python_major_minor = '.'.join(python_version.split('.')[:2])
system_platform = platform.system()
machine = platform.machine()
debug_print(f"Python version: {python_version}")
debug_print(f"Platform: {system_platform}")
debug_print(f"Machine: {machine}")

# Check if required packages are installed
required_packages = ["wheel>=0.36.0", "build", "setuptools>=42", "cmake"]
for package in required_packages:
    package_name = package.split(">=")[0]
    try:
        __import__(package_name)
        debug_print(f"{package_name} is already installed")
    except ImportError:
        print(f"Installing {package} package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        try:
            __import__(package_name)
            debug_print(f"{package_name} version: {sys.modules[package_name].__version__}")
        except (ImportError, AttributeError):
            debug_print(f"Installed {package_name} but couldn't import or get version")

# Clean old build files
print("\nCleaning old build files...")
for dir_to_clean in [DIST_DIR, PYTHON_BUILD_DIR, PACKAGE_DIR]:
    if os.path.exists(dir_to_clean):
        print(f"Deleting directory: {dir_to_clean}")
        shutil.rmtree(dir_to_clean)

# Ensure directories exist
os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(PYTHON_BUILD_DIR, exist_ok=True)
os.makedirs(PACKAGE_DIR, exist_ok=True)

# Build C++ library
print("\nBuilding C++ library...")

# 1. First build wasapi_capture library
if not os.path.exists(BUILD_DIR):
    os.makedirs(BUILD_DIR)

os.chdir(BUILD_DIR)
print(f"Current directory: {os.getcwd()}")

# Run CMake configuration
print("Running CMake configuration for wasapi_capture library...")
cmake_cmd = ["cmake", "..", "-G", "MinGW Makefiles"]
print(f"Executing command: {' '.join(cmake_cmd)}")
subprocess.check_call(cmake_cmd)

# Build wasapi_capture library
print("Building wasapi_capture library...")
build_cmd = ["cmake", "--build", ".", "--config", "Release"]
print(f"Executing command: {' '.join(build_cmd)}")
subprocess.check_call(build_cmd)

# 2. Build Python C interface
os.chdir(SCRIPT_DIR)
print(f"Current directory: {os.getcwd()}")

# Create build directory
if not os.path.exists(PYTHON_BUILD_DIR):
    os.makedirs(PYTHON_BUILD_DIR)

os.chdir(PYTHON_BUILD_DIR)
print(f"Current directory: {os.getcwd()}")

# Run CMake configuration
print("Running CMake configuration for Python C interface...")
cmake_cmd = ["cmake", "..", "-G", "MinGW Makefiles"]
print(f"Executing command: {' '.join(cmake_cmd)}")
subprocess.check_call(cmake_cmd)

# Build Python C interface
print("Building Python C interface...")
build_cmd = ["cmake", "--build", ".", "--config", "Release"]
print(f"Executing command: {' '.join(build_cmd)}")
subprocess.check_call(build_cmd)

# Check if DLL was generated
dll_path = os.path.join(PYTHON_BUILD_DIR, "audio_capture_c.dll")
if not os.path.exists(dll_path):
    print(f"Error: Generated DLL not found: {dll_path}")
    sys.exit(1)
else:
    debug_print(f"DLL generated: {dll_path}")
    # Copy to script directory
    shutil.copy2(dll_path, SCRIPT_DIR)
    debug_print(f"Copied DLL to: {SCRIPT_DIR}")

# Check dependency DLLs
required_dlls = [
    "libgcc_s_seh-1.dll",
    "libstdc++-6.dll",
    "libwinpthread-1.dll"
]

for dll in required_dlls:
    dll_path = os.path.join(SCRIPT_DIR, dll)
    if not os.path.exists(dll_path):
        print(f"Warning: Dependency DLL not found: {dll_path}")
        # Try to copy from system path
        try:
            # Use where command to find DLL
            where_cmd = ["where", dll]
            result = subprocess.check_output(where_cmd, text=True)
            system_dll_path = result.strip().split('\n')[0]
            if os.path.exists(system_dll_path):
                print(f"Copying DLL from system path: {system_dll_path} -> {dll_path}")
                shutil.copy2(system_dll_path, dll_path)
            else:
                print(f"Could not find system DLL: {dll}")
        except Exception as e:
            print(f"Error copying DLL: {e}")
    else:
        debug_print(f"Dependency DLL exists: {dll_path}")

# Create package structure
print("\nCreating package structure...")

# Create __init__.py file
init_file = os.path.join(PACKAGE_DIR, "__init__.py")
with open(init_file, "w") as f:
    f.write("# Audio Capture Package\n")
    f.write("from .audio_capture import *\n")
    f.write("__version__ = '0.1.0'\n")
debug_print(f"Created __init__.py at {init_file}")

# Copy audio_capture.py to package directory
audio_capture_py = os.path.join(SCRIPT_DIR, "audio_capture.py")
shutil.copy2(audio_capture_py, PACKAGE_DIR)
debug_print(f"Copied {audio_capture_py} to {PACKAGE_DIR}")

# Copy DLL file to package directory
dll_file = os.path.join(SCRIPT_DIR, "audio_capture_c.dll")
if os.path.exists(dll_file):
    shutil.copy2(dll_file, PACKAGE_DIR)
    debug_print(f"Copied {dll_file} to {PACKAGE_DIR}")
else:
    print(f"Warning: DLL not found: {dll_file}")

# Copy dependency DLLs to package directory
for dll in required_dlls:
    dll_path = os.path.join(SCRIPT_DIR, dll)
    if os.path.exists(dll_path):
        shutil.copy2(dll_path, PACKAGE_DIR)
        debug_print(f"Copied {dll_path} to {PACKAGE_DIR}")

# Build wheel package
os.chdir(SCRIPT_DIR)
print(f"Current directory: {os.getcwd()}")

print("\nBuilding wheel package...")
# Use bdist_wheel command to build platform-specific wheel
wheel_cmd = [sys.executable, "setup.py", "bdist_wheel", "--plat-name", f"{system_platform.lower()}_{machine.lower()}", "--python-tag", f"cp{sys.version_info.major}{sys.version_info.minor}"]
print(f"Executing command: {' '.join(wheel_cmd)}")
subprocess.check_call(wheel_cmd)

# List generated wheel files
print("\nGenerated wheel files:")
for wheel_file in os.listdir(DIST_DIR):
    if wheel_file.endswith(".whl"):
        wheel_path = os.path.join(DIST_DIR, wheel_file)
        print(f"  - {wheel_file} ({os.path.getsize(wheel_path) / 1024:.1f} KB)")

print("\nWheel package build completed!")
print(f"Wheel package location: {DIST_DIR}")
print("You can install using the following command:")
print(f"pip install {os.path.join(DIST_DIR, os.listdir(DIST_DIR)[0] if os.listdir(DIST_DIR) else 'dist/*.whl')}") 