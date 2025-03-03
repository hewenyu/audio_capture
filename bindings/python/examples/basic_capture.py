#!/usr/bin/env python
import audio_capture
import numpy as np
import time
import os
import sys
import wave
import datetime
import struct

# 用于存储音频数据的列表
audio_data = []

def audio_callback(buffer):
    # buffer 是一个 numpy 数组，形状为 (frames, channels)
    # 将数据添加到全局列表中
    audio_data.append(buffer.copy())
    print(f"Received audio data: shape={buffer.shape}, max={np.max(buffer):.4f}, min={np.min(buffer):.4f}")

def save_to_wav(filename, format, data):
    """将音频数据保存为 WAV 文件"""
    print(f"Saving audio to {filename}...")
    
    # 创建输出目录
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 打开 WAV 文件
    with wave.open(filename, 'wb') as wav_file:
        # 设置 WAV 文件参数
        wav_file.setnchannels(format.channels)
        wav_file.setsampwidth(format.bits_per_sample // 8)
        wav_file.setframerate(format.sample_rate)
        
        # 将所有数据合并为一个大的 numpy 数组
        if not data:
            print("No audio data to save!")
            return False
        
        all_data = np.vstack(data)
        total_frames = all_data.shape[0]
        
        # 将 float32 [-1.0, 1.0] 转换为 int16 [-32768, 32767]
        int_data = (all_data * 32767).astype(np.int16)
        
        # 将数据写入 WAV 文件
        for frame in int_data:
            for sample in frame:
                wav_file.writeframesraw(struct.pack('<h', sample))
        
        print(f"Saved {total_frames} frames to {filename}")
        return True

def main():
    print("Audio Capture Python Example")
    print("----------------------------")
    
    # 创建 AudioCapture 实例
    capture = audio_capture.AudioCapture()
    
    # 初始化
    print("Initializing audio capture...")
    if not capture.initialize():
        print("Failed to initialize audio capture")
        return 1
    
    # 获取音频格式
    format = capture.get_format()
    print(f"Audio format: {format.sample_rate} Hz, {format.channels} channels, {format.bits_per_sample} bits")
    
    # 设置回调函数
    capture.set_callback(audio_callback)
    
    # 获取应用程序列表
    print("\nAvailable applications:")
    apps = capture.get_applications()
    for i, app in enumerate(apps):
        print(f"{i+1}. {app.name} (PID: {app.pid})")
    
    # 询问用户是捕获系统音频还是特定应用程序的音频
    choice = input("\nCapture system audio (s) or application audio (a)? [s/a]: ").strip().lower()
    
    if choice == 'a':
        # 捕获特定应用程序的音频
        try:
            app_index = int(input("Enter application number: ")) - 1
            if app_index < 0 or app_index >= len(apps):
                print("Invalid application number")
                return 1
            
            app = apps[app_index]
            print(f"Starting capture for {app.name} (PID: {app.pid})...")
            if not capture.start_process(app.pid):
                print("Failed to start audio capture for the selected application")
                return 1
            
            # 创建输出文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            app_name = app.name.replace(" ", "_").replace(":", "").replace("\\", "_").replace("/", "_")
            output_dir = "recordings"
            output_file = os.path.join(output_dir, f"{app_name}_{timestamp}.wav")
            
        except ValueError:
            print("Invalid input")
            return 1
    else:
        # 捕获系统音频
        print("Starting system audio capture...")
        if not capture.start():
            print("Failed to start audio capture")
            return 1
        
        # 创建输出文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "recordings"
        output_file = os.path.join(output_dir, f"system_{timestamp}.wav")
    
    # 捕获 30 秒
    duration = 30
    print(f"Capturing audio for {duration} seconds...")
    try:
        for i in range(duration):
            sys.stdout.write(f"\rCapturing: {i+1}/{duration} seconds")
            sys.stdout.flush()
            time.sleep(1)
        print("\nCapture complete!")
    except KeyboardInterrupt:
        print("\nCapture interrupted by user")
    
    # 停止捕获
    print("Stopping audio capture...")
    capture.stop()
    
    # 保存音频数据
    if audio_data:
        save_to_wav(output_file, format, audio_data)
        print(f"Audio saved to {output_file}")
    else:
        print("No audio data was captured!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 