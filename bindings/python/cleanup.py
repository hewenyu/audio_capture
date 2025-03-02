import os
import shutil
import sys

def debug_print(msg):
    print(f"DEBUG: {msg}")

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 要保留的文件列表
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
    "cleanup.py",  # 保留清理脚本本身
    "build_wheel.py"  # 保留构建wheel的脚本
]

# 要保留的目录列表
dirs_to_keep = [
    "src"
]

# 要删除的目录列表
dirs_to_remove = [
    "build",
    "build_c",
    "examples",
    "__pycache__"
]

def cleanup():
    print("开始清理项目...")
    
    # 删除不需要的目录
    for dir_name in dirs_to_remove:
        dir_path = os.path.join(SCRIPT_DIR, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            try:
                shutil.rmtree(dir_path)
                debug_print(f"已删除目录: {dir_path}")
            except Exception as e:
                debug_print(f"删除目录 {dir_path} 时出错: {str(e)}")
    
    # 删除不在保留列表中的文件
    for file_name in os.listdir(SCRIPT_DIR):
        file_path = os.path.join(SCRIPT_DIR, file_name)
        if os.path.isfile(file_path) and file_name not in files_to_keep:
            try:
                os.remove(file_path)
                debug_print(f"已删除文件: {file_path}")
            except Exception as e:
                debug_print(f"删除文件 {file_path} 时出错: {str(e)}")
    
    # 重命名 CMakeLists_c.txt 为 CMakeLists.txt
    cmake_src = os.path.join(SCRIPT_DIR, "CMakeLists_c.txt")
    cmake_dst = os.path.join(SCRIPT_DIR, "CMakeLists.txt")
    if os.path.exists(cmake_src):
        try:
            shutil.copy2(cmake_src, cmake_dst)
            debug_print(f"已复制 {cmake_src} 到 {cmake_dst}")
            os.remove(cmake_src)
            debug_print(f"已删除 {cmake_src}")
        except Exception as e:
            debug_print(f"重命名 {cmake_src} 时出错: {str(e)}")
    
    # 清理 src 目录中的不必要文件
    src_dir = os.path.join(SCRIPT_DIR, "src")
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        # 保留 audio_capture_bind.cpp 文件
        for file_name in os.listdir(src_dir):
            file_path = os.path.join(src_dir, file_name)
            if os.path.isfile(file_path) and file_name != "audio_capture_bind.cpp":
                try:
                    os.remove(file_path)
                    debug_print(f"已删除文件: {file_path}")
                except Exception as e:
                    debug_print(f"删除文件 {file_path} 时出错: {str(e)}")
            elif os.path.isdir(file_path) and file_name != "__pycache__":
                try:
                    shutil.rmtree(file_path)
                    debug_print(f"已删除目录: {file_path}")
                except Exception as e:
                    debug_print(f"删除目录 {file_path} 时出错: {str(e)}")
    
    print("项目清理完成！")
    print("\n保留的文件:")
    for file_name in files_to_keep:
        file_path = os.path.join(SCRIPT_DIR, file_name)
        if os.path.exists(file_path):
            print(f"  - {file_name}")
    
    print("\n保留的目录:")
    for dir_name in dirs_to_keep:
        dir_path = os.path.join(SCRIPT_DIR, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            print(f"  - {dir_name}")

if __name__ == "__main__":
    # 确认是否继续
    print("此脚本将删除不必要的文件，只保留构建 wheel 文件所需的关键文件。")
    print("请确保您已备份重要文件。")
    
    confirm = input("是否继续？(y/n): ")
    if confirm.lower() == 'y':
        cleanup()
    else:
        print("操作已取消。") 