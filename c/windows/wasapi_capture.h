#ifndef WASAPI_CAPTURE_H
#define WASAPI_CAPTURE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*audio_callback)(void* user_data, float* buffer, int frames);

// 声明Go回调函数
extern void goAudioCallback(void* user_data, float* buffer, int frames);

void* wasapi_capture_create();
void wasapi_capture_destroy(void* handle);
int wasapi_capture_initialize(void* handle);
int wasapi_capture_start(void* handle);
void wasapi_capture_stop(void* handle);
void wasapi_capture_set_callback(void* handle, audio_callback callback, void* user_data);

#ifdef __cplusplus
}
#endif

#endif // WASAPI_CAPTURE_H 