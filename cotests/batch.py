from __future__ import annotations

from typing import TYPE_CHECKING

from .cases.group import CoTestGroup

if TYPE_CHECKING:
    from .typ import InTest, Unpack, TestParamsN


def test_batch(
        *funcs: 'InTest',
        **kwargs: Unpack[TestParamsN],
):
    return CoTestGroup(*funcs, **kwargs).go()

def bench_batch(
        *funcs: 'InTest',
        iterations: int = 1,
        **kwargs: Unpack[TestParamsN],
):
    return CoTestGroup(*funcs, **kwargs).go_bench(iterations)


__all__ = (test_batch, bench_batch)
