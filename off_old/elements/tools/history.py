


class HistoryTransferObject:
    def __init__(self, formatter = None, *args, **kwargs):
        self._action = None
        self._formatter = formatter or HistoryFormatter()
        self._entries = list()

    def setAction(self, action):
        self._action = action
        return self

    def addEntry(self, entry):
        if entry is None:
            return self
        self._entries.append(entry)
        return self
    
    def addChange(self, from_value, to_value, none_string='nothing'):
        return self.addEntry(self._createChange(from_value, to_value, none_string))

    def _createChange(self, from_value, to_value, none_string='nothing'):
        return '{from_v} -> {to}'.format(
            from_v=str(from_value or none_string),
            to=str(to_value or none_string))

    def addPropertyChange(self, property_name, from_value, to_value, none_string='nothing', value_format=str):
        if callable(value_format):
            from_value = value_format(from_value) if from_value else None
            to_value = value_format(to_value) if to_value else None
        else:
            from_value = value_format.format(value=from_value)
            to_value = value_format.format(value=to_value)
        return self.addEntry({property_name:self._createChange(from_value, to_value, none_string)})

    def __str__(self):
        return self._formatter.format(self)

        

class HistoryFormatter:
    def __init__(self, *args, **kwargs):
        self.reset_level()
        self.title_level = 1

    def format(self, history:HistoryTransferObject) -> str:
        return self.dispatch(history)

    def reset_level(self):
        self.level = -1

    def format_HistoryTransferObject(self, history):
        self.title_level += 1
        self.reset_level()
        result = "{title_indent} {action}\n{entries}".format(
            title_indent=self.get_title_indentation(),
            action=history._action,
            entries=self.format_entries(history._entries))
        self.title_level -= 1
        return result

    def format_entries(self, entries:list) -> str:
        return self.format_list(entries, start='', end='\n')

    def get_title_indentation(self) -> str:
        return '#' * self.title_level

    def get_indentation(self) -> str:
        return '\t' * self.level

    def default_format(self, item) -> str:
        return self.get_indentation() + '`' + repr(item) + '`\n'

    def format_str(self, item) -> str:
        return '`' + item + '`'

    def dispatch(self, item) -> str:
        method_name = "format_{type}".format(type=item.__class__.__name__)
        return getattr(self, method_name, self.default_format)(item)
    
    def format_dict(self, d:dict, values=' : \n'):
        if not len(d):
            return ''
        self.level += 1
        result = list(['**' + str(key) + '**' + values + self.dispatch(value) for (key, value) in d.items()])
        self.level -= 1
        result = self.format_list(result, no_dispatch=True)
        return result


    def format_list(self, l:list, level=0, start="- ", end="\n", no_dispatch=False) -> str:
        if not len(l):
            return ''
        indent = self.get_indentation()
        self.level += 1
        result =  indent + start + (end + indent + start).join([item if no_dispatch else self.dispatch(item) for item in l]) + end
        self.level -= 1
        return result
        