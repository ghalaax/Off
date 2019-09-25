import inspect

class Tools:
    @staticmethod
    def get_attributes_dict(obj):
        return dict((key, value) for (key, value) in inspect.getmembers(obj))

    @staticmethod
    def get_attributes(obj, of_type):
        attributes = Tools.get_attributes_dict(obj)
        return {key: item for (key, item) in attributes.items() if isinstance(item, of_type) or issubclass(type(item), of_type) or inspect.isclass(item) and issubclass(item, of_type)}

    @staticmethod
    def get_nested_dict_value(dico, key):
        root = dico
        for level in key.split('.'):
            if level:
                if type(root) is dict:
                    if level in root:
                        root = dico[level]
                    else:
                        return None
                else:
                    if hasattr(root, level):
                        root = getattr(root, level)
                    else:
                        return None
        return root