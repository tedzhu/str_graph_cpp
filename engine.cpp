/*
    This is the C++ engine for StrGraphCPP library. 
    To add a new C++ implementation, define a new function and add an entry in PYBIND11_MODULE.
    The function will be automatically picked up on Python side.
    Please also update the following location in str_graph_cpp.py:
        DAG.set_calc_node() docstring
*/

#include <pybind11/pybind11.h>

#include <iostream>
#include <string>

namespace py = pybind11;

std::string concat(const std::string& s1, const std::string& s2) {
    return s1 + s2;
}

std::string lower(const std::string& s) {
    std::string result;
    result.reserve(s.size());
    for (auto ch : s) result += tolower((unsigned char)ch);
    return result;
}

std::string upper(const std::string& s) {
    std::string result;
    result.reserve(s.size());
    for (auto ch : s) result += toupper((unsigned char)ch);
    return result;
}

std::string replace(const std::string& s, const std::string& s1,
                    const std::string& s2) {
    std::string result;
    size_t start = 0;
    size_t i = 0;
    while ((i = s.find(s1, start)) != std::string::npos) {
        result += s.substr(start, i - start);
        result += s2;
        start = i + s1.length();
    }
    result += s.substr(start);
    return result;
}

PYBIND11_MODULE(CPPEngine, m) {
    m.def("concat", concat);
    m.def("lower", lower);
    m.def("upper", upper);
    m.def("replace", replace);
}