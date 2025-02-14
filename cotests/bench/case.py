import asyncio
from time import perf_counter
from typing import Callable, Coroutine, Tuple

from ..progress_bar import ProgressBarPrinter

PROGRESS_BAR_LEN = 50


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

    async def _run_single(self) -> float:
        bench_start = perf_counter()
        await self._run()
        return perf_counter() - bench_start

    async def _run_multiple(self, iterations: int) -> Tuple[float,...]:
        benches = [await self._run_single()
                   for _ in ProgressBarPrinter(iterations, PROGRESS_BAR_LEN)]
        s = sum(benches)
        mx, mn, avg = max(benches), min(benches), s / iterations
        return s, mx, mn, avg

    async def run(self, iterations: int) -> Tuple[float,...]:
        if iterations == 1:
            return (await self._run_single(),)
        else:
            return await self._run_multiple(iterations)


class CoroutineTestCase(TestCase):
    def _run(self):
        # task = asyncio.create_task(self._f)
        return self._f
    async def _run_multiple(self, *_, **__):
        # await self._f
        raise NotImplementedError('cannot reuse coroutines')

class CoroutineFunctionTestCase(TestCase):
    def _run(self):
        return self._f(*self._args, **self._kwargs)

class FunctionTestCase(TestCase):
    async def _run(self):
      self._f(*self._args, **self._kwargs)
