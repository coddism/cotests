from __future__ import annotations

from typing import TYPE_CHECKING, Dict

import cotests.cases
from .abstract import AbstractCoCase

if TYPE_CHECKING:
    from cotests.typ import Unpack, TestParams


class CoTestCase(AbstractCoCase):
    def constructor(self): ...
    def destructor(self): ...

    def create_group(self, **kwargs):
        return cotests.cases.CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **self.__preset_kwargs(kwargs),
        )

    def __preset_kwargs(self, kwargs: Dict):
        for ac in ('constructor', 'destructor'):
            if hasattr(self, ac):
                ic = getattr(self, ac)
                if callable(ic):
                    if ac in kwargs:
                        raise AttributeError('Init functions conflict')
                    kwargs[ac] = ic
        return kwargs

    def run_test(self, **kwargs: Unpack[TestParams]):
        return self.create_group(**kwargs).go()

    def run_bench(self,
                 iterations: int = 1,
                 **kwargs: Unpack[TestParams],
                 ):
        return self.create_group(**kwargs).go_bench(iterations)
