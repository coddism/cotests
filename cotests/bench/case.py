from time import perf_counter
from typing import TYPE_CHECKING, Tuple, List, Union

from ..progress_bar import ProgressBarPrinter

PROGRESS_BAR_LEN = 50
RESULT_TUPLE_SINGLE = Tuple[float]
RESULT_TUPLE_MULTI = Tuple[float, float, float, float]
RESULT_TUPLE = Union[RESULT_TUPLE_SINGLE, RESULT_TUPLE_MULTI]

if TYPE_CHECKING:
    from .co_test_args import ParamsList


def rm_calc(benches: List[float]) -> RESULT_TUPLE_MULTI:
    s = sum(benches)
    mx, mn, avg = (
        max(benches),
        min(benches),
        s / len(benches),
    )
    return s, mx, mn, avg


class TestCase:
    IS_ASYNC = False
    def __init__(self,
                 test,
                 params: 'ParamsList',
                 ):
        self._f = test
        self._params = params

    @property
    def name(self) -> str:
        return self._f.__name__

    def _run(self, *args, **kwargs):
        raise NotImplementedError

    def _run_single(self) -> float:
        bench_start = perf_counter()
        # todo sum
        for p in self._params:
            self._run(*p[0], **p[1])
        return perf_counter() - bench_start

    def run_single(self) -> RESULT_TUPLE_SINGLE:
        return (self._run_single(),)

    def run_multiple(self, iterations: int) -> RESULT_TUPLE_MULTI:
        return rm_calc([self._run_single()
                        for _ in ProgressBarPrinter(iterations, PROGRESS_BAR_LEN)])

    def run(self, iterations: int):
        if iterations == 1:
            return self.run_single()
        else:
            return self.run_multiple(iterations)


class FunctionTestCase(TestCase):
    def _run(self, *args, **kwargs):
        self._f(*args, **kwargs)


class AsyncTestCase(TestCase):
    IS_ASYNC = True

    async def _run_single(self) -> float:
        bench_start = perf_counter()
        for p in self._params:
            await self._run(*p[0], **p[1])
        return perf_counter() - bench_start

    async def run_single(self) -> RESULT_TUPLE_SINGLE:
        return (await self._run_single(),)

    async def run_multiple(self, iterations: int) -> RESULT_TUPLE_MULTI:
        return rm_calc([await self._run_single()
                        for _ in ProgressBarPrinter(iterations, PROGRESS_BAR_LEN)])

    async def run(self, iterations: int):
        if iterations == 1:
            return await self.run_single()
        else:
            return await self.run_multiple(iterations)


class CoroutineTestCase(AsyncTestCase):
    def _run(self, *args, **kwargs):
        if args or kwargs:
            raise Exception('Coroutine with args')
        return self._f

    async def run_multiple(self, *_, **__):
        raise NotImplementedError('cannot reuse coroutines')


class CoroutineFunctionTestCase(AsyncTestCase):
    def _run(self, *args, **kwargs):
        return self._f(*args, **kwargs)
