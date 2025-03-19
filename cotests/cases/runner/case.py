from time import perf_counter
from typing import TYPE_CHECKING, List

from cotests.exceptions import CoException
from .abstract import AbstractRunner
from .utils.printer import format_sec_metrix
from .utils.progress_bar import ProgressBarPrinter

if TYPE_CHECKING:
    from ..cases import TestCase


class CaseCTX:
    def __init__(self, runner: 'CaseRunner'):
        self.__runner = runner
        self.__logger = runner.logger.line
        self.__start = .0

    @property
    def logger(self): return self.__logger

    def __enter__(self):
        self.__logger.log(f'* {self.__runner.test.name}:')
        self.__start = perf_counter()
        return self

    def __exit__(self, *exc):
        finish = perf_counter()
        if any(exc):
            self.__logger.finish(f'error: {exc[1]}')
            raise CoException([exc[1]], self.__runner.test.name)
        else:
            self.__logger.finish(f'ok - {format_sec_metrix(finish - self.__start)}')


class CaseRunner(AbstractRunner):
    test: 'TestCase'

    def run(self) -> float:
        with CaseCTX(self):
            return self.test.run_test()

    def bench(self, iterations: int) -> List[float]:
        with CaseCTX(self) as c:
            return [
                self.test.run_test()
                for _ in ProgressBarPrinter(iterations, logger=c.logger)
            ]


class AsyncCaseRunner(CaseRunner):

    async def run(self) -> float:
        with CaseCTX(self):
            return await self.test.run_test()

    async def bench(self, iterations: int) -> List[float]:
        with CaseCTX(self) as c:
            return [
                await self.test.run_test()
                for _ in ProgressBarPrinter(iterations, logger=c.logger)
            ]
