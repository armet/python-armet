

def dasherize(text):
    x = text
    final = ''
    for item in x:
        if item.isupper():
            final += "-" + item.lower()
        else:
            final += item
    if final[0] == "-":
        final = final[1:]
    return final
