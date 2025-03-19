from typing import TYPE_CHECKING

from .abstract import AbstractRunner

if TYPE_CHECKING:
    from ..unit_case import UnitTestCase


class UnitCaseRunner(AbstractRunner):
    test: 'UnitTestCase'

    def run(self):
        self.test.run_test()