# Audio Capture Python Bindings

这个包提供了对Windows音频捕获库的Python绑定，允许你捕获系统音频或特定应用程序的音频。

## 功能特点

- 捕获系统音频
- 捕获特定应用程序的音频
- 获取可用应用程序列表
- 获取音频格式信息
- 通过回调函数处理实时音频数据

## 安装

### 从PyPI安装

```bash
pip install audio-capture
```

### 从源代码安装

1. 克隆仓库

```bash
git clone https://github.com/hewenyu/audio_capture.git
cd audio_capture
```

2. 构建并安装Python绑定

```bash
cd bindings/python
python build_wheel.py
pip install dist/audio_capture-0.1.0-*.whl
```

## 快速开始

以下是一个简单的例子，展示如何使用这个库捕获系统音频：

```python
import audio_capture
import numpy as np
import time

# 定义音频回调函数
def audio_callback(buffer, user_data):
    # buffer是一个包含音频数据的NumPy数组
    if len(buffer) > 0:
        rms = np.sqrt(np.mean(np.square(buffer)))
        print(f"音频数据: RMS={rms:.4f}, 样本数={len(buffer)}")

# 初始化音频捕获
if audio_capture.init(audio_callback):
    # 开始捕获系统音频
    if audio_capture.start():
        print("开始捕获音频...")
        
        # 运行10秒
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            print("用户中断")
        
        # 停止捕获
        audio_capture.stop()
    
    # 清理资源
    audio_capture.cleanup()
```

## 捕获特定应用程序的音频

你可以获取可用应用程序列表，并捕获特定应用程序的音频：

```python
import audio_capture
import time

# 定义音频回调函数
def audio_callback(buffer, user_data):
    # 处理音频数据...
    pass

# 初始化音频捕获
if audio_capture.init(audio_callback):
    # 获取应用程序列表
    apps = audio_capture.get_applications()
    
    if apps:
        print("可用应用程序:")
        for i, app in enumerate(apps):
            print(f"{i+1}. PID: {app['pid']}, 名称: {app['name']}")
        
        # 选择第一个应用程序
        selected_app = apps[0]
        print(f"选择应用程序: {selected_app['name']} (PID: {selected_app['pid']})")
        
        # 开始捕获特定应用程序的音频
        if audio_capture.start_process(selected_app['pid']):
            print("开始捕获应用程序音频...")
            
            # 运行一段时间
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                print("用户中断")
            
            # 停止捕获
            audio_capture.stop()
    
    # 清理资源
    audio_capture.cleanup()
```

## 获取音频格式

你可以获取捕获的音频格式信息：

```python
import audio_capture

# 初始化音频捕获
if audio_capture.init(lambda buffer, user_data: None):
    # 获取音频格式
    format_info = audio_capture.get_format()
    
    if format_info:
        print(f"音频格式:")
        print(f"采样率: {format_info['sample_rate']} Hz")
        print(f"通道数: {format_info['channels']}")
        print(f"位深度: {format_info['bits_per_sample']} 位")
    
    # 清理资源
    audio_capture.cleanup()
```

## API参考

### 初始化和清理

- `audio_capture.init(callback_fn, user_data=None)` - 初始化音频捕获
- `audio_capture.cleanup()` - 清理资源

### 控制捕获

- `audio_capture.start()` - 开始捕获系统音频
- `audio_capture.start_process(pid)` - 开始捕获特定进程的音频
- `audio_capture.stop()` - 停止音频捕获

### 获取信息

- `audio_capture.get_applications(max_count=50)` - 获取可用应用程序列表
- `audio_capture.get_format()` - 获取音频格式信息

### 回调函数

回调函数的格式为：

```python
def audio_callback(buffer, user_data):
    # buffer是一个包含音频数据的NumPy数组
    # user_data是传递给init函数的用户数据
    pass
```

## 示例

查看 `examples` 目录中的示例脚本，了解更多使用方法。

## 许可证

MIT License 