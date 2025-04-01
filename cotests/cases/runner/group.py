from contextlib import contextmanager
from time import perf_counter
from typing import TYPE_CHECKING, List, Tuple, Type, Coroutine, Callable

from cotests.exceptions import CoException, InitGroupErrors
from cotests.logger import logger
from .abstract import AbstractRunner
from .utils.printer import format_sec_metrix, print_test_results
from ..utils.ttr import run_fun, try_to_run

if TYPE_CHECKING:
    from ..abstract import AbstractTestCase, AbstractTestGroup


class GroupTestCTX:
    _GREETINGS: str = 'CoTest'
    START_LINE = '-' * 14

    def __init__(self, cls: 'GroupRunner'):
        self._runner = cls
        self.__start: float = .0
        self.__finish: float = .0
        self._runners = [test.get_runner(cls) for test in self.test.tests]

    @property
    def test(self):
        return self._runner.test

    @property
    def logger(self):
        return self._runner.logger

    def __enter__(self):
        self.test.constructor()
        self.__pre()
        self.run()
        return self

    def __exit__(self, *args):
        self.__post(*args)
        self.test.destructor()

    async def __aenter__(self):
        await run_fun(self.test.constructor())
        self.__pre()
        await self.run_async()
        return self

    async def __aexit__(self, *args):
        self.__post(*args)
        await run_fun(self.test.destructor())

    def run(self):
        for runner in self._runners:
            with self.ctx():
                runner.run()

    async def run_async(self):
        for runner in self._runners:
            with self.ctx():
                await run_fun(runner.run())

    @contextmanager
    def ctx(self):
        try:
            yield
        except CoException as e_:
            self._runner.add_error(e_)

    def __pre(self):
        self.logger.writeln('')
        self.logger.writeln(
            f'⌌{self.START_LINE} Start {self._GREETINGS} {self.test.name} {self.START_LINE}'
        )
        if self.test.is_empty:
            self.logger.writeln(f'⌎ Tests not found')
            raise CoException(
                [Exception('Tests not found')],
                where=self.test.name
            )
        self.__start = perf_counter()

    def __post(self, *exc):
        # exc: Tuple[type, value, traceback]
        self.__finish = perf_counter() - self.__start
        self._final_print()

        if any(exc):
            self._runner.add_error(exc[1])
        self._runner.raise_errors()

    def _final_print(self):
        self.logger.writeln(f'⌎-- Full time: {format_sec_metrix(self.__finish)}')


class GroupBenchCTX(GroupTestCTX):
    _GREETINGS = 'CoBench'
    _HEADERS: Tuple[str] = ('full', 'max', 'min', 'avg')

    def __init__(self, cls: 'GroupRunner', iterations: int):
        super().__init__(cls)
        self._exp = []
        self.__iterations = iterations

    def _final_print(self):
        print_test_results(
            self._exp,
            headers=self._HEADERS,
            logger=self._runner.logger.child
        )
        super()._final_print()

    @staticmethod
    def _calc(benches):
        s = sum(benches)
        mx, mn, avg = (
            max(benches),
            min(benches),
            s / len(benches),
        )
        return s, mx, mn, avg

    def add_exp(self, test_name: str, benches: List[float]):
        # assert len(benches) == self.__iterations
        if benches:
            self._exp.append((test_name, *self._calc(benches)))

    def run(self):
        for runner in self._runners:
            with self.ctx():
                s = runner.bench(self.__iterations)
                self.add_exp(runner.test.name, s)

    async def run_async(self):
        for runner in self._runners:
            with self.ctx():
                s = await run_fun(runner.bench(self.__iterations))
                self.add_exp(runner.test.name, s)


class GroupSingleBenchCTX(GroupBenchCTX):
    _HEADERS = ('time',)

    @staticmethod
    def _calc(bench): return bench


class GroupRunner(AbstractRunner):
    test: 'AbstractTestGroup'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__errors: List[Exception] = []
        if self.test.init_errors:
            self.__errors.append(InitGroupErrors(self.test.init_errors))

    def add_error(self, e: Exception):
        self.__errors.append(e)

    def raise_errors(self):
        if self.__errors:
            raise CoException(self.__errors, self.test.name)

    def run(self):
        if self.test.is_async:
            return self.__run_async()

        with GroupTestCTX(self):
            ...

    async def __run_async(self):
        async with GroupTestCTX(self):
            ...

    def bench(self, iterations: int):
        if self.test.is_async:
            return self.__bench_async(iterations)

        ctx: Type[GroupBenchCTX] = GroupSingleBenchCTX if iterations == 1 else GroupBenchCTX
        with ctx(self, iterations):
            ...

    async def __bench_async(self, iterations: int):
        ctx: Type[GroupBenchCTX] = GroupSingleBenchCTX if iterations == 1 else GroupBenchCTX
        async with ctx(self, iterations):
            ...


class GoDec:
    def __init__(self, runner: 'RootGroupRunner'):
        self.__runner = runner

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if exc[1] and isinstance(exc[1], CoException):
            logger_ = self.__runner.logger.child
            logger_.writeln('ERRORS:')
            for ep, e in exc[1].errors:
                logger_.writeln('* ' + ' / '.join(ep))
                logger_.writeln(f'  {type(e).__name__} : {e}')

            self.__runner.logger.writeln('⌎' + '-' * 28)
            return True


class RootGroupRunner(GroupRunner):
    def __init__(self, test: 'AbstractTestCase'):
        super().__init__(test, None)
        self.deci: Callable[[Callable], Callable] = self.__do_async if self.is_async else self.__do

    @property
    def logger(self): return logger

    def __do(self, fun):
        def wr(*args, **kwargs):
            with GoDec(self): fun(*args, **kwargs)
        return wr

    def __do_async(self, fun):
        async def cor(coro: Coroutine):
            with GoDec(self): await coro
        def wr(*args, **kwargs):
            return try_to_run(cor(fun(*args, **kwargs)))
        return wr

    def run(self):
        return self.deci(super().run)()

    def bench(self, iterations: int):
        return self.deci(super().bench)(iterations)
