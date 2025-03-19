from typing import TYPE_CHECKING, Optional

from .abstract import AbstractTestCase
from .runner.case import CaseRunner, AsyncCaseRunner
from .utils.case_ext import TestCaseExt

if TYPE_CHECKING:
    from cotests.typ import CoArgsList


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
    _RUNNER = CaseRunner

    def run_test(self) -> float:
        return sum(
            self._ext.decor(self._f)(*p[0], **p[1])
            for p in self._params
        )


class AsyncTestCase(TestCase):
    is_async = True
    _RUNNER = AsyncCaseRunner

    async def _run(self, *args, **kwargs):
        await self._f(*args, **kwargs)

    async def _bench_single(self) -> float:
        return sum([
            await self._ext.decor_async(self._run, True)(*p[0], **p[1])
            for p in self._params
        ])

    async def run_test(self) -> float:
        return await self._bench_single()


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


class CoroutineFunctionTestCase(AsyncTestCase):
    ...
