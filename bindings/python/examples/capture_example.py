import sys
import os
import time
import numpy as np

# 尝试导入audio_capture模块
try:
    import audio_capture
except ImportError:
    try:
        # 如果直接导入失败，尝试从包中导入
        from audio_capture import audio_capture
    except ImportError:
        print("错误: 无法导入audio_capture模块。请确保已安装该模块。")
        sys.exit(1)

# 打印环境信息
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Current directory: {os.getcwd()}")
print(f"PATH: {os.environ.get('PATH', '')}")

# 列出当前目录中的文件
print("Files in current directory:")
for item in os.listdir():
    if os.path.isdir(item):
        print(f"  - {item}")
    else:
        print(f"  - {item}")

# 音频回调函数
def audio_callback(buffer, user_data):
    """
    处理捕获的音频数据
    
    参数:
        buffer: 包含音频数据的NumPy数组
        user_data: 用户数据（可选）
    """
    # 计算音频数据的统计信息
    if len(buffer) > 0:
        min_val = np.min(buffer)
        max_val = np.max(buffer)
        rms = np.sqrt(np.mean(np.square(buffer)))
        
        print(f"Audio data: min={min_val:.4f}, max={max_val:.4f}, rms={rms:.4f}, samples={len(buffer)}")
    else:
        print("Received empty buffer")

def main():
    print("Audio Capture Example")
    print("=====================")

    # 初始化音频捕获
    print("\n初始化音频捕获...")
    if not audio_capture.init(audio_callback):
        print("初始化音频捕获失败")
        return
    
    # 获取音频格式
    print("\n获取音频格式...")
    format_info = audio_capture.get_format()
    if format_info:
        print(f"音频格式: {format_info['sample_rate']} Hz, {format_info['channels']} 通道, {format_info['bits_per_sample']} 位")
    else:
        print("无法获取音频格式")
    
    # 获取应用程序列表
    print("\n获取应用程序列表...")
    apps = audio_capture.get_applications()
    if apps:
        print("找到以下应用程序:")
        for i, app in enumerate(apps):
            print(f"{i+1}. PID: {app['pid']}, 名称: {app['name']}")
        
        # 可选: 选择特定应用程序进行捕获
        # selected_app = apps[0]
        # print(f"\n选择应用程序: {selected_app['name']} (PID: {selected_app['pid']})")
        # if audio_capture.start_process(selected_app['pid']):
        #     print("开始捕获应用程序音频...")
        # else:
        #     print("开始捕获应用程序音频失败")
        #     audio_capture.cleanup()
        #     return
    else:
        print("未找到应用程序")
    
    # 开始捕获系统音频
    print("\n开始捕获系统音频...")
    if not audio_capture.start():
        print("开始捕获系统音频失败")
        audio_capture.cleanup()
        return
    
    print("正在捕获音频，按 Ctrl+C 停止...")
    try:
        # 捕获10秒音频
        time.sleep(10)
    except KeyboardInterrupt:
        print("\n用户中断")
    
    # 停止音频捕获
    print("\n停止音频捕获...")
    audio_capture.stop()
    
    # 清理资源
    print("\n清理资源...")
    audio_capture.cleanup()
    
    print("\n示例结束")

if __name__ == "__main__":
    main() 