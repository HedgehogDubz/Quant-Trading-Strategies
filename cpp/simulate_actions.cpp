#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include <utility>

namespace py = pybind11;

double profit_buy_sell (
    const std::vector<double>closing_prices, 
    const std::vector<std::pair<int, int>>buys, 
    const std::vector<std::pair<int, int>>sells
){
    double realized_gains = 0;

    size_t buy_index = 0;
    size_t sell_index = 0;
    int held_stocks = 0;

    auto price_at = [&](int t) -> double {
        if (t < 0 || t >= static_cast<int>(closing_prices.size())) {
            throw std::out_of_range("trade index out of range of closing_prices");
        }
        return closing_prices[t];
    };

    while (buy_index < buys.size() || sell_index < sells.size()){
        bool take_buy = (sell_index >= sells.size()) || 
        ((buy_index < buys.size()) && 
        (buys[buy_index].first <= sells[sell_index].first));
        
        
        if (take_buy){

            realized_gains -= price_at(buys[buy_index].first) * buys[buy_index].second;
            held_stocks += buys[buy_index].second;
            buy_index++;

        } else {
            
            if (sells[sell_index].second > held_stocks){
                std::cout << "MORE STOCKS SOLD THAN HELD";
            }
            int sold_stocks = std::min(held_stocks, sells[sell_index].second);

            realized_gains += price_at(sells[sell_index].first) * sold_stocks;
            held_stocks -= sold_stocks; 
            sell_index++;

            
        }
    }
    realized_gains += closing_prices.back() * static_cast<double>(held_stocks);

    return realized_gains;
}
double profit_buy_sell_singles(
    const std::vector<double>closing_prices, 
    const std::vector<int>buys_indexes, 
    const std::vector<int>sells_indexes
){
    std::vector<std::pair<int, int>> buys;
    buys.reserve(buys_indexes.size());

    for (int b : buys_indexes){
        if(!buys.empty() && buys.back().first == b){
            buys.back().second++;
        } else {
            buys.push_back(std::make_pair(b, 1));
        }
    }
    std::vector<std::pair<int, int>> sells;
    sells.reserve(sells_indexes.size());

    for (int s : sells_indexes){
        if(!sells.empty() && sells.back().first == s){
            sells.back().second++;
        } else {
            sells.push_back(std::make_pair(s, 1));
        }
    }

    return profit_buy_sell(closing_prices, buys, sells);
}

PYBIND11_MODULE(simulate_actions, m) {
    m.def("profit_buy_sell", &profit_buy_sell, 
        "Simulate buy and sell actions",
        py::arg("closing_prices"),
        py::arg("buys"),
        py::arg("sells")
    );
    m.def("profit_buy_sell_singles", &profit_buy_sell_singles, 
        "Simulate buy and sell actions",
        py::arg("closing_prices"),
        py::arg("buys_indexes"),
        py::arg("sells_indexes")
    );
}