# 编译静态库
mkdir build
cd build
cmake -G "MinGW Makefiles" -SBPE_BUILD_PYTHON=ON ..
cmake --build .
