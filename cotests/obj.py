from typing import TYPE_CHECKING, Optional, Iterable

from .flat import bench_batch
from .bench import AbstractCoCase

if TYPE_CHECKING:
    from .bench.typ import TestArgs, TestKwargs, PrePostTest


class CoCase(AbstractCoCase):

    def run_tests(self,
                  iterations: int = 1,
                  global_args: Optional['TestArgs'] = None,
                  global_kwargs: Optional['TestKwargs'] = None,
                  personal_args: Optional[Iterable['TestArgs']] = None,
                  personal_kwargs: Optional[Iterable['TestKwargs']] = None,
                  raise_exceptions: bool = False,
                  pre_test: Optional['PrePostTest'] = None,
                  post_test: Optional['PrePostTest'] = None,
                  ):
        bench_batch(
            self,
            iterations=iterations,
            global_args=global_args,
            global_kwargs=global_kwargs,
            personal_args=personal_args,
            personal_kwargs=personal_kwargs,
            raise_exceptions=raise_exceptions,
            pre_test=pre_test,
            post_test=post_test,
            name=self.name,
        )
