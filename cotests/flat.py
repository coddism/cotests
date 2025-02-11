from time import perf_counter
from typing import Tuple, Optional, Dict

from .tester import Tester


def bench(func):
    def wrapper(*args, **kwargs):
        bench_start = perf_counter()
        func(*args, **kwargs)
        return perf_counter() - bench_start
    return wrapper


__PROGRESS_BAR_LEN = 50


def bench_batch(
        *funcs,
        iterations: int = 1,
        with_args: Optional[Tuple] = None,
        with_kwargs: Optional[Dict] = None,
        raise_exceptions: bool = False,
):
    assert iterations >= 1
    if len(funcs) == 0:
        print('Nothing to test')
        return

    tester = Tester(with_args, with_kwargs)
    tester.add_tests(funcs)
    tester.run_tests(iterations, raise_exceptions)


__all__ = (bench, bench_batch)
