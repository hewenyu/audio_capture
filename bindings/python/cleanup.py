import os
import shutil
import sys

def debug_print(msg):
    print(f"DEBUG: {msg}")

# Get current script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# List of files to keep
files_to_keep = [
    "c_interface.cpp",
    "audio_capture_c.dll",
    "setup.py",
    "pyproject.toml",
    "setup.cfg",
    "CMakeLists_c.txt",
    "audio_capture.py",
    "libgcc_s_seh-1.dll",
    "libstdc++-6.dll",
    "libwinpthread-1.dll",
    "README.md",
    "cleanup.py",  # Keep the cleanup script itself
    "build_wheel.py"  # Keep the wheel building script
]

# List of directories to keep
dirs_to_keep = [
    "src"
]

# List of directories to remove
dirs_to_remove = [
    "build",
    "build_c",
    "examples",
    "__pycache__"
]

def cleanup():
    print("Starting project cleanup...")
    
    # Delete unnecessary directories
    for dir_name in dirs_to_remove:
        dir_path = os.path.join(SCRIPT_DIR, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            try:
                shutil.rmtree(dir_path)
                debug_print(f"Deleted directory: {dir_path}")
            except Exception as e:
                debug_print(f"Error deleting directory {dir_path}: {str(e)}")
    
    # Delete files not in the keep list
    for file_name in os.listdir(SCRIPT_DIR):
        file_path = os.path.join(SCRIPT_DIR, file_name)
        if os.path.isfile(file_path) and file_name not in files_to_keep:
            try:
                os.remove(file_path)
                debug_print(f"Deleted file: {file_path}")
            except Exception as e:
                debug_print(f"Error deleting file {file_path}: {str(e)}")
    
    # Rename CMakeLists_c.txt to CMakeLists.txt
    cmake_src = os.path.join(SCRIPT_DIR, "CMakeLists_c.txt")
    cmake_dst = os.path.join(SCRIPT_DIR, "CMakeLists.txt")
    if os.path.exists(cmake_src):
        try:
            shutil.copy2(cmake_src, cmake_dst)
            debug_print(f"Copied {cmake_src} to {cmake_dst}")
            os.remove(cmake_src)
            debug_print(f"Deleted {cmake_src}")
        except Exception as e:
            debug_print(f"Error renaming {cmake_src}: {str(e)}")
    
    # Clean unnecessary files in src directory
    src_dir = os.path.join(SCRIPT_DIR, "src")
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        # Keep audio_capture_bind.cpp file
        for file_name in os.listdir(src_dir):
            file_path = os.path.join(src_dir, file_name)
            if os.path.isfile(file_path) and file_name != "audio_capture_bind.cpp":
                try:
                    os.remove(file_path)
                    debug_print(f"Deleted file: {file_path}")
                except Exception as e:
                    debug_print(f"Error deleting file {file_path}: {str(e)}")
            elif os.path.isdir(file_path) and file_name != "__pycache__":
                try:
                    shutil.rmtree(file_path)
                    debug_print(f"Deleted directory: {file_path}")
                except Exception as e:
                    debug_print(f"Error deleting directory {file_path}: {str(e)}")
    
    print("Project cleanup completed!")
    print("\nKept files:")
    for file_name in files_to_keep:
        file_path = os.path.join(SCRIPT_DIR, file_name)
        if os.path.exists(file_path):
            print(f"  - {file_name}")
    
    print("\nKept directories:")
    for dir_name in dirs_to_keep:
        dir_path = os.path.join(SCRIPT_DIR, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"  - {dir_name}")

if __name__ == "__main__":
    # Confirm whether to continue
    print("This script will delete unnecessary files, keeping only the key files needed to build the wheel.")
    print("Please make sure you have backed up important files.")
    
    confirm = input("Continue? (y/n): ")
    if confirm.lower() == 'y':
        cleanup()
    else:
        print("Operation cancelled.") 