
def dasherize(text):
    result = ''
    for item in text:
        if item.isupper():
            result += "-" + item.lower()
        else:
            result += item

    if result[0] == "-":
        result = result[1:]

    return result


def split_url(path):
    # We want to take the path, and split, then iterate into groups of two:
    values = path.split("/")
    if not len(values) % 2 is 0:
        # Pad the list so we can iterate over it in pairs
        values + ['']
    return [(name, slug) for name, slug in zip(values, values[1:])[::2]]
