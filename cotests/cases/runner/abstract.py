from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..abstract import AbstractTestCase
    from cotests.logger import CoLogger


class AbstractRunner:
    def __init__(self,
                 test: 'AbstractTestCase',
                 parent: Optional['AbstractRunner'],
                 ):
        self.test = test
        self.parent = parent

    @property
    def logger(self) -> 'CoLogger':
        return self.parent.logger.child

    @property
    def is_async(self): return self.test.is_async

    def run(self): raise NotImplementedError
    def bench(self, iterations: int): raise NotImplementedError


__all__ = ('AbstractRunner', )
