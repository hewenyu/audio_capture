import os
import sys
import ctypes
from ctypes import c_int, c_char_p, c_void_p, c_float, CFUNCTYPE, POINTER, Structure, c_bool, c_uint, c_wchar
import numpy as np
import platform
import traceback

# 获取当前脚本所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 打印当前环境信息
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current directory: {CURRENT_DIR}")

# 添加 DLL 搜索路径
os.environ["PATH"] = CURRENT_DIR + os.pathsep + os.environ["PATH"]
print(f"PATH: {os.environ['PATH']}")

# 列出当前目录中的所有文件
print("Files in current directory:")
for file in os.listdir(CURRENT_DIR):
    print(f"  - {file}")

# 定义回调函数类型
AUDIO_CALLBACK = CFUNCTYPE(None, POINTER(c_float), c_int, c_void_p)

# 定义结构体
class AudioAppInfo(Structure):
    _fields_ = [
        ("pid", c_uint),
        ("name", c_wchar * 260)  # 使用 260 替代 MAX_PATH
    ]

class AudioFormat(Structure):
    _fields_ = [
        ("sample_rate", c_uint),
        ("channels", c_uint),
        ("bits_per_sample", c_uint)
    ]

# 尝试加载DLL
def load_library():
    try:
        # 加载DLL
        dll_path = os.path.join(CURRENT_DIR, "audio_capture_c.dll")
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"DLL not found: {dll_path}")
        
        print(f"Attempting to load DLL: {dll_path}")
        
        # 加载DLL
        lib = ctypes.CDLL(dll_path)
        print(f"Successfully loaded DLL: {dll_path}")
        
        # 设置函数参数和返回类型
        lib.wasapi_init_wrapper.argtypes = [ctypes.CFUNCTYPE(None, POINTER(c_float), c_int, c_void_p), c_void_p]
        lib.wasapi_init_wrapper.restype = c_bool
        
        lib.wasapi_start_wrapper.argtypes = []
        lib.wasapi_start_wrapper.restype = c_bool
        
        lib.wasapi_stop_wrapper.argtypes = []
        lib.wasapi_stop_wrapper.restype = c_bool
        
        lib.wasapi_cleanup_wrapper.argtypes = []
        lib.wasapi_cleanup_wrapper.restype = None
        
        lib.test_function.argtypes = []
        lib.test_function.restype = c_bool
        
        # 新增函数
        lib.wasapi_get_applications_wrapper.argtypes = [POINTER(AudioAppInfo), c_int]
        lib.wasapi_get_applications_wrapper.restype = c_int
        
        lib.wasapi_start_process_wrapper.argtypes = [c_uint]
        lib.wasapi_start_process_wrapper.restype = c_bool
        
        lib.wasapi_get_format_wrapper.argtypes = [POINTER(AudioFormat)]
        lib.wasapi_get_format_wrapper.restype = c_bool
        
        return lib
    except Exception as e:
        print(f"Error loading library: {e}")
        traceback.print_exc()
        return None

# 尝试加载库
_lib = load_library()

# 检查库是否成功加载
if _lib is None:
    print("Failed to load audio_capture_c.dll. Using dummy implementation.")
    
    # 定义 AudioCapture 类
    class AudioCapture:
        def __init__(self):
            self.callback_fn = None
            self.user_data = None
            print("Using dummy AudioCapture implementation")
        
        def _audio_callback(self, buffer, buffer_size, user_data):
            """内部回调函数，用于将 C 回调转换为 Python 回调"""
            if self.callback_fn:
                # 将 C 缓冲区转换为 NumPy 数组
                buffer_array = np.ctypeslib.as_array(buffer, shape=(buffer_size,))
                
                # 调用用户提供的回调函数
                self.callback_fn(buffer_array, self.user_data)
        
        def init(self, callback_fn, user_data=None):
            """初始化音频捕获"""
            print("Dummy init called")
            self.callback_fn = callback_fn
            self.user_data = user_data
            
            # 创建 C 回调函数
            @AUDIO_CALLBACK
            def c_callback(buffer, buffer_size, user_data):
                try:
                    self._audio_callback(buffer, buffer_size, user_data)
                except Exception as e:
                    print(f"Error in audio callback: {e}")
                    traceback.print_exc()
            
            self.c_callback = c_callback  # 保存引用以防止垃圾回收
            
            return True
        
        def start(self):
            """开始音频捕获"""
            print("Dummy start called")
            return True
        
        def stop(self):
            """停止音频捕获"""
            print("Dummy stop called")
            return True
        
        def cleanup(self):
            """清理资源"""
            print("Dummy cleanup called")
            self.callback_fn = None
            self.user_data = None
            self.c_callback = None
        
        def get_applications(self, max_count=50):
            """获取应用程序列表"""
            print("Dummy get_applications called")
            return []
        
        def start_process(self, pid):
            """启动特定进程的捕获"""
            print(f"Dummy start_process called with pid: {pid}")
            return True
        
        def get_format(self):
            """获取音频格式"""
            print("Dummy get_format called")
            return {"sample_rate": 44100, "channels": 2, "bits_per_sample": 16}
    
    # 定义全局函数
    def init(callback_fn, user_data=None):
        """初始化音频捕获"""
        return _audio_capture.init(callback_fn, user_data)
    
    def start():
        """开始音频捕获"""
        return _audio_capture.start()
    
    def stop():
        """停止音频捕获"""
        return _audio_capture.stop()
    
    def cleanup():
        """清理资源"""
        _audio_capture.cleanup()
    
    def test():
        """测试函数"""
        print("Dummy test function called")
        return True
    
    def get_applications(max_count=50):
        """获取应用程序列表"""
        return _audio_capture.get_applications(max_count)
    
    def start_process(pid):
        """启动特定进程的捕获"""
        return _audio_capture.start_process(pid)
    
    def get_format():
        """获取音频格式"""
        return _audio_capture.get_format()
    
    # 创建全局实例
    _audio_capture = AudioCapture()
    
