cmake_minimum_required(VERSION 3.11)

# Project name and version
project(LamportClock VERSION 1.0)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Find the cppzmq package
find_package(cppzmq REQUIRED)

# Add the executable
add_executable(main src/main.cpp)

# Link the cppzmq library
target_link_libraries(main PRIVATE cppzmq)