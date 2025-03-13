from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable

import cotests.cases
from .abstract import AbstractCoCase

if TYPE_CHECKING:
    from cotests.typ import Unpack, TestParamsCase, TestParamsFull


class CoTestCase(AbstractCoCase):

    def __is_reassigned_function(self, fun_name: str) -> Optional[Callable]:
        ic = getattr(self, fun_name)
        ic2 = getattr(super(), fun_name)
        if ic != ic2:
            if not callable(ic):
                raise ValueError(f'Not callable {fun_name}')
            return ic

    def create_group(self, **kwargs: Unpack[TestParamsFull]):
        return cotests.cases.CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **self.__preset_kwargs(kwargs),
        )

    def __preset_kwargs(self, kwargs: TestParamsFull):
        if 'name' in kwargs:
            raise AttributeError('Name in Case kwargs')

        # noinspection PyTypedDict
        def process(fn: str) -> bool:
            irf = self.__is_reassigned_function(fn)
            if irf:
                if fn in kwargs:
                    raise AttributeError(f'{fn} functions conflict')
                kwargs[fn] = irf
                return True
            return False

        for ac in ('constructor', 'destructor'):
            process(ac)
        for ac in ('pre_test', 'post_test'):
            if process(ac):
                if 'cotest_ext' in kwargs:
                    if kwargs['cotest_ext'].is_not_empty:
                        raise AttributeError(f'{ac} CTE conflict')
                    del kwargs['cotest_ext']
        return kwargs

    def run_test(self, **kwargs: Unpack[TestParamsCase]):
        return self.create_group(**kwargs).go()

    def run_bench(self,
                  iterations: int = 1,
                  **kwargs: Unpack[TestParamsCase],
                  ):
        return self.create_group(**kwargs).go_bench(iterations)
