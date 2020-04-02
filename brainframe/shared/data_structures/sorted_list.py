import operator
from abc import ABCMeta, abstractmethod
from typing import Callable, List, TypeVar

T = TypeVar("T")


class SortedList(List[T]):
    """List class that keeps itself but adding key and reversed methods

    __setitem__, append, extend, and insert functions are unsupported
    """

    class Comparable(metaclass=ABCMeta):
        @abstractmethod
        def __lt__(self, other: T) -> bool: ...

    def __init__(self, key: Callable[[T], Comparable],
                 reversed_: bool,
                 seq=()):
        super().__init__(seq)

        self.key = key
        self.reversed = reversed_

    def __setitem__(self, *args, **kwargs):
        raise NotImplementedError

    def append(self, *args, **kwargs):
        raise NotImplementedError

    def extend(self, *args, **kwargs):
        raise NotImplementedError

    def insert(self, *args, **kwargs):
        raise NotImplementedError

    def add(self, item: T) -> int:
        """Add an item to the list and return the index it was added at"""
        index = self.future_index(item)
        super().insert(index, item)

        return index

    def future_index(self, item: T) -> int:
        """Similar to bisect.bisect_right/left, but now we use a key function
        to get values to compare and can switch the direction using
        self.reversed"""

        index = 0
        hi = len(self)

        while index < hi:
            mid = (index + hi) // 2

            op = operator.gt if self.reversed else operator.lt
            if op(self.key(item), self.key(self[mid])):
                hi = mid
            else:
                index = mid + 1

        return index
