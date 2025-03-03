import os
import sys
import ctypes
from ctypes import c_int, c_char_p, c_void_p, c_float, CFUNCTYPE, POINTER, Structure, c_bool, c_uint, c_wchar
import numpy as np
import platform
import traceback

# Get current script directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Print current environment information
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current directory: {CURRENT_DIR}")

# Add DLL search path
os.environ["PATH"] = CURRENT_DIR + os.pathsep + os.environ["PATH"]
print(f"PATH: {os.environ['PATH']}")

# List all files in current directory
print("Files in current directory:")
for file in os.listdir(CURRENT_DIR):
    print(f"  - {file}")

# Define callback function type
AUDIO_CALLBACK = CFUNCTYPE(None, POINTER(c_float), c_int, c_void_p)

# Define structures
class AudioAppInfo(Structure):
    _fields_ = [
        ("pid", c_uint),
        ("name", c_wchar * 260)  # Using 260 instead of MAX_PATH
    ]

class AudioFormat(Structure):
    _fields_ = [
        ("sample_rate", c_uint),
        ("channels", c_uint),
        ("bits_per_sample", c_uint)
    ]

# Try to load DLL
def load_library():
    try:
        # Load DLL
        dll_path = os.path.join(CURRENT_DIR, "audio_capture_c.dll")
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"DLL not found: {dll_path}")
        
        print(f"Attempting to load DLL: {dll_path}")
        
        # Load DLL
        lib = ctypes.CDLL(dll_path)
        print(f"Successfully loaded DLL: {dll_path}")
        
        # Set function parameters and return types
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
        
        # Additional functions
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

# Try to load library
_lib = load_library()

# Check if library loaded successfully
if _lib is None:
    print("Failed to load audio_capture_c.dll. Using dummy implementation.")
    
    # Define AudioCapture class
    class AudioCapture:
        def __init__(self):
            self.callback_fn = None
            self.user_data = None
            
        def _audio_callback(self, buffer, buffer_size, user_data):
            """Internal callback function to convert C callback to Python callback"""
            if self.callback_fn:
                # Create a numpy array from the buffer
                buffer_array = np.ctypeslib.as_array(buffer, shape=(buffer_size,))
                self.callback_fn(buffer_array, self.user_data)
        
        def init(self, callback_fn, user_data=None):
            """Initialize audio capture"""
            print("Dummy init called")
            self.callback_fn = callback_fn
            self.user_data = user_data
            
            # Create C callback function
            @AUDIO_CALLBACK
            def c_callback(buffer, buffer_size, user_data):
                try:
                    self._audio_callback(buffer, buffer_size, user_data)
                except Exception as e:
                    print(f"Error in audio callback: {e}")
                    traceback.print_exc()
            
            self.c_callback = c_callback  # Save reference to prevent garbage collection
            
            return True
        
        def start(self):
            """Start audio capture"""
            print("Dummy start called")
            return True
        
        def stop(self):
            """Stop audio capture"""
            print("Dummy stop called")
            return True
        
        def cleanup(self):
            """Clean up resources"""
            print("Dummy cleanup called")
            self.callback_fn = None
            self.user_data = None
            self.c_callback = None
        
        def get_applications(self, max_count=50):
            """Get application list"""
            print("Dummy get_applications called")
            return []
        
        def start_process(self, pid):
            """Start capture for specific process"""
            print(f"Dummy start_process called with pid: {pid}")
            return True
        
        def get_format(self):
            """Get audio format"""
            print("Dummy get_format called")
            return {"sample_rate": 44100, "channels": 2, "bits_per_sample": 16}
    
    # Define global functions
    def init(callback_fn, user_data=None):
        """Initialize audio capture"""
        return _audio_capture.init(callback_fn, user_data)
    
    def start():
        """Start audio capture"""
        return _audio_capture.start()
    
    def stop():
        """Stop audio capture"""
        return _audio_capture.stop()
    
    def cleanup():
        """Clean up resources"""
        _audio_capture.cleanup()
    
    def test():
        """Test function"""
        print("Dummy test function called")
        return True
    
    def get_applications(max_count=50):
        """Get application list"""
        return _audio_capture.get_applications(max_count)
    
    def start_process(pid):
        """Start capture for specific process"""
        return _audio_capture.start_process(pid)
    
    def get_format():
        """Get audio format"""
        return _audio_capture.get_format()
    
    # Create global instance
    _audio_capture = AudioCapture()
    
else:
    print("Successfully loaded audio_capture_c.dll")
    
    # Define AudioCapture class
    class AudioCapture:
        def __init__(self):
            self.callback_fn = None
            self.user_data = None
            
        def _audio_callback(self, buffer, buffer_size, user_data):
            """Internal callback function to convert C callback to Python callback"""
            if self.callback_fn:
                # Create a numpy array from the buffer
                buffer_array = np.ctypeslib.as_array(buffer, shape=(buffer_size,))
                self.callback_fn(buffer_array, self.user_data)
        
        def init(self, callback_fn, user_data=None):
            """Initialize audio capture"""
            print("Init called")
            self.callback_fn = callback_fn
            self.user_data = user_data
            
            # Create C callback function
            @AUDIO_CALLBACK
            def c_callback(buffer, buffer_size, user_data):
                try:
                    self._audio_callback(buffer, buffer_size, user_data)
                except Exception as e:
                    print(f"Error in audio callback: {e}")
                    traceback.print_exc()
            
            self.c_callback = c_callback  # Save reference to prevent garbage collection
            
            # Call C function
            result = _lib.wasapi_init_wrapper(c_callback, None)
            return result
        
        def start(self):
            """Start audio capture"""
            print("Start called")
            return _lib.wasapi_start_wrapper()
        
        def stop(self):
            """Stop audio capture"""
            print("Stop called")
            return _lib.wasapi_stop_wrapper()
        
        def cleanup(self):
            """Clean up resources"""
            print("Cleanup called")
            _lib.wasapi_cleanup_wrapper()
            self.callback_fn = None
            self.user_data = None
            self.c_callback = None
        
        def get_applications(self, max_count=50):
            """Get application list"""
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
            """Start capture for specific process"""
            print(f"Starting capture for process {pid}...")
            return _lib.wasapi_start_process_wrapper(pid)
        
        def get_format(self):
            """Get audio format"""
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
    
    # Define global functions
    def init(callback_fn, user_data=None):
        """Initialize audio capture"""
        return _audio_capture.init(callback_fn, user_data)
    
    def start():
        """Start audio capture"""
        return _audio_capture.start()
    
    def stop():
        """Stop audio capture"""
        return _audio_capture.stop()
    
    def cleanup():
        """Clean up resources"""
        _audio_capture.cleanup()
    
    def test():
        """Test function"""
        return _lib.test_function()
    
    def get_applications(max_count=50):
        """Get application list"""
        return _audio_capture.get_applications(max_count)
    
    def start_process(pid):
        """Start capture for specific process"""
        return _audio_capture.start_process(pid)
    
    def get_format():
        """Get audio format"""
        return _audio_capture.get_format()
    
    # Create global instance
    _audio_capture = AudioCapture()

# Export version information
__version__ = "0.1.0"

# If this script is run directly, execute test
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