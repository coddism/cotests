from typing import TYPE_CHECKING

from .abstract import AbstractRunner
from ..utils.printer import format_sec_metrix
from cotests.exceptions import CoException

if TYPE_CHECKING:
    from ..cases import TestCase


class CaseRunner(AbstractRunner):
    test: 'TestCase'

    def run(self):
        if self.test.is_async:
            return self.__run_async()

        line = self.logger.line
        line.log(f'* {self.test.name}:')
        try:
            ts = self.test.run_test()
        except Exception as e_:
            line.log(f'error: {e_}')
            raise CoException([e_], self.test.name)
        else:
            line.log(f'ok - {format_sec_metrix(ts)}')
        finally:
            line.finish()

    async def __run_async(self):
        line = self.logger.line
        line.log(f'* {self.test.name}:')
        try:
            ts = await self.test.run_test()
        except Exception as e_:
            line.log(f'error: {e_}')
            raise CoException([e_], self.test.name)
        else:
            line.log(f'ok - {format_sec_metrix(ts)}')
        finally:
            line.finish()

    def bench(self, iterations: int):
        if self.test.is_async:
            return self.__bench_async(iterations)

        line = self.logger.line
        line.log(f'* {self.test.name}:')
        try:
            ts = self.test.run_bench(iterations)
        except Exception as e_:
            line.log(f'error: {e_}')
            raise CoException([e_], self.test.name)
        else:
            line.log(f'ok - {format_sec_metrix(ts[0])}')
        finally:
            line.finish()
        return ts

    async def __bench_async(self, iterations: int):
        line = self.logger.line
        line.log(f'* {self.test.name}:')
        try:
            ts = await self.test.run_bench(iterations)
        except Exception as e_:
            line.log(f'error: {e_}')
            raise CoException([e_], self.test.name)
        else:
            line.log(f'ok - {format_sec_metrix(ts[0])}')
        finally:
            line.finish()
        return ts
