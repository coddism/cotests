from typing import TYPE_CHECKING, List, Type
from .runner.group import GroupRunner

if TYPE_CHECKING:
    from cotests.logger import CoLogger
    from .runner.abstract import AbstractRunner


class AbstractTestCase:
    is_async: bool
    name: str
    _RUNNER: Type['AbstractRunner']

    def run_test(self, *, level: int = 0):
        raise NotImplementedError
    def run_bench(self, iterations: int, *, level: int = 0):
        raise NotImplementedError
    def get_runner(self, parent: 'AbstractRunner') -> 'AbstractRunner':
        return self._RUNNER(self, parent)


class AbstractTestGroup(AbstractTestCase):
    is_empty: bool
    init_errors: List[Exception]
    logger: 'CoLogger'
    tests: List[AbstractTestCase]
    _RUNNER = GroupRunner
    def constructor(self): ...
    def destructor(self): ...
