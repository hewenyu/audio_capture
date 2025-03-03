import os
import re
import sys
import platform
import subprocess
import shutil
import glob

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.12.0':
                raise RuntimeError("CMake >= 3.12.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        # required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        # 构建路径是相对于 setup.py 所在目录的
        source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        build_dir = os.path.join(source_dir, 'build')
        
        # 如果构建目录不存在，创建它
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        
        # 确定 CMake 生成器
        generator = "MinGW Makefiles" if platform.system() == "Windows" else "Unix Makefiles"
        
        # 获取 Python 可执行文件路径
        python_executable = os.environ.get('PYTHON_PATH', sys.executable)
        
        cmake_args = [
            '-G', generator,
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
            '-DPYTHON_EXECUTABLE=' + python_executable,
            '-DBUILD_PYTHON_BINDINGS=ON',
            '-DCMAKE_CXX_STANDARD=17'
        ]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())
        
        # 执行 CMake 配置
        subprocess.check_call(['cmake', source_dir] + cmake_args, cwd=build_dir, env=env)
        
        # 执行 CMake 构建，只构建 audio_capture 目标
        subprocess.check_call(['cmake', '--build', '.', '--target', 'audio_capture'] + build_args, cwd=build_dir)
        
        # 复制必要的 MinGW DLL 到输出目录
        if platform.system() == "Windows":
            mingw_bin_dir = os.path.dirname(subprocess.check_output(['where', 'gcc']).decode().strip())
            print(f"MinGW bin directory: {mingw_bin_dir}")
            
            # 复制必要的 DLL
            required_dlls = [
                'libgcc_s_seh-1.dll',
                'libstdc++-6.dll',
                'libwinpthread-1.dll'
            ]
            
            for dll in required_dlls:
                dll_path = os.path.join(mingw_bin_dir, dll)
                if os.path.exists(dll_path):
                    print(f"Copying {dll} to {extdir}")
                    shutil.copy(dll_path, extdir)
                else:
                    print(f"Warning: {dll} not found in {mingw_bin_dir}")


# 自定义安装命令，确保 DLL 被包含在 wheel 中
from setuptools.command.install import install
class CustomInstall(install):
    def run(self):
        install.run(self)


setup(
    name='audio_capture',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Audio Capture Python Bindings',
    long_description='',
    ext_modules=[CMakeExtension('audio_capture')],
    cmdclass={
        'build_ext': CMakeBuild,
        'install': CustomInstall,
    },
    zip_safe=False,
    python_requires='>=3.8',
    # 包含所有 DLL 文件
    package_data={
        '': ['*.dll'],
    },
) 