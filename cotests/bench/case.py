from time import perf_counter
from typing import TYPE_CHECKING, Tuple, List, Union

from ..progress_bar import ProgressBarPrinter


RESULT_TUPLE_SINGLE = Tuple[float]
RESULT_TUPLE_MULTI = Tuple[float, float, float, float]
RESULT_TUPLE = Union[RESULT_TUPLE_SINGLE, RESULT_TUPLE_MULTI]

if TYPE_CHECKING:
    from .co_test_args import ParamsList


def _calc_multi_results(benches: List[float]) -> RESULT_TUPLE_MULTI:
    s = sum(benches)
    mx, mn, avg = (
        max(benches),
        min(benches),
        s / len(benches),
    )
    return s, mx, mn, avg


class TestCase:
    IS_ASYNC = False
    def __init__(self, test, params: 'ParamsList'):
        self._f = test
        self._params = params

    @property
    def name(self) -> str:
        return self._f.__name__

    def _run(self, *args, **kwargs):
        return self._f(*args, **kwargs)

    def _bench_single(self) -> float:
        res = .0
        for p in self._params:
            bench_start = perf_counter()
            self._run(*p[0], **p[1])
            res += perf_counter() - bench_start
        return res

    def run_single(self) -> RESULT_TUPLE_SINGLE:
        return (self._bench_single(),)

    def run_multiple(self, iterations: int) -> RESULT_TUPLE_MULTI:
        return _calc_multi_results([self._bench_single()
                                    for _ in ProgressBarPrinter(iterations)])

    def run(self, iterations: int):
        if iterations == 1:
            return self.run_single()
        else:
            return self.run_multiple(iterations)


class FunctionTestCase(TestCase):
    ...


class AsyncTestCase(TestCase):
    IS_ASYNC = True

    async def _bench_single(self) -> float:
        res = .0
        for p in self._params:
            bench_start = perf_counter()
            await self._run(*p[0], **p[1])
            res += perf_counter() - bench_start
        return res

    async def run_single(self) -> RESULT_TUPLE_SINGLE:
        return (await self._bench_single(),)

    async def run_multiple(self, iterations: int) -> RESULT_TUPLE_MULTI:
        return _calc_multi_results([await self._bench_single()
                                    for _ in ProgressBarPrinter(iterations)])


class CoroutineTestCase(AsyncTestCase):
    def __init__(self, test, params: 'ParamsList'):
        assert params == [((), {})], 'Coroutine with args'
        super().__init__(test, params)

    def _run(self, *_, **__):
        return self._f

    async def run_multiple(self, *_, **__):
        raise NotImplementedError('cannot reuse coroutines')


class CoroutineFunctionTestCase(AsyncTestCase):
    ...
