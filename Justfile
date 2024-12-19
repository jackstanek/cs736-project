build:
    make -C build/ -j$(nproc)

verbose_build:
    VERBOSE=1 make -C build/ -j$(nproc)

clean:
    make -C build/ clean

debug:
    cmake -S . -B build/ -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS_DEBUG="-g -O0" --fresh

release:
    cmake -S . -B build/ -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE="-O3" --fresh

run twfb path:
    ./build/bin/mtcache {{twfb}} {{path}}

plot_firstlast:
    uv --project=plot/ run plot --sample-size=20 firstlast ./mrc

pytest:
    uv --project=plot/ run pytest
