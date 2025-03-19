from typing import TYPE_CHECKING, Optional
from cotests.logger import CoLogger

if TYPE_CHECKING:
    from ..abstract import AbstractTestCase


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

    @property
    def is_async(self): return self.test.is_async

    def run(self): raise NotImplementedError
    def bench(self, iterations: int): raise NotImplementedError


__all__ = ('AbstractRunner', )
