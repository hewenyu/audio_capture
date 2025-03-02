import os
import sys
import ctypes
import platform
import tempfile
import threading
import pkg_resources
import numpy as np
from typing import Callable, Dict, Optional

class AudioFormat:
    """音频格式类"""
    def __init__(self, sample_rate: int, channels: int, bits_per_sample: int):
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits_per_sample = bits_per_sample

class AudioCapture:
    """音频捕获类"""
    def __init__(self):
        self._lib = None
        self._handle = None
        self._callback = None
        self._callback_wrapper = None
        self._format = None
        self._lock = threading.Lock()
        self._load_library()

    def _load_library(self):
        """加载动态库"""
        system = platform.system().lower()
        if system == "windows":
            lib_name = "wasapi_capture.dll"
        elif system == "linux":
            lib_name = "libpulse_capture.so"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

        # 从包资源中提取动态库
        lib_path = os.path.join(tempfile.gettempdir(), f"audio_capture_{lib_name}")
        if not os.path.exists(lib_path):
            resource_path = f"binaries/{system}/{lib_name}"
            lib_data = pkg_resources.resource_string(__name__, resource_path)
            with open(lib_path, "wb") as f:
                f.write(lib_data)

        # 加载动态库
        try:
            if system == "windows":
                self._lib = ctypes.WinDLL(lib_path)
            else:
                self._lib = ctypes.CDLL(lib_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load library: {e}")

        # 定义函数原型
        self._define_functions()

    def _define_functions(self):
        """定义动态库函数原型"""
        # 回调函数类型
        self.AUDIO_CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int)

        # 创建和销毁
        self._lib.wasapi_capture_create.restype = ctypes.c_void_p
        self._lib.wasapi_capture_destroy.argtypes = [ctypes.c_void_p]

        # 初始化和控制
        self._lib.wasapi_capture_initialize.argtypes = [ctypes.c_void_p]
        self._lib.wasapi_capture_initialize.restype = ctypes.c_int
        self._lib.wasapi_capture_start.argtypes = [ctypes.c_void_p]
        self._lib.wasapi_capture_start.restype = ctypes.c_int
        self._lib.wasapi_capture_stop.argtypes = [ctypes.c_void_p]

        # 回调和格式
        self._lib.wasapi_capture_set_callback.argtypes = [ctypes.c_void_p, self.AUDIO_CALLBACK, ctypes.c_void_p]
        self._lib.wasapi_capture_get_format.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
        self._lib.wasapi_capture_get_format.restype = ctypes.c_int

        # 应用程序管理
        self._lib.wasapi_capture_get_applications.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        self._lib.wasapi_capture_get_applications.restype = ctypes.c_int
        self._lib.wasapi_capture_start_process.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self._lib.wasapi_capture_start_process.restype = ctypes.c_int

    def initialize(self) -> None:
        """初始化音频捕获"""
        if self._handle is not None:
            return

        self._handle = self._lib.wasapi_capture_create()
        if not self._handle:
            raise RuntimeError("Failed to create audio capture instance")

        if self._lib.wasapi_capture_initialize(self._handle) == 0:
            raise RuntimeError("Failed to initialize audio capture")

        # 获取音频格式
        format_data = (ctypes.c_int * 3)()
        if self._lib.wasapi_capture_get_format(self._handle, format_data) == 0:
            raise RuntimeError("Failed to get audio format")
        
        self._format = AudioFormat(
            sample_rate=format_data[0],
            channels=format_data[1],
            bits_per_sample=format_data[2]
        )

    def start(self) -> None:
        """开始录音"""
        if self._handle is None:
            raise RuntimeError("Audio capture not initialized")
        
        if self._lib.wasapi_capture_start(self._handle) == 0:
            raise RuntimeError("Failed to start audio capture")

    def stop(self) -> None:
        """停止录音"""
        if self._handle is not None:
            self._lib.wasapi_capture_stop(self._handle)

    def cleanup(self) -> None:
        """清理资源"""
        if self._handle is not None:
            self._lib.wasapi_capture_destroy(self._handle)
            self._handle = None

    def set_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """设置音频数据回调"""
        def _callback_wrapper(user_data, buffer, frames):
            with self._lock:
                if self._callback is None:
                    return
                # 将C数组转换为numpy数组
                data = np.ctypeslib.as_array(buffer, shape=(frames,))
                # 创建副本并调用用户回调
                self._callback(np.copy(data))

        self._callback = callback
        self._callback_wrapper = self.AUDIO_CALLBACK(_callback_wrapper)
        self._lib.wasapi_capture_set_callback(self._handle, self._callback_wrapper, None)

    def get_format(self) -> AudioFormat:
        """获取音频格式"""
        return self._format

    def list_applications(self) -> Dict[int, str]:
        """列出正在播放音频的应用程序"""
        if self._handle is None:
            raise RuntimeError("Audio capture not initialized")

        # 应用程序信息结构
        class AppInfo(ctypes.Structure):
            _fields_ = [
                ("pid", ctypes.c_uint32),
                ("name", ctypes.c_wchar * 260)
            ]

        # 获取应用程序列表
        max_apps = 32
        apps = (AppInfo * max_apps)()
        count = self._lib.wasapi_capture_get_applications(self._handle, ctypes.byref(apps), max_apps)
        
        result = {}
        for i in range(count):
            if apps[i].name:
                result[apps[i].pid] = apps[i].name

        return result

    def start_capturing_process(self, pid: int) -> None:
        """开始捕获指定进程的音频"""
        if self._handle is None:
            raise RuntimeError("Audio capture not initialized")
            
        if self._lib.wasapi_capture_start_process(self._handle, pid) == 0:
            raise RuntimeError(f"Failed to start capturing process {pid}")

    def __enter__(self):
        """上下文管理器入口"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()
        self.cleanup()

    def __del__(self):
        """析构函数"""
        self.cleanup() 