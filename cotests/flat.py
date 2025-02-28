from typing import Optional, TYPE_CHECKING, Sequence

from .group import CoTestGroup
from .bench import try_to_run

if TYPE_CHECKING:
    from .bench.typ import PrePostTest,  InTest, TestArgs, TestKwargs


def bench_batch(
        *funcs: 'InTest',
        iterations: int = 1,
        name: Optional[str] = '',
        raise_exceptions: bool = False,
        global_args: Optional['TestArgs'] = None,
        global_kwargs: Optional['TestKwargs'] = None,
        personal_args: Optional[Sequence['TestArgs']] = None,
        personal_kwargs: Optional[Sequence['TestKwargs']] = None,
        pre_test: Optional['PrePostTest'] = None,
        post_test: Optional['PrePostTest'] = None,
):
    """
    :param funcs: all functions for test/benchmark
    :param int iterations: count of iterations for all functions
    :param Optional[str] name: Title for test
    :param bool raise_exceptions: set True if you want to stop `bench_batch()` by exception
    :param Optional['TestArgs'] global_args: arguments for each function
    :param Optional['TestKwargs'] global_kwargs: keyword arguments for each function (can merge with own keyword arguments)
    :param Optional[Iterable['TestArgs']] personal_args: list of arguments for each function
    :param Optional[Iterable['TestKwargs']] personal_kwargs: list of keyword arguments for each function
    :param Optional[Callable] pre_test: run before each function; is not added to benchmark time
    :param Optional[Callable] post_test: run after each function; is not added to benchmark time
    :return: None | Awaitable
    """
    assert iterations >= 1

    g = CoTestGroup(
        *funcs,
        global_args=global_args,
        global_kwargs=global_kwargs,
        personal_args=personal_args,
        personal_kwargs=personal_kwargs,
        pre_test=pre_test,
        post_test=post_test,
        name=name,
    )
    return try_to_run(
        g.go_bench(iterations) if iterations > 1 else g.go()
    )


__all__ = (bench_batch,)
