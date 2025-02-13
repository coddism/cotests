import asyncio
from time import perf_counter
from typing import Callable, Coroutine


class TestCase:
    def __init__(self, test, *args, **kwargs):
        self._f = test

    @property
    def name(self) -> str:
        return self._f.__name__

    def _run(self):
        raise NotImplementedError

    def run(self) -> float:
        bench_start = perf_counter()
        self._run()
        return perf_counter() - bench_start

class CoroutineTestCase(TestCase):
    def __init__(self, test: Coroutine):
        super().__init__(test)
    def _run(self):
        asyncio.run(self._f)

class CoroutineFunctionTestCase(TestCase):
    def __init__(self, test: Callable, *args, **kwargs):
        super().__init__(test(*args, **kwargs))
    def _run(self):
        asyncio.run(self._f)

class FunctionTestCase(TestCase):
    def __init__(self, test: Callable, *args, **kwargs):
        super().__init__(test)
        # self._f = test
        self.__args = args
        self.__kwargs = kwargs
    def _run(self):
      self._f(*self.__args, **self.__kwargs)
