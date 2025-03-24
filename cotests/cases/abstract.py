from typing import TYPE_CHECKING, List, Type
from .runner.group import GroupRunner

if TYPE_CHECKING:
    from .runner.abstract import AbstractRunner


class AbstractTestCase:
    is_async: bool
    name: str
    _RUNNER: Type['AbstractRunner']

    def run_test(self):
        raise NotImplementedError
    def run_bench(self, iterations: int):
        raise NotImplementedError
    def get_runner(self, parent: 'AbstractRunner') -> 'AbstractRunner':
        return self._RUNNER(self, parent)


class AbstractTestGroup(AbstractTestCase):
    is_empty: bool
    init_errors: List[Exception]
    tests: List[AbstractTestCase]
    _RUNNER = GroupRunner
    def constructor(self): ...
    def destructor(self): ...
