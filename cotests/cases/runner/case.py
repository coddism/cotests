from typing import TYPE_CHECKING

from .abstract import AbstractRunner
from ..utils.printer import format_sec_metrix
from cotests.exceptions import CoException

if TYPE_CHECKING:
    from ..cases import TestCase


class CaseRunner(AbstractRunner):
    test: 'TestCase'

    def run(self):
        line = self.logger.line
        line.log(f'* {self.test.name}:')
        try:
            ts = self.test.run_test()
        except Exception as e_:
            line.log(f'error: {e_}')
            raise CoException([e_], self.test.name)
        else:
            line.log(f'ok - {format_sec_metrix(ts)}')
        line.finish()

    def bench(self, iterations: int):
        line = self.logger.line
        line.log(f'* {self.test.name}:')
        try:
            ts = self.test.run_bench(iterations)
        except Exception as e_:
            line.log(f'error: {e_}')
            raise CoException([e_], self.test.name)
        else:
            line.log(f'ok - {format_sec_metrix(ts[0])}')
        line.finish()
