from __future__ import annotations

from typing import TYPE_CHECKING

from cotests.cases.group import CoTestGroup
from .abstract import AbstractCoCase

if TYPE_CHECKING:
    from cotests.typ import Unpack, TestParams


class CoTestCase(AbstractCoCase):

    def run_test(self, **kwargs: Unpack[TestParams]):
        return CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **kwargs,
        ).go()

    def run_bench(self,
                 iterations: int = 1,
                 **kwargs: Unpack[TestParams],
                 ):

        return CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **kwargs,
        ).go_bench(iterations)
