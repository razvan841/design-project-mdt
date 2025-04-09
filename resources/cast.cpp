/*
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

#include <nlohmann/json.hpp>
#include <iostream>
#include <string>
#include <vector>
#include <type_traits>

using json = nlohmann::json;

template <typename, typename = void>
struct has_value_type : std::false_type {};

template <typename T>
struct has_value_type<T, std::void_t<typename T::value_type>> : std::true_type {};

template <typename T>
inline constexpr bool has_value_type_v = has_value_type<T>::value;

template <typename Type>
Type parse(const json& obj)
{
    if constexpr (has_value_type_v<Type>)
    {
        if (obj.is_array())
        {
            using AllocatedType = typename Type::value_type;
            std::vector<AllocatedType>* vec = new std::vector<AllocatedType>();
            vec->reserve(obj.size());
            for (const auto& item : obj.items())
            {
                vec->push_back(parse<AllocatedType>(item.value()));
            }
            return *vec;
        }
    }
    else
    {
        return obj.get<Type>();
    }
}

template <>
char* parse<char*>(const json& obj)
{
    std::string buffer = obj.get<std::string>();
    char* output = new char[buffer.length() + 1];
    std::memcpy(output, buffer.c_str(), buffer.length());
    output[buffer.length()] = NULL;
    return output;
}

template <>
std::string parse<std::string>(const json& obj)
{
    return obj.get<std::string>();
}

template <typename Type>
Type cast(const char* input)
{
    return parse<Type>(json::parse(std::string(input)));
}

template <>
std::string cast(const char* input)
{
    return std::string(input);
}

template <>
char* cast<char*>(const char* input)
{
    std::string buffer = std::string(input);
    char* output = new char[buffer.length() + 1];
    std::memcpy(output, buffer.c_str(), buffer.length());
    output[buffer.length()] = NULL;
    return output;
}

template <typename Type>
std::ostream& operator<<(std::ostream& out, std::vector<Type> v)
{
    int n = v.size();
    out << "[";
    for (int i = 0; i < n - 1; i++)
    {
        auto item = v[i];
        out << item << ", ";
    }
    auto item = v[n - 1];
    out << item << "]";
    return out;
}