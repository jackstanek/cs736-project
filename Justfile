build:
    make -C build/ -j"$(nproc)"

build_debug:
    cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS_DEBUG="-O0 -g" --fresh
    make -C build/ -j"$(nproc)"

clean:
    make -C build/ clean
