import sys
import os
import time
import numpy as np
import wave
import struct
from datetime import datetime

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

# 全局变量，用于存储音频数据
audio_data = []
sample_rate = 16000  # 默认采样率
channels = 1  # 默认通道数
bits_per_sample = 16  # 默认位深度

# 音频回调函数
def audio_callback(buffer, user_data):
    """
    处理捕获的音频数据
    
    参数:
        buffer: 包含音频数据的NumPy数组
        user_data: 用户数据（可选）
    """
    global audio_data
    
    # 将音频数据添加到全局列表中
    if len(buffer) > 0:
        audio_data.append(buffer.copy())
        
        # 计算音频数据的统计信息
        min_val = np.min(buffer)
        max_val = np.max(buffer)
        rms = np.sqrt(np.mean(np.square(buffer)))
        
        print(f"Audio data: min={min_val:.4f}, max={max_val:.4f}, rms={rms:.4f}, samples={len(buffer)}")
    else:
        print("Received empty buffer")

def save_to_wav(filename, data, sample_rate, channels, bits_per_sample):
    """
    将音频数据保存为WAV文件
    
    参数:
        filename: WAV文件名
        data: 音频数据（NumPy数组）
        sample_rate: 采样率
        channels: 通道数
        bits_per_sample: 位深度
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    
    # 打开WAV文件
    with wave.open(filename, 'w') as wav_file:
        # 设置WAV文件参数
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(bits_per_sample // 8)
        wav_file.setframerate(sample_rate)
        
        # 将浮点数据转换为整数数据
        max_amplitude = 2 ** (bits_per_sample - 1) - 1
        data_int = (data * max_amplitude).astype(np.int16)
        
        # 写入WAV文件
        wav_file.writeframes(data_int.tobytes())
    
    print(f"音频数据已保存到: {filename}")

def main():
    global audio_data, sample_rate, channels, bits_per_sample
    
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
        sample_rate = format_info['sample_rate']
        channels = format_info['channels']
        bits_per_sample = format_info['bits_per_sample']
        print(f"音频格式: {sample_rate} Hz, {channels} 通道, {bits_per_sample} 位")
    else:
        print("无法获取音频格式，使用默认值")
    
    # 获取应用程序列表
    print("\n获取应用程序列表...")
    apps = audio_capture.get_applications()
    if apps:
        print("找到以下应用程序:")
        for i, app in enumerate(apps):
            print(f"{i+1}. PID: {app['pid']}, 名称: {app['name']}")
        
        # 手动输入应用ID
        try:
            choice = input("\n请输入要录制的应用序号 (1-{0})，或直接输入PID，或按Enter录制系统音频: ".format(len(apps)))
            
            if choice.strip():
                # 尝试将输入解析为整数
                try:
                    choice_int = int(choice)
                    
                    # 检查是否是序号
                    if 1 <= choice_int <= len(apps):
                        selected_pid = apps[choice_int-1]['pid']
                        app_name = apps[choice_int-1]['name']
                    else:
                        # 假设是直接输入的PID
                        selected_pid = choice_int
                        app_name = f"PID-{selected_pid}"
                        
                    print(f"\n选择应用: {app_name} (PID: {selected_pid})")
                    
                    # 开始捕获特定应用程序的音频
                    print(f"开始捕获应用程序 (PID: {selected_pid}) 的音频...")
                    if not audio_capture.start_process(selected_pid):
                        print(f"无法捕获应用程序 (PID: {selected_pid}) 的音频，尝试捕获系统音频...")
                        if not audio_capture.start():
                            print("无法捕获系统音频")
                            audio_capture.cleanup()
                            return
                        else:
                            app_name = "System"
                    
                except ValueError:
                    print("输入无效，将捕获系统音频")
                    if not audio_capture.start():
                        print("无法捕获系统音频")
                        audio_capture.cleanup()
                        return
                    app_name = "System"
            else:
                # 开始捕获系统音频
                print("\n开始捕获系统音频...")
                if not audio_capture.start():
                    print("无法捕获系统音频")
                    audio_capture.cleanup()
                    return
                app_name = "System"
        except Exception as e:
            print(f"发生错误: {e}")
            print("将捕获系统音频")
            if not audio_capture.start():
                print("无法捕获系统音频")
                audio_capture.cleanup()
                return
            app_name = "System"
    else:
        print("未找到应用程序，将捕获系统音频")
        # 开始捕获系统音频
        print("\n开始捕获系统音频...")
        if not audio_capture.start():
            print("无法捕获系统音频")
            audio_capture.cleanup()
            return
        app_name = "System"
    
    # 清空之前的音频数据
    audio_data = []
    
    # 录制时长（秒）
    recording_duration = 30
    print(f"\n正在录制音频，持续 {recording_duration} 秒...")
    
    try:
        # 录制指定时长
        start_time = time.time()
        while time.time() - start_time < recording_duration:
            remaining = recording_duration - (time.time() - start_time)
            print(f"\r录制中... 剩余 {remaining:.1f} 秒", end="")
            time.sleep(0.1)
        print("\n录制完成!")
    except KeyboardInterrupt:
        print("\n用户中断录制")
    
    # 停止音频捕获
    print("\n停止音频捕获...")
    audio_capture.stop()
    
    # 清理资源
    print("\n清理资源...")
    audio_capture.cleanup()
    
    # 处理录制的音频数据
    if audio_data:
        # 合并所有音频数据
        all_audio = np.concatenate(audio_data)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 处理应用名称，避免路径分隔符问题
        app_name_clean = os.path.basename(app_name).split('.')[0]
        filename = f"recorded_{app_name_clean}_{timestamp}.wav"
        
        # 保存为WAV文件
        print(f"\n保存音频数据到WAV文件...")
        save_to_wav(filename, all_audio, sample_rate, channels, bits_per_sample)
        
        print(f"\n录制信息:")
        print(f"  - 应用: {app_name}")
        print(f"  - 时长: {len(all_audio) / sample_rate:.2f} 秒")
        print(f"  - 采样率: {sample_rate} Hz")
        print(f"  - 通道数: {channels}")
        print(f"  - 位深度: {bits_per_sample} 位")
        print(f"  - 样本数: {len(all_audio)}")
        print(f"  - 文件大小: {os.path.getsize(filename) / 1024:.1f} KB")
    else:
        print("\n未捕获到音频数据")
    
    print("\n示例结束")

if __name__ == "__main__":
    main() 