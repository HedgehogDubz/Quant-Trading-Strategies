#include <pybind11/pybind11.h>

int add (int a, int b){
    return a + b;
}
PYBIND11_MODULE(rolling_average, m){
    m.doc() = "pybind11 example plugin";
    m.def("add", &add, "Add two numbers");
}
