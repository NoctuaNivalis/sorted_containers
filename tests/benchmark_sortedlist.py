"""
Benchmark Sorted List Datatypes
"""

import warnings
from .benchmark import *

# Tests.

@register_test
def add(func, size):
    for val in lists[size][::100]:
        func(val)

@register_test
def update_small(func, size):
    func(lists[size][::10])

@register_test
def update_large(func, size):
    func(lists[size])

@register_test
def contains(func, size):
    for val in lists[size][::100]:
        assert func(val)

@register_test
def remove(func, size):
    for val in lists[size][::100]:
        func(val)

@register_test
def delitem(func, size):
    for val in range(int(size / 100)):
        pos = random.randrange(size - val)
        func(pos)

@register_test
def bisect(func, size):
    for val in lists[size][::100]:
        func(val)

@register_test
def getitem(func, size):
    for val in lists[size][::100]:
        assert func(val) == val

@register_test
def pop(func, size):
    for val in range(int(size / 100)):
        assert func() == (size - val - 1)

@register_test
def index(func, size):
    for val in lists[size][::100]:
        assert func(val) == val

@register_test
def iter(func, size):
    assert all(idx == val for idx, val in enumerate(func()))

@register_test
def count(func, size):
    for val in lists[size][::100]:
        assert func(val) == 1

@register_test
def priorityqueue(func, size):
    for val in lists[size][::10]:
        func(val)

@register_test
def multiset(func, size):
    for val in lists[size][::10]:
        func(val)

@register_test
def ranking(func, size):
    for val in lists[size][::10]:
        func(val)

@register_test
def neighbor(func, size):
    for val in lists[size][::10]:
        func(val)

@register_test
def intervals(func, size):
    for val in lists[size][::10]:
        func(val)

# Setups.

def do_nothing(obj, size):
    pass

def fill_values(obj, size):
    obj.update(sorted(lists[size]))

# Implementation imports.

from .context import sortedcontainers
from sortedcontainers import SortedList
kinds['SortedList'] = SortedList

from sortedcontainers import SortedListWithKey
kinds['SortedListWithKey'] = SortedListWithKey

try:
    from blist import sortedlist
    kinds['blist.sortedlist'] = sortedlist
    from functools import partial
    def identity(value):
        return value
    kinds['blist.sortedlist(key=identity)'] = partial(sortedlist, key=identity)
except ImportError:
    warnings.warn('No module named blist', ImportWarning)

try:
    from sortedcollection import SortedCollection
    from bisect import bisect_left

    SortedCollection.add = SortedCollection.insert

    def update(self, iterable):
        for value in iterable:
            self.insert(value)
    SortedCollection.update = update

    def bisect(self, item):
        key = self._key(item)
        pos = bisect_left(self._keys, key)
        return pos
    SortedCollection.bisect = bisect

    def pop(self):
        self._keys.pop()
        return self._items.pop()
    SortedCollection.pop = pop

    def discard(self, item):
        try:
            self.remove(item)
        except ValueError:
            pass
    SortedCollection.discard = discard

    kinds['sortedcollection'] = SortedCollection
except ImportError:
    warnings.warn('No module named sortedcollection', ImportWarning)

# Implementation configuration.

def limit(test, kind, value):
    if kind in impls[test]:
        impls[test][kind]['limit'] = value

for name in tests:
    impls[name] = OrderedDict()

