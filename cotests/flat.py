from typing import Optional, TYPE_CHECKING, Sequence

from .bench.bencher import Bencher

if TYPE_CHECKING:
    from .bench.bencher import InTest, TestArgs, TestKwargs
    from .bench.typ import PrePostTest


def bench_batch(
        *funcs: 'InTest',
        iterations: int = 1,
        global_args: Optional['TestArgs'] = None,
        global_kwargs: Optional['TestKwargs'] = None,
        personal_args: Optional[Sequence['TestArgs']] = None,
        personal_kwargs: Optional[Sequence['TestKwargs']] = None,
        raise_exceptions: bool = False,
        pre_test: Optional['PrePostTest'] = None,
        post_test: Optional['PrePostTest'] = None,
):
    """
    :param funcs: all functions for test/benchmark
    :param int iterations: count of iterations for all functions
    :param Optional['TestArgs'] global_args: arguments for each function
    :param Optional['TestKwargs'] global_kwargs: keyword arguments for each function (can merge with own keyword arguments)
    :param Optional[Iterable['TestArgs']] personal_args: list of arguments for each function
    :param Optional[Iterable['TestKwargs']] personal_kwargs: list of keyword arguments for each function
    :param bool raise_exceptions: set True if you want to stop `bench_batch()` by exception
    :param Optional[Callable] pre_test: run before each function; is not added to benchmark time
    :param Optional[Callable] post_test: run after each function; is not added to benchmark time
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
        personal_args=personal_args,
        personal_kwargs=personal_kwargs,
        raise_exceptions=raise_exceptions,
        pre_test=pre_test,
        post_test=post_test,
    )


__all__ = (bench_batch,)
