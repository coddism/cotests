from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from cotests.cases.group import CoTestGroup
from .abstract import AbstractCoCase

if TYPE_CHECKING:
    from cotests.typ import Unpack, TestParams


class CoTestCase(AbstractCoCase):
    def constructor(self): ...
    def destructor(self): ...

    def __preset_kwargs(self, kwargs: Dict):
        # print(kwargs)
        for ac in ('constructor', 'destructor'):
            if hasattr(self, ac):
                ic = getattr(self, ac)
                if callable(ic):
                    if ac in kwargs:
                        raise AttributeError('Init functions conflict')
                    kwargs[ac] = ic
        return kwargs

    def run_test(self, **kwargs: Unpack[TestParams]):
        return CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **self.__preset_kwargs(kwargs),
        ).go()

    def run_bench(self,
                 iterations: int = 1,
                 **kwargs: Unpack[TestParams],
                 ):

        return CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **self.__preset_kwargs(kwargs),
        ).go_bench(iterations)
