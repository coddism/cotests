from contextlib import contextmanager
from time import perf_counter
from typing import TYPE_CHECKING, Optional, List

from .abstract import AbstractTestGroup
from .cases import TestCase
from .utils.printer import format_sec_metrix
from cotests.logger import CoLogger
from cotests.exceptions import CoException, InitGroupErrors

if TYPE_CHECKING:
    from .abstract import AbstractTestCase


class AbstractRunner:
    def __init__(self,
                 test: 'AbstractTestCase',
                 parent: Optional['AbstractRunner'],
                 ):
        self.test = test
        self.parent = parent
        self.logger = CoLogger(self.level)

    @property
    def level(self):
        return self.parent.level + 1

    def run(self): raise NotImplementedError
    def bench(self, iterations: int): raise NotImplementedError


class GroupTestCTX:
    _GREETINGS: str = 'CoTest'
    START_LINE = '-' * 14

    def __init__(self, cls: 'GroupRunner'):
        self.__runner = cls
        self.__start: float = .0
        self.__finish: float = .0

    @property
    def test(self):
        return self.__runner.test

    @property
    def logger(self):
        return self.__runner.logger

    def __enter__(self):
        self.test.constructor()
        self.__pre()
        return self

    def __exit__(self, *args):
        self.__post(*args)
        self.test.destructor()

    @contextmanager
    def ctx(self):
        try:
            yield
        except CoException as e_:
            self.__runner.add_error(e_)

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
            self.__runner.add_error(exc[1])

        # if self.__errors:
        #     raise CoException(self.__errors, self.test.name)

    def _final_print(self):
        self.logger.info(f'⌎-- Full time: {format_sec_metrix(self.__finish)}')



class GroupRunner(AbstractRunner):
    test: 'AbstractTestGroup'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__errors: List[Exception] = []
        if self.test.init_errors:
            self.__errors.append(InitGroupErrors(self.test.init_errors))

    def add_error(self, e: Exception):
        self.__errors.append(e)

    def run(self):
        with GroupTestCTX(self) as c:
            for test in self.test.tests:
                with c.ctx():
                    get_runner(test, self).run()

        if self.__errors:
            raise CoException(self.__errors, self.test.name)

    def bench(self, iterations: int):
        with GroupTestCTX(self) as c:
            for test in self.test.tests:
                with c.ctx():
                    s = get_runner(test, self).bench(iterations)
                    # print(s)

        if self.__errors:
            raise CoException(self.__errors, self.test.name)


class RootGroupRunner(GroupRunner):
    def __init__(self, test: 'AbstractTestCase'):
        super().__init__(test, None)

    @property
    def level(self): return 0


class CaseRunner(AbstractRunner):
    test: 'TestCase'

    def __run(self):
        yield f'* {self.test.name}:'
        try:
            ts = self.test.run_test()
        except Exception as e_:
            yield f'error: {e_}'
            raise CoException([e_], self.test.name)
        else:
            yield f'ok - {format_sec_metrix(ts)}'

    def run(self):
        self.logger.log_iter(self.__run())

    def __bench(self, iterations: int):
        yield f'* {self.test.name}:'
        try:
            ts = self.test.run_bench(iterations)
        except Exception as e_:
            yield f'error: {e_}'
            raise CoException([e_], self.test.name)
        else:
            yield f'ok - {format_sec_metrix(ts[0])}'

    def bench(self, iterations: int):
        self.logger.log_iter(self.__bench(iterations))



def get_runner(
        test: 'AbstractTestCase',
        parent: 'AbstractRunner',
) -> 'AbstractRunner':
    if isinstance(test, AbstractTestGroup):
        return GroupRunner(test, parent)
    elif isinstance(test, TestCase):
        return CaseRunner(test, parent)

    raise TypeError(f'Unknown test: {test}')
