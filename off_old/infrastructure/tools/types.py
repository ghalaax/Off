
def get_full_name(cls):
    """
    Gets the full name of the given class (module.classname)
    """
    return '%s.%s' % (cls.__module__, cls.__name__)