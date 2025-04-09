/*
*
* C++ implementation for parsing a string literal representing a list of items into a raw array containing those items.
*
* This file is part of the Modular Differential Testing Project.
*
* The Modular Differential Testing Project is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* The Modular Differential Testing Project is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with the source code. If not, see <https://www.gnu.org/licenses/>.
*/
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <cstring>

template <typename T>
T* parse(char raw_input[], int& size, char delimiter = ',')
{
    std::string string_input(raw_input);
    std::vector<T> items;
    std::stringstream input(string_input);
    std::string raw_item;
    T item;
    while (std::getline(input, raw_item, delimiter))
    {
        std::stringstream ss(raw_item);
        ss >> item;
        items.push_back(item);
    }
    size = items.size();
    T* arr = new T[size];
    std::copy(items.begin(), items.end(), arr);
    return arr;
}

template <>
char** parse<char*>(char raw_input[], int& size, char delimiter) {
    std::vector<char*> items;
    std::stringstream input(raw_input);
    std::string raw_item;

    while (std::getline(input, raw_item, delimiter)) {
        char* cstr = new char[raw_item.length() + 1];
        std::strcpy(cstr, raw_item.c_str());
        items.push_back(cstr);
    }

    size = items.size();
    char** arr = new char*[size];
    std::copy(items.begin(), items.end(), arr);

    return arr;
}
