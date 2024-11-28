add_executable(mtcache main.cpp)
include_directories(lib)
target_compile_features(mtcache PRIVATE cxx_std_20)