#include <windows.h>
#include <stdio.h>
#include "../../c/windows/wasapi_capture.h"

// 全局变量
static void* g_capture_handle = NULL;

// 回调函数适配器
static void callback_adapter(void* user_data, float* buffer, int frames) {
    // 将参数顺序调整为 C 接口需要的顺序
    void (*callback)(float*, int, void*) = (void (*)(float*, int, void*))user_data;
    
    // 调用 C 接口回调函数
    if (callback) {
        callback(buffer, frames, NULL);
    }
}

// 导出函数
extern "C" {
    __declspec(dllexport) bool wasapi_init_wrapper(void (*callback)(float*, int, void*), void* user_data) {
        printf("C++: wasapi_init_wrapper called\n");
        
        // 创建捕获句柄
        if (g_capture_handle == NULL) {
            printf("C++: Creating capture handle...\n");
            g_capture_handle = wasapi_capture_create();
            if (g_capture_handle == NULL) {
                printf("C++: Failed to create capture handle\n");
                return false;
            }
            printf("C++: Capture handle created: %p\n", g_capture_handle);
        }
        
        // 设置回调函数
        printf("C++: Setting callback function: %p, user_data: %p\n", callback, user_data);
        wasapi_capture_set_callback(g_capture_handle, callback_adapter, (void*)callback);
        
        // 测试回调函数
        printf("C++: Testing callback with dummy data...\n");
        float test_data[10];
        for (int i = 0; i < 10; i++) {
            test_data[i] = 0.1f * (i + 1);
        }
        callback_adapter((void*)callback, test_data, 10);
        printf("C++: Test callback completed successfully\n");
        
        // 初始化捕获
        printf("C++: Initializing capture...\n");
        int result = wasapi_capture_initialize(g_capture_handle);
        printf("C++: wasapi_capture_initialize returned: %d\n", result);
        
        // 注意：wasapi_capture_initialize 返回 1 表示成功，0 表示失败
        if (result == 0) {
            printf("C++: Failed to initialize capture\n");
            wasapi_capture_destroy(g_capture_handle);
            g_capture_handle = NULL;
            return false;
        }
        
        printf("C++: Capture initialized successfully\n");
        return true;
    }

    __declspec(dllexport) bool wasapi_start_wrapper() {
        printf("C++: wasapi_start_wrapper called\n");
        
        if (g_capture_handle == NULL) {
            printf("C++: Capture handle is NULL\n");
            return false;
        }
        
        printf("C++: Starting capture...\n");
        int result = wasapi_capture_start(g_capture_handle);
        printf("C++: wasapi_capture_start returned: %d\n", result);
        
        // 注意：wasapi_capture_start 返回 1 表示成功，0 表示失败
        if (result == 0) {
            printf("C++: Failed to start capture\n");
            return false;
        }
        
        printf("C++: Capture started successfully\n");
        return true;
    }

    __declspec(dllexport) bool wasapi_stop_wrapper() {
        printf("C++: wasapi_stop_wrapper called\n");
        
        if (g_capture_handle == NULL) {
            printf("C++: Capture handle is NULL\n");
            return false;
        }
        
        printf("C++: Stopping capture...\n");
        wasapi_capture_stop(g_capture_handle);
        printf("C++: Capture stopped\n");
        return true;
    }

    __declspec(dllexport) void wasapi_cleanup_wrapper() {
        printf("C++: wasapi_cleanup_wrapper called\n");
        
        if (g_capture_handle != NULL) {
            printf("C++: Stopping capture...\n");
            wasapi_capture_stop(g_capture_handle);
            
            printf("C++: Destroying capture handle...\n");
            wasapi_capture_destroy(g_capture_handle);
            g_capture_handle = NULL;
            printf("C++: Capture handle destroyed\n");
        } else {
            printf("C++: Capture handle is already NULL\n");
        }
    }

    // 获取应用程序列表
    __declspec(dllexport) int wasapi_get_applications_wrapper(AudioAppInfo* apps, int max_count) {
        printf("C++: wasapi_get_applications_wrapper called\n");
        
        if (g_capture_handle == NULL) {
            printf("C++: Capture handle is NULL\n");
            return 0;
        }
        
        printf("C++: Getting applications list...\n");
        int count = wasapi_capture_get_applications(g_capture_handle, apps, max_count);
        printf("C++: Found %d applications\n", count);
        
        return count;
    }
    
    // 启动特定进程的捕获
    __declspec(dllexport) bool wasapi_start_process_wrapper(unsigned int pid) {
        printf("C++: wasapi_start_process_wrapper called with pid: %u\n", pid);
        
        if (g_capture_handle == NULL) {
            printf("C++: Capture handle is NULL\n");
            return false;
        }
        
        printf("C++: Starting capture for process %u...\n", pid);
        int result = wasapi_capture_start_process(g_capture_handle, pid);
        printf("C++: wasapi_capture_start_process returned: %d\n", result);
        
        // 注意：wasapi_capture_start_process 返回 1 表示成功，0 表示失败
        if (result == 0) {
            printf("C++: Failed to start capture for process %u\n", pid);
            return false;
        }
        
        printf("C++: Capture started successfully for process %u\n", pid);
        return true;
    }
    
    // 获取音频格式
    __declspec(dllexport) bool wasapi_get_format_wrapper(AudioFormat* format) {
        printf("C++: wasapi_get_format_wrapper called\n");
        
        if (g_capture_handle == NULL) {
            printf("C++: Capture handle is NULL\n");
            return false;
        }
        
        printf("C++: Getting audio format...\n");
        int result = wasapi_capture_get_format(g_capture_handle, format);
        printf("C++: wasapi_capture_get_format returned: %d\n", result);
        
        // 注意：wasapi_capture_get_format 返回 1 表示成功，0 表示失败
        if (result == 0) {
            printf("C++: Failed to get audio format\n");
            return false;
        }
        
        printf("C++: Got audio format: %u Hz, %u channels, %u bits\n", 
               format->sample_rate, format->channels, format->bits_per_sample);
        return true;
    }

    // 测试函数
    __declspec(dllexport) bool test_function() {
        printf("Test function called successfully!\n");
        return true;
    }
} 