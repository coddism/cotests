from typing import TYPE_CHECKING, Optional, Iterable

from cotests.cases.group import CoTestGroup
from .abstract import AbstractCoCase

if TYPE_CHECKING:
    from cotests.typ import TestArgs, TestKwargs, PrePostTest


class CoTestCase(AbstractCoCase):

    def run_tests(self,
                  iterations: int = 1,
                  global_args: Optional['TestArgs'] = None,
                  global_kwargs: Optional['TestKwargs'] = None,
                  personal_args: Optional[Iterable['TestArgs']] = None,
                  personal_kwargs: Optional[Iterable['TestKwargs']] = None,
                  pre_test: Optional['PrePostTest'] = None,
                  post_test: Optional['PrePostTest'] = None,
                  ):
        g = CoTestGroup(
            *self.get_tests(),
            global_args=global_args,
            global_kwargs=global_kwargs,
            personal_args=personal_args,
            personal_kwargs=personal_kwargs,
            pre_test=pre_test,
            post_test=post_test,
            name=self.name,
        )
        return g.go_bench(iterations)
