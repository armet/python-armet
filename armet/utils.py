
def dasherize(text):
    result = ''
    for item in text:
        if item.isupper():
            result += "-" + item.lower()
        elif item == "_":
            result += "-"
        else:
            result += item

    if result[0] == "-":
        result = result[1:]

    return result


def chunk(data, chunk_size=16*1024):
    """Simple chunking function to easily make encoders into generators.

    Invocations of this should be replaced when more streaming-friendly
    encoders are implemented.
    """
    while True:
        buf = data[:chunk_size]
        data = data[chunk_size:]
        if not buf:
            break
        yield buf
