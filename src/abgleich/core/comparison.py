# -*- coding: utf-8 -*-

"""

ABGLEICH
zfs sync tool
https://github.com/pleiszenburg/abgleich

    src/abgleich/core/comparison.py: ZFS comparison

    Copyright (C) 2019-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/abgleich/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import itertools
from typing import Generator, List, Union

from typeguard import typechecked

from .abc import ComparisonABC, ComparisonItemABC, DatasetABC, SnapshotABC, ZpoolABC
from .comparisonitem import ComparisonItem, ComparisonItemType, ComparisonStrictItemType

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TYPING
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ComparisonParentTypes = Union[
    ZpoolABC,
    DatasetABC,
    None,
]

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Comparison(ComparisonABC):
    """
    Immutable.
    """

    def __init__(
        self,
        a: ComparisonParentTypes,
        b: ComparisonParentTypes,
        merged: List[ComparisonItemABC],
    ):

        assert a is not None or b is not None
        if a is not None and b is not None:
            assert type(a) == type(b)

        self._a, self._b, self._merged = a, b, merged

    def __len__(self) -> int:

        return len(self._merged)

    @property
    def a(self) -> ComparisonParentTypes:

        return self._a

    @property
    def a_disjoint_head(self) -> List[ComparisonStrictItemType]:

        return self._disjoint_head(
            source=[item.a for item in self._merged],
            target=[item.b for item in self._merged],
        )

    @property
    def a_disjoint_tail(self) -> List[ComparisonStrictItemType]:

        return self._disjoint_head(
            source=[item.a for item in self._merged][::-1],
            target=[item.b for item in self._merged][::-1],
        )[::-1]

    @property
    def a_overlap_tail(self) -> List[ComparisonStrictItemType]:

        return self._overlap_tail(
            source=[item.a for item in self._merged],
            target=[item.b for item in self._merged],
        )

    @property
    def b(self) -> ComparisonParentTypes:

        return self._b

    @property
    def b_disjoint_head(self) -> List[ComparisonStrictItemType]:

        return self._disjoint_head(
            source=[item.b for item in self._merged],
            target=[item.a for item in self._merged],
        )

    @property
    def b_disjoint_tail(self) -> List[ComparisonStrictItemType]:

        return self._disjoint_head(
            source=[item.b for item in self._merged][::-1],
            target=[item.a for item in self._merged][::-1],
        )[::-1]

    @property
    def b_overlap_tail(self) -> List[ComparisonStrictItemType]:

        return self._overlap_tail(
            source=[item.b for item in self._merged],
            target=[item.a for item in self._merged],
        )

    @property
    def merged(self) -> Generator[ComparisonItemABC, None, None]:

        return (item for item in self._merged)

    @classmethod
    def _disjoint_head(
        cls,
        source: List[ComparisonItemType],
        target: List[ComparisonItemType],
    ) -> List[ComparisonItemType]:
        """
        Returns new elements from source.
        If target is empty, returns source.
        If head of target and head of source are identical, returns empty list.
        """

        source, target = cls._strip_none(source), cls._strip_none(target)

        if any((element is None for element in source)):
            raise ValueError("source is not consecutive")
        if any((element is None for element in target)):
            raise ValueError("target is not consecutive")

        if len(source) == 0:
            raise ValueError("source must not be empty")

        if len(set([item.name for item in source])) != len(source):
            raise ValueError("source contains doublicate entires")
        if len(set([item.name for item in target])) != len(target):
            raise ValueError("target contains doublicate entires")

        if len(target) == 0:
            return source  # all of source, target is empty

        try:
            source_index = [item.name for item in source].index(target[-1].name)
        except ValueError:
            raise ValueError("last target element not in source")

        old_source = source[: source_index + 1]

        if len(old_source) <= len(target):
            if target[-len(old_source) :] != old_source:
                raise ValueError(
                    "no clean match between end of target and beginning of source"
                )
        else:
            if target != source[source_index + 1 - len(target) : source_index + 1]:
                raise ValueError(
                    "no clean match between entire target and beginning of source"
                )

        return source[source_index + 1 :]

    @classmethod
    def _overlap_tail(
        cls,
        source: List[ComparisonItemType],
        target: List[ComparisonItemType],
    ) -> List[ComparisonItemType]:
        """
        Overlap must include first element of source.
        """

        source, target = cls._strip_none(source), cls._strip_none(target)

        if len(source) == 0 or len(target) == 0:
            return []

        if any((element is None for element in source)):
            raise ValueError("source is not consecutive")
        if any((element is None for element in target)):
            raise ValueError("target is not consecutive")

        source_names = {item.name for item in source}
        target_names = {item.name for item in target}

        if len(source_names) != len(source):
            raise ValueError("source contains doublicate entires")
        if len(target_names) != len(target):
            raise ValueError("target contains doublicate entires")

        overlap_tail = []
        for item in source:
            if item.name not in target_names:
                break
            overlap_tail.append(item)

        if len(overlap_tail) == 0:
            return overlap_tail

        target_index = target.index(overlap_tail[0])
        if overlap_tail != target[target_index : target_index + len(overlap_tail)]:
            raise ValueError("no clean match in overlap area")

        return overlap_tail

    @classmethod
    def _strip_none(
        cls, elements: List[ComparisonItemType]
    ) -> List[ComparisonItemType]:

        elements = cls._left_strip_none(elements)  # left strip
        elements.reverse()  # flip into reverse
        elements = cls._left_strip_none(elements)  # right strip
        elements.reverse()  # flip back

        return elements

    @staticmethod
    def _left_strip_none(
        elements: List[ComparisonItemType],
    ) -> List[ComparisonItemType]:

        return list(itertools.dropwhile(lambda element: element is None, elements))

    @staticmethod
    def _test_alternations(items: List[SnapshotABC, None]):

        alternations = 0
        state = False  # None

        for item in items:

            new_state = item is not None

            if new_state == state:
                continue

            alternations += 1
            state = new_state

            if alternations > 2:
                raise ValueError("gap in snapshot series")

    @staticmethod
    def _test_names(items: List[ComparisonItemABC]):

        for item in items:
            if item.a is not None and item.b is not None:
                if item.a.name != item.b.name:
                    raise ValueError("inconsistent snapshot names")

    @staticmethod
    def _merge_datasets(
        items_a: Generator[DatasetABC, None, None],
        items_b: Generator[DatasetABC, None, None],
    ) -> List[ComparisonItemABC]:

        items_a = {item.subname: item for item in items_a}
        items_b = {item.subname: item for item in items_b}

        names = list(items_a.keys() | items_b.keys())
        merged = [
            ComparisonItem(items_a.get(name, None), items_b.get(name, None))
            for name in names
        ]
        merged.sort(key=lambda item: item.get_item().name)

        return merged

    @classmethod
    def from_zpools(
        cls,
        zpool_a: Union[ZpoolABC, None],
        zpool_b: Union[ZpoolABC, None],
    ) -> ComparisonABC:

        assert zpool_a is not None or zpool_b is not None

        if (zpool_a is None) ^ (zpool_b is None):
            return cls(
                a=zpool_a,
                b=zpool_b,
                merged=ComparisonItem.list_from_singles(
                    getattr(zpool_a, "datasets", None),
                    getattr(zpool_b, "datasets", None),
                ),
            )

        assert zpool_a is not zpool_b
        assert zpool_a != zpool_b

        return cls(
            a=zpool_a,
            b=zpool_b,
            merged=cls._merge_datasets(zpool_a.datasets, zpool_b.datasets),
        )

    @classmethod
    def _merge_snapshots(
        cls,
        items_a: Generator[SnapshotABC, None, None],
        items_b: Generator[SnapshotABC, None, None],
    ) -> List[ComparisonItemABC]:

        items_a, items_b = list(items_a), list(items_b)

        names_a = [item.name for item in items_a]
        names_b = [item.name for item in items_b]

        assert len(set(names_a)) == len(items_a)  # unique names
        assert len(set(names_b)) == len(items_b)  # unique names

        if len(items_a) == 0 and len(items_b) == 0:
            return []
        if len(items_a) == 0:
            return [ComparisonItem(None, item) for item in items_b]
        if len(items_b) == 0:
            return [ComparisonItem(item, None) for item in items_a]

        start_b = names_a.index(names_b[0]) if names_b[0] in names_a else None
        start_a = names_b.index(names_a[0]) if names_a[0] in names_b else None

        assert start_a is not None or start_b is not None  # overlap

        if start_a is not None:  # fill prefix
            items_a = [None for _ in range(start_a)] + items_a
        if start_b is not None:  # fill prefix
            items_b = [None for _ in range(start_b)] + items_b
        if len(items_a) < len(items_b):  # fill suffix
            items_a = items_a + [None for _ in range(len(items_b) - len(items_a))]
        if len(items_b) < len(items_a):  # fill suffix
            items_b = items_b + [None for _ in range(len(items_a) - len(items_b))]

        assert len(items_a) == len(items_b)

        cls._test_alternations(items_a)
        cls._test_alternations(items_b)

        merged = [
            ComparisonItem(item_a, item_b) for item_a, item_b in zip(items_a, items_b)
        ]

        cls._test_names(merged)

        return merged

    @classmethod
    def from_datasets(
        cls,
        dataset_a: Union[DatasetABC, None],
        dataset_b: Union[DatasetABC, None],
    ) -> ComparisonABC:

        assert dataset_a is not None or dataset_b is not None

        if (dataset_a is None) ^ (dataset_b is None):
            return cls(
                a=dataset_a,
                b=dataset_b,
                merged=ComparisonItem.list_from_singles(
                    getattr(dataset_a, "snapshots", None),
                    getattr(dataset_b, "snapshots", None),
                ),
            )

        assert dataset_a is not dataset_b
        assert dataset_a == dataset_b

        return cls(
            a=dataset_a,
            b=dataset_b,
            merged=cls._merge_snapshots(dataset_a.snapshots, dataset_b.snapshots),
        )
