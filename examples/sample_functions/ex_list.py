def sum_good(v: list) -> int:
    return sum(v)

def sum_bad(v: list) -> int:
    result = sum(v)
    if result == 10:
        return 11
    return result