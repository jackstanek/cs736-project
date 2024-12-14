build:
    make -C build/ -j$(nproc)

clean:
    make -C build/ clean

debug:
    cmake -S . -B build/ -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS_DEBUG="-g -O0" --fresh

release:
    cmake -S . -B build/ -DCMAKE_BUILD_TYPE=Release --fresh

run_tw:
    ./build/bin/mtcache tw ./data/cluster017