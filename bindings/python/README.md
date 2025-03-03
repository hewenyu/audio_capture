# Audio Capture Python Bindings

这是 Audio Capture 库的 Python 绑定，允许你在 Python 中捕获系统音频或特定应用程序的音频输出。

## 安装

### 从预编译的 wheel 安装

最简单的方法是从 GitHub Releases 页面下载预编译的 wheel 文件：

```bash
pip install audio_capture-0.1.0-cp39-cp39-win_amd64.whl
```

### 从源代码构建

如果你想从源代码构建 Python 绑定，请按照以下步骤操作：

1. 确保你已安装以下依赖：
   - Python 3.8 或更高版本
   - CMake 3.12 或更高版本
   - 适合你平台的 C++ 编译器（Windows 上的 MinGW-w64 或 Visual Studio）

2. 克隆仓库：
   ```bash
   git clone https://github.com/hewenyu/audio_capture.git
   cd audio_capture
   ```

3. 构建并安装 Python 绑定：

   **Windows (使用默认 Python):**
   ```bash
   build_python.cmd
   ```

   **Windows (指定 Python 路径):**
   ```bash
   # 编辑 build_python.cmd 文件，设置 PYTHON_PATH 变量
   # 或者直接在命令行中设置环境变量
   set PYTHON_PATH=C:\path\to\your\python.exe
   build_python.cmd
   ```

   **Linux/macOS:**
   ```bash
   ./build_python.sh
   ```

4. 安装生成的 wheel 文件：
   ```bash
   pip install bindings/python/dist/audio_capture-0.1.0-*.whl
   ```

## 使用方法

以下是一个简单的示例，展示如何使用 Audio Capture Python 绑定：

```python
import audio_capture
import numpy as np
import time

# 定义音频回调函数
def audio_callback(buffer):
    # buffer 是一个 numpy 数组，形状为 (frames, channels)
    # 这里我们只是打印一些信息
    print(f"Received audio data: shape={buffer.shape}, max={np.max(buffer)}, min={np.min(buffer)}")

# 创建 AudioCapture 实例
capture = audio_capture.AudioCapture()

# 初始化
if not capture.initialize():
    print("Failed to initialize audio capture")
    exit(1)

# 获取音频格式
format = capture.get_format()
print(f"Audio format: {format.sample_rate} Hz, {format.channels} channels, {format.bits_per_sample} bits")

# 设置回调函数
capture.set_callback(audio_callback)

# 获取应用程序列表
apps = capture.get_applications()
print("Available applications:")
for app in apps:
    print(f"  - {app.name} (PID: {app.pid})")

# 开始捕获系统音频
if not capture.start():
    print("Failed to start audio capture")
    exit(1)

print("Capturing system audio for 10 seconds...")
time.sleep(10)

# 停止捕获
capture.stop()
print("Audio capture stopped")

# 如果要捕获特定应用程序的音频，可以使用：
# capture.start_process(app.pid)
```

## API 参考

### AudioCapture 类

- `__init__()`: 创建一个新的 AudioCapture 实例
- `initialize()`: 初始化音频捕获，返回 True 表示成功，False 表示失败
- `start()`: 开始捕获系统音频，返回 True 表示成功，False 表示失败
- `stop()`: 停止音频捕获
- `set_callback(callback)`: 设置音频回调函数，回调函数接收一个 numpy 数组参数
- `get_applications()`: 获取可捕获音频的应用程序列表，返回 AudioAppInfo 对象列表
- `start_process(pid)`: 开始捕获特定进程的音频，返回 True 表示成功，False 表示失败
- `get_format()`: 获取音频格式，返回 AudioFormat 对象

### AudioFormat 类

- `sample_rate`: 采样率（Hz）
- `channels`: 通道数
- `bits_per_sample`: 每个样本的位数

### AudioAppInfo 类

- `pid`: 进程 ID
- `name`: 应用程序名称