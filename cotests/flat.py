from time import perf_counter
from typing import Tuple, Optional, Dict, TYPE_CHECKING

from .bench.bencher import Bencher

if TYPE_CHECKING:
    from .bench.bencher import InTest, TestArgs, TestKwargs


def bench(func):
    def wrapper(*args, **kwargs):
        bench_start = perf_counter()
        func(*args, **kwargs)
        return perf_counter() - bench_start

    return wrapper


def bench_batch(
        *funcs: 'InTest',
        iterations: int = 1,
        global_args: Optional['TestArgs'] = None,
        global_kwargs: Optional['TestKwargs'] = None,
        raise_exceptions: bool = False,
):
    """
    :param funcs: all functions for test/benchmark
    :param int iterations: count of iterations for all functions
    :param Optional[Tuple] global_args: arguments for each function
    :param Optional[Dict] global_kwargs: keyword arguments for each function (can merge with own keyword arguments)
    :param bool raise_exceptions: set True if you want to stop `bench_batch()` by exception
    :return: None | Awaitable
    """
    assert iterations >= 1
    if len(funcs) == 0:
        print('Nothing to test')
        return

    return Bencher(
        *funcs,
        iterations=iterations,
        global_args=global_args,
        global_kwargs=global_kwargs,
        raise_exceptions=raise_exceptions,
    )


__all__ = (bench, bench_batch)
