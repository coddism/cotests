from typing import TYPE_CHECKING, List, Optional

from . import AbstractTestCase
from .case_decorators import RESULT_TUPLE_MULTI, SyncDecoratorFactory, AsyncDecoratorFactory
from .case_ext import TestCaseExt
from .progress_bar import ProgressBarPrinter

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


class TestCase(AbstractTestCase):
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

class FunctionTestCase(TestCase):
    is_async = False

    def _bench_single(self) -> float:
        return sum(
            self._ext.decor(self._f)(*p[0], **p[1])
            for p in self._params
        )

    @SyncDecoratorFactory()
    def run_test(self, *, level: int = 0) -> float:
        return self._bench_single()

    @SyncDecoratorFactory(True)
    def run_bench(self, iterations: int, *, level: int = 0) -> RESULT_TUPLE_MULTI:
        return _calc_multi_results([self._bench_single() for _ in ProgressBarPrinter(iterations)])



class AsyncTestCase(TestCase):
    is_async = True

    async def _run(self, *args, **kwargs):
        await self._f(*args, **kwargs)

    async def _bench_single(self) -> float:
        return sum([
            await self._ext.decor_async(self._run, True)(*p[0], **p[1])
            for p in self._params
        ])

    @AsyncDecoratorFactory()
    async def run_test(self, *, level: int = 0) -> float:
        return await self._bench_single()

    @AsyncDecoratorFactory(True)
    async def run_bench(self, iterations: int, *, level: int = 0) -> RESULT_TUPLE_MULTI:
        return _calc_multi_results([await self._bench_single() for _ in ProgressBarPrinter(iterations)])


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

    @AsyncDecoratorFactory(True)
    async def run_bench(self, iterations: int, *, level: int = 0) -> RESULT_TUPLE_MULTI:
        if iterations > 1:
            raise NotImplementedError('cannot reuse coroutines')
        return await super().run_bench(self, iterations, level=level)


class CoroutineFunctionTestCase(AsyncTestCase):
    ...
