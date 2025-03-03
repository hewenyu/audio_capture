#!/usr/bin/env python
import audio_capture
import numpy as np
import time
import os
import sys

def audio_callback(buffer):
    # buffer 是一个 numpy 数组，形状为 (frames, channels)
    # 这里我们只是打印一些信息
    print(f"Received audio data: shape={buffer.shape}, max={np.max(buffer):.4f}, min={np.min(buffer):.4f}")

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
        except ValueError:
            print("Invalid input")
            return 1
    else:
        # 捕获系统音频
        print("Starting system audio capture...")
        if not capture.start():
            print("Failed to start audio capture")
            return 1
    
    # 捕获 10 秒
    duration = 10
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
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 