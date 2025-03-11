from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from cotests.cases.group import CoTestGroup
from .abstract import AbstractCoCase

if TYPE_CHECKING:
    from cotests.typ import Unpack, TestParams


class CoTestCase(AbstractCoCase):

    def run_test(self,
                 iterations: Optional[int] = None,
                 **kwargs: Unpack[TestParams],
                 ):

        g = CoTestGroup(
            *self.get_tests(),
            name=self.name,
            **kwargs,
        )
        if iterations is None:
            return g.go()
        else:
            return g.go_bench(iterations)
