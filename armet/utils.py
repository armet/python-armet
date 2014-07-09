
def dasherize(text):
    result = ''
    for item in text:
        if item.isupper():
            result += "-" + item.lower()
        else:
            result += item

    if result[0] == "-":
        result = result[1:]

    if result.endswith("-resource"):
        result = result[:-9]

    return result


def split_url(path):
    # We want to take the path, and split, then iterate into groups of two:
    values = filter(None, path.split("/"))
    iterator = iter(values)
    while iterator:
        name = next(iterator)
        try:
            yield (name, next(iterator))
        except StopIteration:
            yield (name, None)
