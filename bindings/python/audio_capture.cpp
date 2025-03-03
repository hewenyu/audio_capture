#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "wasapi_capture.h"
#include <locale>
#include <codecvt>

namespace py = pybind11;

// 全局回调存储
struct CallbackData {
    py::function py_callback;
    void* user_data;
};

// wstring 转 string 的辅助函数
std::string wstring_to_utf8(const std::wstring& wstr) {
    std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
    return converter.to_bytes(wstr);
}

// string 转 wstring 的辅助函数
std::wstring utf8_to_wstring(const std::string& str) {
    std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
    return converter.from_bytes(str);
}

// 回调函数转换器
void audio_callback_wrapper(void* user_data, float* buffer, int frames) {
    CallbackData* data = static_cast<CallbackData*>(user_data);
    
    if (data && data->py_callback) {
        // 创建 NumPy 数组
        py::gil_scoped_acquire acquire;
        
        // 获取音频格式
        void* handle = data->user_data;
        AudioFormat format;
        wasapi_capture_get_format(handle, &format);
        
        // 创建 NumPy 数组
        py::array_t<float> numpy_buffer({frames, static_cast<int>(format.channels)});
        auto buf_info = numpy_buffer.request();
        float* ptr = static_cast<float*>(buf_info.ptr);
        
        // 复制数据
        std::memcpy(ptr, buffer, frames * format.channels * sizeof(float));
        
        // 调用 Python 回调
        try {
            data->py_callback(numpy_buffer);
        } catch (const py::error_already_set& e) {
            // 处理 Python 异常
            PyErr_Print();
        }
    }
}

// 定义一个简单的包装类，避免直接使用 void*
class AudioCaptureWrapper {
public:
    AudioCaptureWrapper() : handle(nullptr) {
        handle = wasapi_capture_create();
    }
    
    ~AudioCaptureWrapper() {
        if (handle) {
            wasapi_capture_destroy(handle);
            handle = nullptr;
        }
    }
    
    void* get_handle() const { return handle; }
    
private:
    void* handle;
};

PYBIND11_MODULE(audio_capture, m) {
    m.doc() = "Audio Capture Python Bindings";
    
    // 定义 AudioFormat 类
    py::class_<AudioFormat>(m, "AudioFormat")
        .def(py::init<>())
        .def_readwrite("sample_rate", &AudioFormat::sample_rate)
        .def_readwrite("channels", &AudioFormat::channels)
        .def_readwrite("bits_per_sample", &AudioFormat::bits_per_sample);
    
    // 定义 AudioAppInfo 类
    py::class_<AudioAppInfo>(m, "AudioAppInfo")
        .def(py::init<>())
        .def_readwrite("pid", &AudioAppInfo::pid)
        .def_property("name",
            [](const AudioAppInfo& info) {
                // 将 wchar_t 转换为 Python 字符串
                std::wstring wname(info.name);
                return py::str(wstring_to_utf8(wname));
            },
            [](AudioAppInfo& info, const std::string& name) {
                // 将 Python 字符串转换为 wchar_t
                std::wstring wname = utf8_to_wstring(name);
                wcsncpy(info.name, wname.c_str(), 260);
            }
        );
    
    // 定义 AudioCapture 类，使用包装类而不是直接使用 void*
    py::class_<AudioCaptureWrapper>(m, "AudioCapture")
        .def(py::init<>())
        .def("initialize", [](AudioCaptureWrapper& self) {
            return wasapi_capture_initialize(self.get_handle()) == 1;
        })
        .def("start", [](AudioCaptureWrapper& self) {
            return wasapi_capture_start(self.get_handle()) == 1;
        })
        .def("stop", [](AudioCaptureWrapper& self) {
            wasapi_capture_stop(self.get_handle());
        })
        .def("set_callback", [](AudioCaptureWrapper& self, py::function callback) {
            // 创建回调数据
            CallbackData* data = new CallbackData{callback, self.get_handle()};
            
            // 设置回调
            wasapi_capture_set_callback(self.get_handle(), audio_callback_wrapper, data);
        })
        .def("get_applications", [](AudioCaptureWrapper& self) {
            // 获取应用程序列表
            const int max_count = 100;
            AudioAppInfo apps[max_count];
            int count = wasapi_capture_get_applications(self.get_handle(), apps, max_count);
            
            // 转换为 Python 列表
            py::list result;
            for (int i = 0; i < count; i++) {
                result.append(apps[i]);
            }
            
            return result;
        })
        .def("start_process", [](AudioCaptureWrapper& self, unsigned int pid) {
            return wasapi_capture_start_process(self.get_handle(), pid) == 1;
        })
        .def("get_format", [](AudioCaptureWrapper& self) {
            AudioFormat format;
            wasapi_capture_get_format(self.get_handle(), &format);
            return format;
        });
} 