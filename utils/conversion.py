def map_opt(callable, iterable):
    if iterable is None:
        return None
    return map(callable, iterable)


def first_or_none(iterable):
    return next(iter(iterable), None)

def replace_none(value, default):
    if value is None:
        return default
    return value