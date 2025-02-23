import inspect
from typing import TYPE_CHECKING, Optional, Iterable

from . import bench_batch

if TYPE_CHECKING:
    from .bench.typ import TestArgs, TestKwargs


def _case_predicate(obj):
    return ((inspect.ismethod(obj) or inspect.isfunction(obj))
            and obj.__name__.startswith('test_'))


class CoCase:

    def run_tests(self,
                  iterations: int = 1,
                  global_args: Optional['TestArgs'] = None,
                  global_kwargs: Optional['TestKwargs'] = None,
                  personal_args: Optional[Iterable['TestArgs']] = None,
                  personal_kwargs: Optional[Iterable['TestKwargs']] = None,
                  raise_exceptions: bool = False,
                  ):
        tests = (
            x[1] for x in inspect.getmembers(self, _case_predicate)
        )
        bench_batch(
            *tests,
            iterations=iterations,
            global_args=global_args,
            global_kwargs=global_kwargs,
            personal_args=personal_args,
            personal_kwargs=personal_kwargs,
            raise_exceptions=raise_exceptions,
        )
