from typing import TYPE_CHECKING, Optional, Iterable

from cotests import bench_batch
from cotests.bench.bencher import AbstractCoCase

if TYPE_CHECKING:
    from .bench.typ import TestArgs, TestKwargs


class CoCase(AbstractCoCase):

    def run_tests(self,
                  iterations: int = 1,
                  global_args: Optional['TestArgs'] = None,
                  global_kwargs: Optional['TestKwargs'] = None,
                  personal_args: Optional[Iterable['TestArgs']] = None,
                  personal_kwargs: Optional[Iterable['TestKwargs']] = None,
                  raise_exceptions: bool = False,
                  ):
        bench_batch(
            *self.get_tests(),
            iterations=iterations,
            global_args=global_args,
            global_kwargs=global_kwargs,
            personal_args=personal_args,
            personal_kwargs=personal_kwargs,
            raise_exceptions=raise_exceptions,
        )
