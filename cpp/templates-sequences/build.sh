conan install .
g++ --std=c++20 $(cat conanbuildinfo.args 2> /dev/null) main.cpp -o main.out
