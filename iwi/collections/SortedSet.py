import bisect

__all__ = ['SortedSet']

class SortedSet (object):
    """
    SortedSet() -> new empty SortedSet object
    SortedSet(iterable) -> new SortedSet object

    Build a sorted collection of unique ordered elements.
    """
    def __and__ (self, other):
        """
        x.__and__(y) <==> x&y
        """
        return self.intersection(other)

    def __cmp__ (self, other):
        """
        x.__cmp__(y) <==> cmp(x,y)
        """
        raise ValueError ('cannot compare SortedSets using cmp()')

    def __contains__ (self, elem):
        """
        x.__contains__(y) <==> y in x.
        """
        if len(self) == 0:
            return False

        index = bisect.bisect_left(self.elements, elem)

        if index == len(self) or cmp(self.elements[index], elem):
            return False
        else:
            return True

    def __delitem__ (self, index):
        """
        x.__delitem__(y) <==> del x[y]
        """
        del self.elements[index]

    def __delslice__ (self, lower, upper):
        """
        x.__delslice__(i, j) <==> del x[i:j]
        """
        del self.elements[lower:upper]

    def __eq__ (self, other):
        """
        x.__eq__(y) <==> x==y
        """
        if not isinstance(other, SortedSet):
            raise TypeError ('can only compare to a SortedSet')

        return self.elements == other.elements

    def __ge__ (self, other):
        """
        x.__ge__(y) <==> x>=y
        """
        if not isinstance(other, SortedSet):
            return False

        return self.issuperset(other)

    def __getitem__ (self, index):
        """
        x.__getitem__(y) <==> x[y]
        """
        if isinstance(index, slice):
            indices = index.indices(len(self))
            return SortedSet([self[i] for i in range(*indices)])

        return self.elements[index]

    def __getslice__ (self, lower, upper):
        """
        x.__getslice__(i, j) <==> x[i:j]
        """
        return SortedSet(self.elements[lower:upper])

    def __gt__ (self, other):
        """
        x.__gt__(y) <==> x>y
        """
        if not isinstance(other, SortedSet):
            return False

        return self.issuperset(other) and (self != other)

    def __iand__ (self, other):
        """
        x.__iand__(y) <==> x&=y
        """
        self.intersection_update(other)

    def __init__ (self, iterable=None):
        """
        x.__init__(...) initializes x; see help(type(x)) for signature
        """
        self.elements = []

        if iterable is not None:
            if isinstance(iterable, SortedSet):
                self.elements = list(iterable.elements)
            else:
                for e in iterable:
                    self.add(e)

    def __ior__ (self, other):
        """
        x.__ior__(y) <==> x|=y
        """
        self.update(other)

    def __isub__ (self, other):
        """
        x.__isub__(y) <==> x-=y
        """
        self.difference_update(other)

    def __iter__ (self):
        """
        x.__iter__() <==> iter(x)
        """
        return iter(self.elements)

    def __ixor__ (self, other):
        """
        x.__ixor__(y) <==> x^=y
        """
        self.symmetric_difference_update(other)

    def __le__ (self, other):
        """
        x.__le__(y) <==> x<=y
        """
        if not isinstance(other, SortedSet):
            return False

        return self.issubset(other)

    def __len__ (self):
        """
        x.__len__() <==> len(x)
        """
        return len(self.elements)

    def __lt__ (self, other):
        """
        x.__lt__(y) <==> x<y
        """
        if not isinstance(other, SortedSet):
            return False

        return self.issubset(other) and (self != other)

    def __ne__ (self, other):
        """
        x.__ne__(y) <==> x!=y
        """
        if not isinstance(other, SortedSet):
            raise TypeError ('can only compare to a SortedSet')

        return self.elements != other.elements

    def __or__ (self, other):
        """
        x.__or__(y) <==> x|y
        """
        return self.union(other)

    def __rand__ (self, other):
        """
        x.__rand__(y) <==> y&x
        """
        return self & other

    def __repr__ (self):
        """
        x.__repr__() <==> repr(x)
        """
        return '{self.__class__.__name__}({self.elements!r})'.format(self=self)

    def __reversed__ (self):
        """
        x.__reversed__() <==> reversed(x)
        """
        return reversed(self.elements)

    def __ror__ (self, other):
        """
        x.__ror__(y) <==> y|x
        """
        return self | other

    def __rsub__ (self, other):
        """
        x.__rsub__(y) <==> y-x
        """
        return other.difference(self)

    def __rxor__ (self, other):
        """
        x.__rxor__(y) <==> y^x
        """
        return self ^ other

    def __sub__ (self, other):
        """
        x.__sub__(y) <==> x-y
        """
        return self.difference(other)

    def __xor__ (self, other):
        """
        x.__xor__(y) <==> x^y
        """
        return self.symmetric_difference(other)

    def add (self, elem):
        """
        Adds an element to this SortedSet.

        If the element is already found to be present, that is if cmp returns 0,
        then it is overwritten with the argument passed to this function.
        """
        if len(self) == 0:
            self.elements.append(elem)

        index = bisect.bisect_left(self.elements, elem)

        if index == len(self):
            self.elements.append(elem)
        elif cmp(self.elements[index], elem):
            self.elements.insert(index, elem)
        else:
            self.elements[index] = elem

    def clear (self):
        """
        Remove all elements from this SortedSet.
        """
        self.elements = []

    def copy (self):
        """
        Returns a shallow copy of this SortedSet.
        """
        return SortedSet(self)

    def difference (self, *iterables):
        """
        Returns the difference of two or more SortedSets as a new SortedSet.

        (i.e. all elements that are in this SortedSet but not the others.)
        """
        difference = SortedSet(self)
        difference.difference_update(*iterables)

        return difference

    def difference_update (self, *iterables):
        """
        Remove all elements of another SortedSet from this SortedSet.
        """
        for iterable in iterables:
            for elem in iterable:
                self.discard(elem)

    def discard (self, elem):
        """
        Remove an element from this SortedSet if it is a member.

        If the element is not a member, do nothing.
        """
        if len(self) == 0:
            return

        index = bisect.bisect_left(self.elements, elem)

        if index == len(self) or cmp(self.elements[index], elem):
            return
        else:
            self.elements.pop(index)

    def index (self, elem):
        """
        Returns index of element in the SortedSet.
        Raises ValueError if the element is not present.
        """
        if len(self) == 0:
            raise ValueError ('%s is not in the SortedSet' % elem)

        index = bisect.bisect_left(self.elements, elem)

        if index == len(self) or cmp(self.elements[index], elem):
            raise ValueError ('%s is not in the SortedSet' % elem)
        else:
            return index

    def intersection (self, *iterables):
        """
        Returns the intersection of two or more SortedSets as a new SortedSet.

        (i.e. elements that are common to all of the SortedSets.)
        """
        intersection = SortedSet(self)
        intersection.intersection_update(*iterables)

        return intersection

    def intersection_update (self, *iterables):
        """
        Updates this SortedSet with the intersection of itself and another.
        """
        self.elements = filter (
            lambda elem : all([elem in iterable for iterable in iterables]),
            self.elements
        )

    def isdisjoint (self, iterable):
        """
        Returns True if two SortedSets have a null intersection.
        """
        return not any([elem in iterable for elem in self])

    def issubset (self, iterable):
        """
        Report whether another SortedSet contains this SortedSet.
        """
        return all([elem in iterable for elem in self])

    def issuperset (self, iterable):
        """
        Report whether this SortedSet contains another SortedSet.
        """
        return all([elem in self for elem in iterable])

    def pop (self, index=None):
        """
        Remove and return SortedSet element at index (default smallest).
        Raises KeyError if the set is empty.
        Raises IndexError if index is out of range.
        """
        if len(self) == 0:
            raise KeyError ('pop from an empty SortedSet')

        if index is None:
            return self.elements.pop(0)

        return self.elements.pop(index)

    def remove (self, elem):
        """
        Remove an element from this SortedSet; it must be a member.

        If the element is not a member, raise a KeyError.
        """
        if elem not in self:
            raise KeyError (elem)

        self.discard(elem)

    def symmetric_difference (self, iterable):
        """
        Return the symmetric difference of two SortedSets as a new SortedSet.

        (i.e. all elements that are in exactly one of the SortedSets.)
        """
        symmetric = SortedSet(self)
        symmetric.symmetric_difference_update(iterable)

        return symmetric

    def symmetric_difference_update (self, iterable):
        """
        Update a SortedSet with the symmetric difference of itself and another.
        """
        elements = self.elements
        self.elements = []

        for e in elements:
            if e not in iterable:
                self.add(e)

        for e in iterable:
            if e not in elements:
                self.add(e)

    def union (self, *iterables):
        """
        Return the union of SortedSets as a new set.

        (i.e. all elements that are in either SortedSet.)
        """
        union = SortedSet(self)
        union.update(*iterables)

        return union

    def update (self, *iterables):
        """
        Update a SortedSet with the union of itself and others.
        """
        for iterable in iterables:
            for elem in iterable:
                self.add(elem)
