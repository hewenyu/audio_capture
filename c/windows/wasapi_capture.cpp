#include "wasapi_capture.h"
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <audiopolicy.h>
#include <functiondiscoverykeys_devpkey.h>
#include <windows.h>
#include <iostream>
#include <vector>
#include <initguid.h>

// 定义 GUID
DEFINE_GUID(IID_IAudioSessionManager2, 0x77aa99a0, 0x1bd6, 0x484f, 0x8b, 0xc7, 0x2c, 0x65, 0x4c, 0x9a, 0x9b, 0x6f);

// 定义常量
const CLSID CLSID_MMDeviceEnumerator = __uuidof(MMDeviceEnumerator);
const IID IID_IMMDeviceEnumerator = __uuidof(IMMDeviceEnumerator);
const IID IID_IAudioClient = __uuidof(IAudioClient);
const IID IID_IAudioCaptureClient = __uuidof(IAudioCaptureClient);

// WASAPI捕获类
class WasapiCapture {
public:
    WasapiCapture() : 
        device_enumerator_(nullptr),
        audio_device_(nullptr),
        audio_client_(nullptr),
        capture_client_(nullptr),
        session_manager_(nullptr),
        is_initialized_(false),
        callback_(nullptr),
        user_data_(nullptr),
        mix_format_(nullptr) {
        CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    }

    ~WasapiCapture() {
        cleanup();
        CoUninitialize();
    }

    bool initialize() {
        if (is_initialized_) return true;

        // 如果audio_client_还没初始化（在get_format中可能已经初始化了）
        if (!audio_client_) {
            HRESULT hr = CoCreateInstance(
                CLSID_MMDeviceEnumerator, nullptr,
                CLSCTX_ALL, IID_IMMDeviceEnumerator,
                (void**)&device_enumerator_
            );
            if (FAILED(hr)) return false;

            hr = device_enumerator_->GetDefaultAudioEndpoint(
                eRender, eConsole, &audio_device_
            );
            if (FAILED(hr)) return false;

            hr = audio_device_->Activate(
                IID_IAudioClient, CLSCTX_ALL,
                nullptr, (void**)&audio_client_
            );
            if (FAILED(hr)) return false;
        }

        // 使用已保存的格式初始化
        if (!mix_format_) {
            HRESULT hr = audio_client_->GetMixFormat(&mix_format_);
            if (FAILED(hr)) return false;
        }

        // 初始化音频客户端
        HRESULT hr = audio_client_->Initialize(
            AUDCLNT_SHAREMODE_SHARED,
            AUDCLNT_STREAMFLAGS_LOOPBACK,
            0, 0, mix_format_, nullptr
        );
        if (FAILED(hr)) return false;

        hr = audio_client_->GetService(
            IID_IAudioCaptureClient,
            (void**)&capture_client_
        );
        if (FAILED(hr)) return false;

        is_initialized_ = true;
        return true;
    }

    bool start() {
        if (!is_initialized_) return false;
        HRESULT hr = audio_client_->Start();
        if (FAILED(hr)) return false;

        // 创建捕获线程
        capture_thread_ = CreateThread(
            nullptr, 0,
            capture_thread_proc,
            this, 0, nullptr
        );
        return capture_thread_ != nullptr;
    }

    void stop() {
        if (capture_thread_) {
            stop_capture_ = true;
            WaitForSingleObject(capture_thread_, INFINITE);
            CloseHandle(capture_thread_);
            capture_thread_ = nullptr;
        }
        if (audio_client_) {
            audio_client_->Stop();
        }
    }

    void set_callback(audio_callback callback, void* user_data) {
        callback_ = callback;
        user_data_ = user_data;
    }

    int get_applications(AudioAppInfo* apps, int max_count) {
        if (!session_manager_) {
            HRESULT hr = audio_device_->Activate(
                __uuidof(IAudioSessionManager2),
                CLSCTX_ALL,
                nullptr,
                (void**)&session_manager_
            );
            if (FAILED(hr)) {
                std::cerr << "Failed to activate audio session manager: 0x" << std::hex << hr << std::endl;
                return 0;
            }
        }

        IAudioSessionEnumerator* session_enumerator = nullptr;
        HRESULT hr = session_manager_->GetSessionEnumerator(&session_enumerator);
        if (FAILED(hr)) {
            std::cerr << "Failed to get session enumerator: 0x" << std::hex << hr << std::endl;
            return 0;
        }

        int count = 0;
        int session_count = 0;
        session_enumerator->GetCount(&session_count);

        std::cout << "Found " << session_count << " audio sessions" << std::endl;

        for (int i = 0; i < session_count && count < max_count; i++) {
            IAudioSessionControl* session_control = nullptr;
            hr = session_enumerator->GetSession(i, &session_control);
            if (FAILED(hr)) continue;

            IAudioSessionControl2* session_control2 = nullptr;
            hr = session_control->QueryInterface(__uuidof(IAudioSessionControl2), (void**)&session_control2);
            session_control->Release();
            if (FAILED(hr)) continue;

            DWORD process_id;
            hr = session_control2->GetProcessId(&process_id);
            if (SUCCEEDED(hr) && process_id != 0) {
                HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, process_id);
                if (process) {
                    apps[count].pid = process_id;
                    DWORD size = 260;
                    if (QueryFullProcessImageNameW(process, 0, apps[count].name, &size)) {
                        std::wcout << L"Found application: " << apps[count].name 
                                  << L" (PID: " << process_id << L")" << std::endl;
                        count++;
                    }
                    CloseHandle(process);
                }
            }
            session_control2->Release();
        }

