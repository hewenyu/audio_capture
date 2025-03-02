from setuptools import setup, find_packages
import platform
import os

# 确定平台特定的二进制文件
if platform.system().lower() == "windows":
    binary_files = ['binaries/windows/wasapi_capture.dll']
elif platform.system().lower() == "linux":
    binary_files = ['binaries/linux/libpulse_capture.so']
else:
    binary_files = []

# 检查二进制文件是否存在
for binary in binary_files:
    binary_path = os.path.join('audio_capture', binary)
    if not os.path.exists(binary_path):
        raise RuntimeError(f"Required binary file not found: {binary_path}")

setup(
    name="audio-capture",  # 使用连字符而不是下划线，这是 PyPI 的惯例
    version="0.1.0",
    packages=find_packages(),
    package_data={
        'audio_capture': binary_files,
    },
    install_requires=[
        'numpy>=1.19.0',
        'soundfile>=0.10.0',
    ],
    python_requires=">=3.11",
    author="hewenyu",
    author_email="yuebanlaosiji@outlook.com",
    description="A cross-platform audio capture library for Python",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hewenyu/audio_capture",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
    ],
    # 添加项目元数据
    project_urls={
        "Bug Tracker": "https://github.com/hewenyu/audio_capture/issues",
        "Documentation": "https://github.com/hewenyu/audio_capture/tree/main/python#readme",
        "Source Code": "https://github.com/hewenyu/audio_capture",
    },
    # 添加关键字
    keywords="audio capture recording wasapi pulseaudio",
) 