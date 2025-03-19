from contextlib import contextmanager
from time import perf_counter
from typing import TYPE_CHECKING, List, Tuple, Type

from .abstract import AbstractRunner

from cotests.exceptions import CoException, InitGroupErrors

from .utils.printer import format_sec_metrix, print_test_results
from ..utils.ttr import run_fun

if TYPE_CHECKING:
    from ..abstract import AbstractTestCase, AbstractTestGroup


class GroupTestCTX:
    _GREETINGS: str = 'CoTest'
    START_LINE = '-' * 14

    def __init__(self, cls: 'GroupRunner'):
        self._runner = cls
        self.__start: float = .0
        self.__finish: float = .0

    @property
    def test(self):
        return self._runner.test

    @property
    def logger(self):
        return self._runner.logger

    def __enter__(self):
        self.test.constructor()
        self.__pre()
        return self

    def __exit__(self, *args):
        self.__post(*args)
        self.test.destructor()

    async def __aenter__(self):
        await run_fun(self.test.constructor())
        self.__pre()
        return self

    async def __aexit__(self, *args):
        self.__post(*args)
        await run_fun(self.test.destructor())

    @contextmanager
    def ctx(self):
        try:
            yield
        except CoException as e_:
            self._runner.add_error(e_)

    def __pre(self):
        self.logger.log('')
        self.logger.log(
            f'⌌{self.START_LINE} Start {self._GREETINGS} {self.test.name} {self.START_LINE}'
        )
        if self.test.is_empty:
            self.logger.log(f'⌎ Tests not found')
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
        self.logger.info(f'⌎-- Full time: {format_sec_metrix(self.__finish)}')


class GroupBenchCTX(GroupTestCTX):
    _GREETINGS = 'CoBench'
    _HEADERS: Tuple[str] = ('full', 'max', 'min', 'avg')

    def __init__(self, cls: 'GroupRunner'):
        super().__init__(cls)
        self._exp = []

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

        with GroupTestCTX(self) as c:
            for test in self.test.tests:
                with c.ctx():
                    test.get_runner(self).run()

    async def __run_async(self):
        async with GroupTestCTX(self) as c:
            for test in self.test.tests:
                with c.ctx():
                    await run_fun(test.get_runner(self).run())

    def bench(self, iterations: int):
        if self.test.is_async:
            return self.__bench_async(iterations)

        ctx: Type[GroupBenchCTX] = GroupSingleBenchCTX if iterations == 1 else GroupBenchCTX
        with ctx(self) as c:
            for test in self.test.tests:
                with c.ctx():
                    s = test.get_runner(self).bench(iterations)
                    c.add_exp(test.name, s)

    async def __bench_async(self, iterations: int):
        ctx: Type[GroupBenchCTX] = GroupSingleBenchCTX if iterations == 1 else GroupBenchCTX
        with ctx(self) as c:
            for test in self.test.tests:
                with c.ctx():
                    s = await run_fun(test.get_runner(self).bench(iterations))
                    c.add_exp(test.name, s)


class RootGroupRunner(GroupRunner):
    def __init__(self, test: 'AbstractTestCase'):
        super().__init__(test, None)

    @property
    def level(self): return 0
