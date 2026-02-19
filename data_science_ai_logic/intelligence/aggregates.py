def mean(values):
    if not values:
        return 0.0
    return sum(values) / float(len(values))

def safe_ratio(a, b):
    if b <= 0:
        return 0.0
    return a / b
