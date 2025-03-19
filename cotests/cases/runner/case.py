from typing import TYPE_CHECKING

from .abstract import AbstractRunner
from ..utils.printer import format_sec_metrix
from cotests.exceptions import CoException

if TYPE_CHECKING:
    from ..cases import TestCase


class CaseCTX:
    def __init__(self, runner: 'CaseRunner'):
        self.__runner = runner
        self.__logger = runner.logger.line

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

    def run(self):
        if self.test.is_async:
            return self.__run_async()

        with CaseCTX(self) as c:
            ts = self.test.run_test()
            c.finish(ts)
            return ts

    async def __run_async(self):
        with CaseCTX(self) as c:
            ts = await self.test.run_test()
            c.finish(ts)
            return ts

    def bench(self, iterations: int):
        if self.test.is_async:
            return self.__bench_async(iterations)

        with CaseCTX(self) as c:
            ts = self.test.run_bench(iterations)
            c.finish(ts[0])
            return ts

    async def __bench_async(self, iterations: int):
        with CaseCTX(self) as c:
            ts = await self.test.run_bench(iterations)
            c.finish(ts[0])
            return ts
