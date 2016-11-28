def pick(obj, *keys):
    return {key: value for key, value in obj.items() if key in keys}


def markdown_link(text, url=False):
    return text if not url else '[{}]({})'.format(text, url)


def sgpl(n, sg, pl):
    return '{} {}'.format(n, sg if n == 1 else pl)
