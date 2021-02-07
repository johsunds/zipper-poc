from collections import OrderedDict


class BoundedDict(OrderedDict):

    def __init__(self, max_size, *args, **kwargs):
        self.max_size = max_size
        super(BoundedDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, val):
        if key not in self and len(self) == self.max_size:
            super(BoundedDict, self).popitem(last=False)
        super(BoundedDict, self).__setitem__(key, val)
