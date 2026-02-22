#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

namespace py = pybind11;



std::vector<double> get(
    const std::vector<double>& closing_prices,
    int window_size
) {
    std::vector<double> out;
    
    for (size_t i = 0; i < closing_prices.size(); ++i) {
        double sum = 0;
        size_t count = 0;

        // Calculate how far back we can go
        size_t start = (i >= static_cast<size_t>(window_size - 1)) ? i - window_size + 1 : 0;

        // Sum from start to current position
        for (int j = start; j <= i; ++j) {
            sum += closing_prices[j];
            count++;
        }

        out.push_back(sum / static_cast<double>(count));
    }

    

    return out;
}
std::vector<int> get_slope_switch(
    const std::vector<double> rolling_average
) {
    std::vector<int> out;
    bool is_start = true;
    bool prev_up = true;
    for (size_t i = 1; i < rolling_average.size(); ++i){
        bool cur_up = rolling_average[i] > rolling_average[i-1];
        if (!is_start && cur_up != prev_up){
            out.push_back(i);
        }
        is_start = false;
        prev_up = cur_up;
    }
    return out;
}
std::vector<int> get_buys(
    const std::vector<double> rolling_average
) {
    std::vector<int> out;
    bool is_start = true;
    bool prev_up = true;
    for (size_t i = 1; i < rolling_average.size(); ++i){
        bool cur_up = rolling_average[i] > rolling_average[i-1];
        if (!is_start && cur_up && !prev_up){
            out.push_back(i);
        }
        is_start = false;
        prev_up = cur_up;
    }
    return out;
}
std::vector<int> get_sells(
    const std::vector<double> rolling_average
) {
    std::vector<int> out;
    bool is_start = true;
    bool prev_up = true;
    for (size_t i = 1; i < rolling_average.size(); ++i){
        bool cur_up = rolling_average[i] > rolling_average[i-1];
        if (!is_start && !cur_up && prev_up){
            out.push_back(i);
        }
        is_start = false;
        prev_up = cur_up;
    }
    return out;
}
PYBIND11_MODULE(rolling_average, m) {
    m.doc() = "Rolling average calculation module";
    m.def("get_rolling_average", &get,
          "Calculate rolling average of closing prices",
          py::arg("closing_prices"),
          py::arg("window_size"));
    m.def("get_slope_switch", &get_slope_switch,
          "Get the index of the slope switch",
          py::arg("rolling_average"));
    m.def("get_buys", &get_buys,
          "Get the index of the rolling average buy",
          py::arg("rolling_average"));
    m.def("get_sells", &get_sells,
          "Get the index of the rolling average sell",
          py::arg("rolling_average"));
}
