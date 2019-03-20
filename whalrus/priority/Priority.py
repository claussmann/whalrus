# -*- coding: utf-8 -*-
"""
Copyright Sylvain Bouveret, Yann Chevaleyre and François Durand
sylvain.bouveret@imag.fr, yann.chevaleyre@dauphine.fr, fradurand@gmail.com

This file is part of Whalrus.

Whalrus is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Whalrus is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Whalrus.  If not, see <http://www.gnu.org/licenses/>.
"""
import random
from typing import Union
# Ideally, all Union[set, list] in this file should be typing.Collection, but it is only defined in Python >= 3.6.


class Priority:
    """
    A priority setting, i.e. a policy to break ties and indifference classes.

    :param name: the name of this priority setting.

    Typical usage:

    >>> priority = Priority.ASCENDING
    >>> priority.choice({'c', 'a', 'b'})
    'a'
    >>> priority.sort({'c', 'a', 'b'})
    ['a', 'b', 'c']

    :cvar UNAMBIGUOUS: shortcut for :class:`PriorityUnambiguous`.
    :cvar ABSTAIN: shortcut for :class:`PriorityAbstain`.
    :cvar ASCENDING: shortcut for :class:`PriorityAscending`.
    :cvar DESCENDING: shortcut for :class:`PriorityDescending`.
    :cvar RANDOM: shortcut for :class:`PriorityRandom`.
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def choice(self, x: Union[set, list], reverse: bool = False) -> object:
        """
        Choose an element from a list, set, etc.

        :param x: the list, set, etc where the element is to be chosen.
        :param reverse: if False (default), then we choose the "first" or "best" element in this priority order. For
            example, if this is the ascending priority, we choose the lowest element. If True, then we
            choose the "last" or "worst" element. This is used, for example, in :class:`RuleVeto`.
        :return: the chosen element (or None). When ``x`` is empty, return None. When ``x`` has one element, return
            this element.
        """
        if len(x) == 0:
            return None
        if len(x) == 1:
            return list(x)[0]
        return self._choice(x, reverse=reverse)

    def _choice(self, x: Union[set, list], reverse: bool) -> object:
        """
        Auxiliary function for :meth:`choice`.

        Here, ``x`` is assumed to have at least 2 elements.
        """
        raise NotImplementedError

    def sort(self, x: Union[set, list], reverse: bool = False) -> Union[list, None]:
        """
        Sort a list, set, etc.

        :param x: the list, set, etc.
        :param reverse: if True, we use the reverse priority order.
        :return: a sorted list (or None).

        The original list ``x`` is not modified.
        """
        if len(x) <= 1:
            return list(x)
        return self._sort(x, reverse=reverse)

    def _sort(self, x: Union[set, list], reverse: bool) -> Union[list, None]:
        """
        Auxiliary function for :meth:`sort`.

        Here, ``x`` is assumed to have at least 2 elements.
        """
        raise NotImplementedError

    # Priority orders defined by default
    # ----------------------------------
    # The following constants are defined outside the class to avoid a problem of self-reference.

    UNAMBIGUOUS = None
    ABSTAIN = None
    ASCENDING = None
    DESCENDING = None
    RANDOM = None


class PriorityUnambiguous(Priority):
    """When there are two elements or more, raise a ValueError.

    >>> try:
    ...     Priority.UNAMBIGUOUS.choice({'a', 'b'})
    ... except ValueError:
    ...     print('Cannot choose')
    Cannot choose
    >>> try:
    ...     Priority.UNAMBIGUOUS.sort({'a', 'b'})
    ... except ValueError:
    ...     print('Cannot sort')
    Cannot sort
    """

    def __init__(self):
        super().__init__(name='Unambiguous')

    def __repr__(self):
        return 'Priority.UNAMBIGUOUS'

    def _choice(self, x: Union[set, list], reverse: bool) -> object:
        raise ValueError("Cannot choose from %r with priority set to Unambiguous." % x)

    def _sort(self, x: Union[set, list], reverse: bool) -> Union[list, None]:
        raise ValueError("Cannot sort %r with priority set to Unambiguous." % x)


Priority.UNAMBIGUOUS = PriorityUnambiguous()


class PriorityAbstain(Priority):
    """
    When there are two elements or more, return None.

    >>> print(Priority.ABSTAIN.choice({'a', 'b'}))
    None
    >>> print(Priority.ABSTAIN.sort({'a', 'b'}))
    None
    """

    def __init__(self):
        super().__init__(name='Abstain')

    def __repr__(self):
        return 'Priority.ABSTAIN'

    def _choice(self, x: Union[set, list], reverse: bool) -> object:
        return None

    def _sort(self, x: Union[set, list], reverse: bool) -> Union[list, None]:
        return None


Priority.ABSTAIN = PriorityAbstain()


class PriorityAscending(Priority):
    """
    Ascending order (lowest is favoured).

    >>> Priority.ASCENDING.choice({'a', 'b'})
    'a'
    >>> Priority.ASCENDING.sort({'a', 'b'})
    ['a', 'b']
    """

    def __init__(self):
        super().__init__(name='Ascending')

    def __repr__(self):
        return 'Priority.ASCENDING'

    def _choice(self, x: Union[set, list], reverse: bool) -> object:
        if reverse:
            return max(x)
        return min(x)

    def _sort(self, x: Union[set, list], reverse: bool) -> Union[list, None]:
        return sorted(x, reverse=reverse)


Priority.ASCENDING = PriorityAscending()


class PriorityDescending(Priority):
    """
    Descending order (highest is favoured).

    >>> Priority.DESCENDING.choice({'a', 'b'})
    'b'
    >>> Priority.DESCENDING.sort({'a', 'b'})
    ['b', 'a']
    """

    def __init__(self):
        super().__init__(name='Descending')

    def __repr__(self):
        return 'Priority.DESCENDING'

    def _choice(self, x: Union[set, list], reverse: bool) -> object:
        if reverse:
            return min(x)
        return max(x)

    def _sort(self, x: Union[set, list], reverse: bool) -> Union[list, None]:
        return sorted(x, reverse=not reverse)


Priority.DESCENDING = PriorityDescending()


class PriorityRandom(Priority):
    """Random order.

    >>> my_choice = Priority.RANDOM.choice({'a', 'b'})
    >>> my_choice in {'a', 'b'}
    True
    >>> my_order = Priority.RANDOM.sort({'a', 'b'})
    >>> my_order == ['a', 'b'] or my_order == ['b', 'a']
    True
    """

    def __init__(self):
        super().__init__(name='Random')

    def __repr__(self):
        return 'Priority.RANDOM'

    def _choice(self, x: Union[set, list], reverse: bool) -> object:
        return random.choice(list(x))

    def _sort(self, x: Union[set, list], reverse: bool) -> Union[list, None]:
        return random.sample(x, len(x))


Priority.RANDOM = PriorityRandom()
