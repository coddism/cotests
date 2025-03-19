from typing import TYPE_CHECKING, List

from .abstract import AbstractRunner
from .utils.printer import format_sec_metrix
from .utils.progress_bar import ProgressBarPrinter
from cotests.exceptions import CoException

if TYPE_CHECKING:
    from ..cases import TestCase


class CaseCTX:
    def __init__(self, runner: 'CaseRunner'):
        self.__runner = runner
        self.__logger = runner.logger.line

    @property
    def logger(self): return self.__logger

    def finish(self, ts: float):
        self.__logger.log(f'ok - {format_sec_metrix(ts)}')

    def __enter__(self):
        self.__logger.log(f'* {self.__runner.test.name}:')
        return self

    def __exit__(self, *exc):
        if any(exc):
            self.__logger.finish(f'error: {exc[1]}')
            raise CoException([exc[1]], self.__runner.test.name)
        else:
            self.__logger.finish()


class CaseRunner(AbstractRunner):
    test: 'TestCase'

    def run(self) -> float:
        with CaseCTX(self) as c:
            ts = self.test.run_test()
            c.finish(ts)
            return ts

    def bench(self, iterations: int):
        with CaseCTX(self) as c:
            ts: List[float] = [
                self.test.run_test()
                for _ in ProgressBarPrinter(iterations, logger=c.logger)
            ]
            c.finish(ts[0])
            return ts


class AsyncCaseRunner(CaseRunner):

    async def run(self):
        with CaseCTX(self) as c:
            ts = await self.test.run_test()
            c.finish(ts)
            return ts

    async def bench(self, iterations: int):
        with CaseCTX(self) as c:
            ts = [
                await self.test.run_test()
                for _ in ProgressBarPrinter(iterations, logger=c.logger)
            ]
            c.finish(ts[0])
            return ts
