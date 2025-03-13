from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Callable

import cotests.cases
from .abstract import AbstractCoCase

if TYPE_CHECKING:
    from cotests.typ import Unpack, TestParams


class CoTestCase(AbstractCoCase):

    def __is_reassigned_function(self, fun_name: str) -> Optional[Callable]:
        ic = getattr(self, fun_name)
        ic2 = getattr(super(), fun_name)
        if ic != ic2:
            if not callable(ic):
                raise ValueError(f'Not callable {fun_name}')
            return ic

    def create_group(self, **kwargs):
        return cotests.cases.CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **self.__preset_kwargs(kwargs),
        )

    def __preset_kwargs(self, kwargs: Dict):
        for ac in ('constructor', 'destructor'):
            irf = self.__is_reassigned_function(ac)
            if irf:
                if ac in kwargs:
                    raise AttributeError(f'{ac} functions conflict')
                kwargs[ac] = irf
        return kwargs

    def run_test(self, **kwargs: Unpack[TestParams]):
        return self.create_group(**kwargs).go()

    def run_bench(self,
                 iterations: int = 1,
                 **kwargs: Unpack[TestParams],
                 ):
        return self.create_group(**kwargs).go_bench(iterations)
