from time import perf_counter
from typing import Tuple, List, Union

from ..progress_bar import ProgressBarPrinter

PROGRESS_BAR_LEN = 50
RESULT_TUPLE_SINGLE = Tuple[float]
RESULT_TUPLE_MULTI = Tuple[float,float,float,float]
RESULT_TUPLE = Union[RESULT_TUPLE_SINGLE,RESULT_TUPLE_MULTI]


def _rm_calc(benches: List[float]) -> RESULT_TUPLE_MULTI:
    s = sum(benches)
    mx, mn, avg = (
        max(benches),
        min(benches),
        s / len(benches),
    )
    return s, mx, mn, avg


class TestCase:
    def __init__(self, test, *args, **kwargs):
        self._f = test
        self._args = args
        self._kwargs = kwargs

    @property
    def name(self) -> str:
        return self._f.__name__

    def _run(self):
        raise NotImplementedError

    def _run_single(self) -> float:
        bench_start = perf_counter()
        self._run()
        return perf_counter() - bench_start

    def run_single(self) -> RESULT_TUPLE_SINGLE:
        return (self._run_single(),)

    def run_multiple(self, iterations: int) -> RESULT_TUPLE_MULTI:
        return _rm_calc([self._run_single()
                for _ in ProgressBarPrinter(iterations, PROGRESS_BAR_LEN)])

    def run(self, iterations: int):
        if iterations == 1:
            return self.run_single()
        else:
            return self.run_multiple(iterations)

    async def run_async(self, iterations: int):
        raise NotImplementedError

class FunctionTestCase(TestCase):
    def _run(self):
      self._f(*self._args, **self._kwargs)

class AsyncTestCase(TestCase):

    async def _run_single(self) -> float:
        bench_start = perf_counter()
        await self._run()
        return perf_counter() - bench_start

    async def run_single(self) -> RESULT_TUPLE_SINGLE:
        return (await self._run_single(),)

    async def run_multiple(self, iterations: int) -> RESULT_TUPLE_MULTI:
        return _rm_calc([await self._run_single()
                for _ in ProgressBarPrinter(iterations, PROGRESS_BAR_LEN)])

    async def run(self, iterations: int):
        if iterations == 1:
            return await self.run_single()
        else:
            return await self.run_multiple(iterations)

    def _run(self):
        return self._f

class CoroutineTestCase(AsyncTestCase):
    def _run(self):
        return self._f
    async def _run_multiple(self, *_, **__):
        raise NotImplementedError('cannot reuse coroutines')

class CoroutineFunctionTestCase(AsyncTestCase):
    def _run(self):
        return self._f(*self._args, **self._kwargs)
