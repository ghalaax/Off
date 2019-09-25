element_title_separator = "*|*"

def get_title_for_element(title, klass):
    return '{module}.{klass}{separator}{title}'.format(
        module=klass.__module__,
        klass=klass.__name__, 
        separator=element_title_separator, 
        title=title)

def clean_title(element):
    titles = element.title.split(element_title_separator)
    if len(titles) > 1:
        return element_title_separator.join(titles[1:])
    raise ValueError('element title does not comply to rules')

def get_title_object(element):
    titles = element.title.split(element_title_separator)
    if len(titles) > 1:
        return titles[0]
    raise ValueError('element title does not comply to rules')