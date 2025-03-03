from typing import TYPE_CHECKING, Tuple, List, Union, Optional

from .case_ext import TestCaseExt
from ..progress_bar import ProgressBarPrinter

RESULT_TUPLE_SINGLE = Tuple[float]
RESULT_TUPLE_MULTI = Tuple[float, float, float, float]
RESULT_TUPLE = Union[RESULT_TUPLE_SINGLE, RESULT_TUPLE_MULTI]

if TYPE_CHECKING:
    from .co_test_args import CoArgsList


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
    def __init__(self,
                 test,
                 *,
                 params: 'CoArgsList',
                 ext: Optional[TestCaseExt] = None,
                 ):
        self._f = test
        self._params = params
        self._ext = ext or TestCaseExt()

    @property
    def name(self) -> str:
        return self._f.__name__

    def _bench_single(self) -> float:
        return sum(
            self._ext.decor(self._f)(*p[0], **p[1])
            for p in self._params
        )

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

    async def _run(self, *args, **kwargs):
        await self._f(*args, **kwargs)

    async def _bench_single(self) -> float:
        return sum([
            await self._ext.decor_async(self._run, True)(*p[0], **p[1])
            for p in self._params
        ])

    async def run_single(self) -> RESULT_TUPLE_SINGLE:
        return (await self._bench_single(),)

    async def run_multiple(self, iterations: int) -> RESULT_TUPLE_MULTI:
        return _calc_multi_results([await self._bench_single()
                                    for _ in ProgressBarPrinter(iterations)])


class FunctionTestCaseWithAsyncPrePost(AsyncTestCase):
    async def _bench_single(self) -> float:
        return sum([
            await self._ext.decor_async(self._f, False)(*p[0], **p[1])
            for p in self._params
        ])


class CoroutineTestCase(AsyncTestCase):
    def __init__(self, *args, **kwargs):
        assert kwargs['params'] == [((), {})], 'Coroutine with args'
        super().__init__(*args, **kwargs)

    def _run(self, *_, **__):
        return self._f

    async def run_multiple(self, *_, **__):
        raise NotImplementedError('cannot reuse coroutines')


class CoroutineFunctionTestCase(AsyncTestCase):
    ...
