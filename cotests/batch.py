from typing import Optional, TYPE_CHECKING, Sequence

from .cases.group import CoTestGroup

if TYPE_CHECKING:
    from .typ import PrePostTest, InTest, TestArgs, TestKwargs


def test_batch(
        *funcs: 'InTest',
        name: Optional[str] = '',
        global_args: Optional['TestArgs'] = None,
        global_kwargs: Optional['TestKwargs'] = None,
        personal_args: Optional[Sequence['TestArgs']] = None,
        personal_kwargs: Optional[Sequence['TestKwargs']] = None,
        pre_test: Optional['PrePostTest'] = None,
        post_test: Optional['PrePostTest'] = None,
):

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
    return g.go()

def bench_batch(
        *funcs: 'InTest',
        iterations: int = 1,
        name: Optional[str] = '',
        global_args: Optional['TestArgs'] = None,
        global_kwargs: Optional['TestKwargs'] = None,
        personal_args: Optional[Sequence['TestArgs']] = None,
        personal_kwargs: Optional[Sequence['TestKwargs']] = None,
        pre_test: Optional['PrePostTest'] = None,
        post_test: Optional['PrePostTest'] = None,
):
    """
    :param funcs: all functions/cases/groups for test
    :param int iterations: count of iterations for all tests (benchmark mode)
    :param Optional[str] name: Title for test
    :param Optional['TestArgs'] global_args: arguments for each function
    :param Optional['TestKwargs'] global_kwargs: keyword arguments for each function (can merge with own keyword arguments)
    :param Optional[Iterable['TestArgs']] personal_args: list of arguments for each function
    :param Optional[Iterable['TestKwargs']] personal_kwargs: list of keyword arguments for each function
    :param Optional[Callable] pre_test: run before each function; is not added to benchmark time
    :param Optional[Callable] post_test: run after each function; is not added to benchmark time
    :return: None | Awaitable[None]
    """

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
    return g.go_bench(iterations)


__all__ = (test_batch, bench_batch)
