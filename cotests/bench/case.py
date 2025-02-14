import asyncio
from time import perf_counter
from typing import Callable, Coroutine, Tuple

from ..progress_bar import ProgressBarPrinter

PROGRESS_BAR_LEN = 50


class TestCase:
    def __init__(self, test, *args, **kwargs):
        self._f = test

    @property
    def name(self) -> str:
        return self._f.__name__

    def _run(self):
        raise NotImplementedError

    async def __run_single(self) -> float:
        bench_start = perf_counter()
        await self._run()
        return perf_counter() - bench_start

    def __run_multiple(self, iterations: int) -> Tuple[float,...]:
        benches = [self.__run_single()
                for _ in ProgressBarPrinter(
                    iterations, PROGRESS_BAR_LEN
                )]
        s = sum(benches)
        mx, mn, avg = max(benches), min(benches), s / iterations
        return s, mx, mn, avg

    async def run(self, iterations: int) -> Tuple[float,...]:
        if iterations == 1:
            return (await self.__run_single(),)
        else:
            return self.__run_multiple(iterations)


class CoroutineTestCase(TestCase):
    def __init__(self, test: Coroutine):
        super().__init__(test)
    def _run(self):
        return self._f

class CoroutineFunctionTestCase(TestCase):
    def __init__(self, test: Callable, *args, **kwargs):
        super().__init__(test(*args, **kwargs))
    def _run(self):
        return self._f

class FunctionTestCase(TestCase):
    def __init__(self, test: Callable, *args, **kwargs):
        super().__init__(test)
        # self._f = test
        self.__args = args
        self.__kwargs = kwargs
    async def _run(self):
      self._f(*self.__args, **self.__kwargs)