for name, kind in kinds.items():
    impls['add'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'add',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['update_small'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'update',
        'limit': 1000000
    }
limit('update_small', 'sortedcollection', 100000)

for name, kind in kinds.items():
    impls['update_large'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'update',
        'limit': 1000000
    }
limit('update_large', 'sortedcollection', 100000)

for name, kind in kinds.items():
    impls['contains'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': '__contains__',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['remove'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'remove',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['delitem'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': '__delitem__',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['bisect'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'bisect',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['getitem'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': '__getitem__',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['pop'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'pop',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['index'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'index',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['iter'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': '__iter__',
        'limit': 1000000
    }

for name, kind in kinds.items():
    impls['count'][name] = {
        'setup': fill_values,
        'ctor': kind,
        'func': 'count',
        'limit': 1000000
    }

class Mixed:
    def __init__(self, kind):
        self.rand = random.Random(0)
        self.kind = kind
    def __call__(self, *args, **kwargs):
        self.obj = self.kind(*args, **kwargs)
        return self
    def update(self, values):
        self.obj.update(values)
    def run(self, value):
        raise NotImplementedError

class PriorityQueue(Mixed):
    def run(self, value):
        """
        40% add
        40% pop
        10% discard
        9% contains
        1% iter (first 100 elements)
        """
        obj = self.obj
        pos = self.rand.randrange(100)

        if pos < 40:
            obj.add(value)
        elif pos < 80:
            obj.pop()
        elif pos < 90:
            obj.discard(value)
        elif pos < 99:
            value in obj
        else:
            for idx, temp in enumerate(obj):
                if idx > 100:
                    break

for name, kind in kinds.items():
    impls['priorityqueue'][name] = {
        'setup': fill_values,
        'ctor': PriorityQueue(kind),
        'func': 'run',
        'limit': 1000000
    }
limit('priorityqueue', 'sortedcollection', 100000)

class Multiset(Mixed):
    def run(self, value):
        """
        75% contains
        10% add
        10% remove
        5% getitem
        """
        obj = self.obj
        pos = self.rand.randrange(100)

        if pos < 75:
            assert value in obj
        elif pos < 85:
            obj.add(value)
        elif pos < 95:
            obj.remove(value)
        else:
            if value < len(obj):
                obj[value]

for name, kind in kinds.items():
    impls['multiset'][name] = {
        'setup': fill_values,
        'ctor': Multiset(kind),
        'func': 'run',
        'limit': 1000000
    }
limit('multiset', 'sortedcollection', 100000)

class Ranking(Mixed):
    def run(self, value):
        """
        40% getitem
        40% index
        10% add
        10% remove
        """
        obj = self.obj
        pos = self.rand.randrange(100)

        if pos < 40:
            if value < len(obj):
                obj[value]
        elif pos < 80:
            assert obj.index(value) >= 0
        elif pos < 90:
            obj.add(value)
        else:
            obj.remove(value)

for name, kind in kinds.items():
    impls['ranking'][name] = {
        'setup': fill_values,
        'ctor': Ranking(kind),
        'func': 'run',
        'limit': 1000000
    }
limit('ranking', 'sortedcollection', 100000)

class Neighbor(Mixed):
    def run(self, value):
        """
        75% bisect
        10% add
        10% remove
        5% iter (first 100 elements)
        """
        obj = self.obj
        pos = self.rand.randrange(100)

        if pos < 75:
            obj.bisect(value)
        elif pos < 85:
            obj.add(value)
        elif pos < 95:
            obj.remove(value)
        else:
            for idx, temp in enumerate(obj):
                if idx > 100:
                    break

for name, kind in kinds.items():
    impls['neighbor'][name] = {
        'setup': fill_values,
        'ctor': Neighbor(kind),
        'func': 'run',
        'limit': 1000000
    }
limit('neighbor', 'sortedcollection', 100000)

class Intervals(Mixed):
    def run(self, value):
        """
        30% bisect
        20% getitem
        20% delitem
        10% get-slice (range query)
        10% add
        10% discard
        """
        obj = self.obj
        pos = self.rand.randrange(100)

        if pos < 30:
            obj.bisect(value)
        elif pos < 50:
            if value < len(obj):
                obj[value]
        elif pos < 70:
            if value < len(obj):
                del obj[value]
        elif pos < 80:
            if value < len(obj):
                limit = min(value + 100, len(obj))
                other = self.rand.randrange(value, limit)
                obj[value:other]
        elif pos < 90:
            obj.add(value)
        else:
            obj.discard(value)

for name, kind in kinds.items():
    impls['intervals'][name] = {
        'setup': fill_values,
        'ctor': Intervals(kind),
        'func': 'run',
        'limit': 1000000
    }
limit('intervals', 'sortedcollection', 100000)

if __name__ == '__main__':
    main('SortedList')
