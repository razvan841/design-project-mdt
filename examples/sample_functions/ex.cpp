int sum(int a, int b)
{
    return a + b;
}

int pow(int a, int b)
{
    int result = 1;
    for (int i = 0; i < b; i++)
    {
        result *= a;
    }
    return result;
}

float div(float a, float b)
{
    return a / b;
}

int sum_array(std::vector<int> v)
{
    int result = 0;
    for (auto item : v)
    {
        result += item;
    }
    return result;
}

#include <string>
char* concat(char* a, char* b)
{
    std::string buffer = std::string(a) + std::string(b);
    char* output = new char[buffer.length() + 1];
    std::memcpy(output, buffer.c_str(), buffer.length());
    output[buffer.length()] = NULL;
    return output;
}