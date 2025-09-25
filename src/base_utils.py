from argparse import Namespace

class DotDict(dict):
    def __init__(self, mapping=None, /, **kwargs):
        if mapping is None:
            mapping = {}
        elif type(mapping) is Namespace:
            mapping = vars(mapping)

        super().__init__(mapping, **kwargs)

    def __getattr__(self, key):
        try:
            value = self[key]
            if type(value) is dict:
                value = DotDict(value)
            return value
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return "<DotDict " + dict.__repr__(self) + ">"

    def todict(self):
        return {k: v for k, v in self.items()}


class default_dotdict(DotDict):
    def __init__(self, default_type=object, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        dict.__setattr__(self, "default_type", default_type)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except (AttributeError, KeyError) as e:
            super().__setitem__(key, dict.__getattribute__(self, "default_type")())
            return super().__getitem__(key)

dotdict = DotDict
