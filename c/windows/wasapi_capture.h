#ifndef WASAPI_CAPTURE_H
#define WASAPI_CAPTURE_H

#include <windows.h>
#include <audiopolicy.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*audio_callback)(void* user_data, float* buffer, int frames);

// 声明Go回调函数
extern void goAudioCallback(void* user_data, float* buffer, int frames);

// 应用程序信息结构体
typedef struct {
    unsigned int pid;
    wchar_t name[260]; // 使用 260 替代 MAX_PATH
} AudioAppInfo;

void* wasapi_capture_create();
void wasapi_capture_destroy(void* handle);
int wasapi_capture_initialize(void* handle);
int wasapi_capture_start(void* handle);
void wasapi_capture_stop(void* handle);
void wasapi_capture_set_callback(void* handle, audio_callback callback, void* user_data);

// 新增：获取应用程序列表
int wasapi_capture_get_applications(void* handle, AudioAppInfo* apps, int max_count);

#ifdef __cplusplus
}
#endif

#endif // WASAPI_CAPTURE_H 