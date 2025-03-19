from time import perf_counter
from typing import TYPE_CHECKING, Optional, List

from .abstract import AbstractTestCase, AbstractTestGroup
from .cases import TestCase
from .utils.printer import format_sec_metrix
from cotests.logger import CoLogger
from cotests.exceptions import CoException


def get_multilevel_logger(level: int):
    return CoLogger(level)


class AbstractRunner:
    def __init__(self,
                 test: 'AbstractTestCase',
                 parent: Optional['AbstractRunner'],
                 ):
        self.test = test
        self.parent = parent
        self.logger = get_multilevel_logger(self.level)

    @property
    def level(self):
        return self.parent.level + 1

    def run(self): raise NotImplementedError
    def bench(self): raise NotImplementedError


class GroupRunner(AbstractRunner):
    test: 'AbstractTestGroup'
    START_LINE = '-' * 14

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__errors: List[Exception] = []

    def run(self):
        self.logger.info('')
        self.logger.info(
            f'⌌{self.START_LINE} Start CoTest {self.test.name} {self.START_LINE}'
        )

        start_pc = perf_counter()
        for test in self.test.tests:
            try:
                get_runner(test, self).run()
            except Exception as e_:
                self.__errors.append(e_)
        finish_pc = perf_counter() - start_pc

        self.logger.info(f'⌎-- Full time: {format_sec_metrix(finish_pc)}')
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


def get_runner(
        test: 'AbstractTestCase',
        parent: 'AbstractRunner',
) -> 'AbstractRunner':
    if isinstance(test, AbstractTestGroup):
        return GroupRunner(test, parent)
    elif isinstance(test, TestCase):
        return CaseRunner(test, parent)

    raise TypeError(f'Unknown test: {test}')
