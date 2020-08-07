def map_opt(callable, iterable):
    if iterable is None:
        return None
    return map(callable, iterable)
