
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
