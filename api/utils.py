
def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}
