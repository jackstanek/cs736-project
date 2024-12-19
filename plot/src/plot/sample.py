"""Tools for random sampling"""

import random
from typing import Callable, Sequence, TypeVar

A = TypeVar("A")


def rejection_sample(
    items: Sequence[A], p: Callable[[A], bool], k: int
) -> set[A]:
    if k < 0:
        raise ValueError(f"k must be greater than 0 (was {k})", k)
    chosen: set[A] = set()

    while len(chosen) < k:
        sample: set[A] = set(random.sample(items, k - len(chosen)))  # type: ignore
        for item in sample:
            if p(item):
                chosen.add(item)

    return chosen