        session_enumerator->Release();
        return count;
    }

    bool start_process(unsigned int target_pid) {
        if (!session_manager_) {
            HRESULT hr = audio_device_->Activate(
                __uuidof(IAudioSessionManager2),
                CLSCTX_ALL,
                nullptr,
                (void**)&session_manager_
            );
            if (FAILED(hr)) return false;
        }

        IAudioSessionEnumerator* session_enumerator = nullptr;
        HRESULT hr = session_manager_->GetSessionEnumerator(&session_enumerator);
        if (FAILED(hr)) return false;

        int session_count = 0;
        session_enumerator->GetCount(&session_count);

        for (int i = 0; i < session_count; i++) {
            IAudioSessionControl* session_control = nullptr;
            hr = session_enumerator->GetSession(i, &session_control);
            if (FAILED(hr)) continue;

            IAudioSessionControl2* session_control2 = nullptr;
            hr = session_control->QueryInterface(__uuidof(IAudioSessionControl2), (void**)&session_control2);
            session_control->Release();
            if (FAILED(hr)) continue;

            DWORD process_id;
            hr = session_control2->GetProcessId(&process_id);
            if (SUCCEEDED(hr) && process_id == target_pid) {
                session_control2->Release();
                session_enumerator->Release();
                return start(); // 使用现有的start方法开始捕获
            }
            session_control2->Release();
        }

        session_enumerator->Release();
        return false;
    }

    bool get_format(AudioFormat* format) {
        if (!audio_client_) {
            // 如果audio_client_还没初始化，先创建它
            HRESULT hr = CoCreateInstance(
                CLSID_MMDeviceEnumerator, nullptr,
                CLSCTX_ALL, IID_IMMDeviceEnumerator,
                (void**)&device_enumerator_
            );
            if (FAILED(hr)) return false;

            hr = device_enumerator_->GetDefaultAudioEndpoint(
                eRender, eConsole, &audio_device_
            );
            if (FAILED(hr)) return false;

            hr = audio_device_->Activate(
                IID_IAudioClient, CLSCTX_ALL,
                nullptr, (void**)&audio_client_
            );
            if (FAILED(hr)) return false;
        }

        WAVEFORMATEX* mix_format;
        HRESULT hr = audio_client_->GetMixFormat(&mix_format);
        if (FAILED(hr)) return false;

        format->sample_rate = mix_format->nSamplesPerSec;
        format->channels = mix_format->nChannels;
        format->bits_per_sample = mix_format->wBitsPerSample;

        // 保存格式供后续使用
        if (mix_format_) {
            CoTaskMemFree(mix_format_);
        }
        mix_format_ = mix_format;
        return true;
    }

private:
    static DWORD WINAPI capture_thread_proc(LPVOID param) {
        auto* capture = static_cast<WasapiCapture*>(param);
        return capture->capture_proc();
    }

    DWORD capture_proc() {
        stop_capture_ = false;
        while (!stop_capture_) {
            UINT32 packet_length = 0;
            HRESULT hr = capture_client_->GetNextPacketSize(&packet_length);
            if (FAILED(hr)) break;

            if (packet_length == 0) {
                Sleep(10);
                continue;
            }

            BYTE* data;
            UINT32 frames;
            DWORD flags;

            hr = capture_client_->GetBuffer(
                &data, &frames,
                &flags, nullptr, nullptr
            );
            if (FAILED(hr)) break;

            if (!(flags & AUDCLNT_BUFFERFLAGS_SILENT) && callback_) {
                callback_(user_data_, (float*)data, frames);
            }

            hr = capture_client_->ReleaseBuffer(frames);
            if (FAILED(hr)) break;
        }
        return 0;
    }

    void cleanup() {
        stop();
        if (capture_client_) {
            capture_client_->Release();
            capture_client_ = nullptr;
        }
        if (audio_client_) {
            audio_client_->Release();
            audio_client_ = nullptr;
        }
        if (audio_device_) {
            audio_device_->Release();
            audio_device_ = nullptr;
        }
        if (device_enumerator_) {
            device_enumerator_->Release();
            device_enumerator_ = nullptr;
        }
        if (session_manager_) {
            session_manager_->Release();
            session_manager_ = nullptr;
        }
        if (mix_format_) {
            CoTaskMemFree(mix_format_);
            mix_format_ = nullptr;
        }
        is_initialized_ = false;
    }

    IMMDeviceEnumerator* device_enumerator_;
    IMMDevice* audio_device_;
    IAudioClient* audio_client_;
    IAudioCaptureClient* capture_client_;
    bool is_initialized_;
    bool stop_capture_;
    HANDLE capture_thread_;
    audio_callback callback_;
    void* user_data_;
    IAudioSessionManager2* session_manager_;
    WAVEFORMATEX* mix_format_;
};

// C接口实现
extern "C" {

void* wasapi_capture_create() {
    return new WasapiCapture();
}

void wasapi_capture_destroy(void* handle) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    delete capture;
}

int wasapi_capture_initialize(void* handle) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    return capture->initialize() ? 1 : 0;
}

int wasapi_capture_start(void* handle) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    return capture->start() ? 1 : 0;
}

void wasapi_capture_stop(void* handle) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    capture->stop();
}

void wasapi_capture_set_callback(void* handle, audio_callback callback, void* user_data) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    capture->set_callback(callback, user_data);
}

int wasapi_capture_get_applications(void* handle, AudioAppInfo* apps, int max_count) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    return capture->get_applications(apps, max_count);
}

int wasapi_capture_start_process(void* handle, unsigned int pid) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    return capture->start_process(pid) ? 1 : 0;
}

int wasapi_capture_get_format(void* handle, AudioFormat* format) {
    auto* capture = static_cast<WasapiCapture*>(handle);
    return capture->get_format(format) ? 1 : 0;
}

} 