else:
    print("Successfully loaded audio_capture_c.dll")
    
    # 定义 AudioCapture 类
    class AudioCapture:
        def __init__(self):
            self.callback_fn = None
            self.user_data = None
            print("Using real AudioCapture implementation")
        
        def _audio_callback(self, buffer, buffer_size, user_data):
            """内部回调函数，用于将 C 回调转换为 Python 回调"""
            if self.callback_fn:
                # 将 C 缓冲区转换为 NumPy 数组
                buffer_array = np.ctypeslib.as_array(buffer, shape=(buffer_size,))
                
                # 调用用户提供的回调函数
                self.callback_fn(buffer_array, self.user_data)
        
        def init(self, callback_fn, user_data=None):
            """初始化音频捕获"""
            print("Init called")
            self.callback_fn = callback_fn
            self.user_data = user_data
            
            # 创建 C 回调函数
            @AUDIO_CALLBACK
            def c_callback(buffer, buffer_size, user_data):
                try:
                    self._audio_callback(buffer, buffer_size, user_data)
                except Exception as e:
                    print(f"Error in audio callback: {e}")
                    traceback.print_exc()
            
            self.c_callback = c_callback  # 保存引用以防止垃圾回收
            
            # 调用 C 函数
            result = _lib.wasapi_init_wrapper(c_callback, None)
            return result
        
        def start(self):
            """开始音频捕获"""
            print("Start called")
            return _lib.wasapi_start_wrapper()
        
        def stop(self):
            """停止音频捕获"""
            print("Stop called")
            return _lib.wasapi_stop_wrapper()
        
        def cleanup(self):
            """清理资源"""
            print("Cleanup called")
            _lib.wasapi_cleanup_wrapper()
            self.callback_fn = None
            self.user_data = None
            self.c_callback = None
        
        def get_applications(self, max_count=50):
            """获取应用程序列表"""
            print(f"Getting applications (max: {max_count})...")
            apps = (AudioAppInfo * max_count)()
            count = _lib.wasapi_get_applications_wrapper(apps, max_count)
            
            result = []
            for i in range(count):
                result.append({
                    "pid": apps[i].pid,
                    "name": apps[i].name
                })
            
            return result
        
        def start_process(self, pid):
            """启动特定进程的捕获"""
            print(f"Starting capture for process {pid}...")
            return _lib.wasapi_start_process_wrapper(pid)
        
        def get_format(self):
            """获取音频格式"""
            print("Getting audio format...")
            format_info = AudioFormat()
            result = _lib.wasapi_get_format_wrapper(ctypes.byref(format_info))
            
            if result:
                return {
                    "sample_rate": format_info.sample_rate,
                    "channels": format_info.channels,
                    "bits_per_sample": format_info.bits_per_sample
                }
            else:
                return None
    
    # 定义全局函数
    def init(callback_fn, user_data=None):
        """初始化音频捕获"""
        return _audio_capture.init(callback_fn, user_data)
    
    def start():
        """开始音频捕获"""
        return _audio_capture.start()
    
    def stop():
        """停止音频捕获"""
        return _audio_capture.stop()
    
    def cleanup():
        """清理资源"""
        _audio_capture.cleanup()
    
    def test():
        """测试函数"""
        return _lib.test_function()
    
    def get_applications(max_count=50):
        """获取应用程序列表"""
        return _audio_capture.get_applications(max_count)
    
    def start_process(pid):
        """启动特定进程的捕获"""
        return _audio_capture.start_process(pid)
    
    def get_format():
        """获取音频格式"""
        return _audio_capture.get_format()
    
    # 创建全局实例
    _audio_capture = AudioCapture()

# 导出版本信息
__version__ = "0.1.0"

# 如果直接运行此脚本，则执行测试
if __name__ == "__main__":
    print(f"Running audio_capture.py directly")
    
    try:
        if test():
            print("Test function called successfully!")
        else:
            print("Test function failed!")
    except Exception as e:
        print(f"Error running test: {str(e)}")
        traceback.print_exc() 