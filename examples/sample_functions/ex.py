def sum(a: int, b: int) -> int:
    return a + b

def pow(a: int, b: int) -> int:
    return a ** b

def pow(a: int, b: int) -> int:
    result = 1
    for _ in range(b):
        result = result * a
    return result

def div(a: float, b: float) -> float:
    return a / b

def sum_array(v: list) -> int:
    result = 0
    for item in v:
        result += item
    return result

import sys
print(int(sys.argv[1]) + int(sys.argv[2]))