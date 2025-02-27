from typing import TYPE_CHECKING, Tuple, List, Optional

from .case_ext import TestCaseExt
from .progress_bar import ProgressBarPrinter
from .utils import format_sec_metrix, get_level_prefix

RESULT_TUPLE_SINGLE = Tuple[float]
RESULT_TUPLE_MULTI = Tuple[float, float, float, float]

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


def b_sec_s(ts: float) -> float:
    return ts
def b_sec_m(ts: RESULT_TUPLE_MULTI) -> float:
    return ts[0]

class __DecoratorFactory:
    def __init__(self, multi: bool = False):
        if multi:
            self.bs = b_sec_m
        else:
            self.bs = b_sec_s

    def __call__(self, func):
        return self.wrapper(self, func)

    @staticmethod
    def _print_start(cls: 'TestCase', **kwargs):
        level = kwargs.get('level', 0)
        print(f'{get_level_prefix(level)} * {cls.name}:', end='', flush=True)

    @staticmethod
    def wrapper(self: '__DecoratorFactory', func):
        raise NotImplementedError


class SyncDecoratorFactory(__DecoratorFactory):
    @staticmethod
    def wrapper(self: '__DecoratorFactory', func):
        def w(cls: 'TestCase', *args, **kwargs):
            self._print_start(cls, **kwargs)
            try:
                ts = func(cls, *args, **kwargs)
            except Exception as e_:
                print(f'error: {e_}')
                raise
            else:
                print(f'ok - {format_sec_metrix(self.bs(ts))}')
                return ts
        return w

class AsyncDecoratorFactory(__DecoratorFactory):
    @staticmethod
    def wrapper(self: '__DecoratorFactory', func):
        async def wa(cls: 'TestCase', *args, **kwargs):
            self._print_start(cls, **kwargs)
            try:
                ts = await func(cls, *args, **kwargs)
            except Exception as e_:
                print(f'error: {e_}')
                raise
            else:
                print(f'ok - {format_sec_metrix(self.bs(ts))}')
                return ts
        return wa

# TestCases


class AbstractTestCase:
    is_async: bool
    name: str

    def run_test(self, *, level: int = 0):
        raise NotImplementedError
    def run_bench(self, iterations: int, *, level: int = 0):
        raise NotImplementedError


class TestCase(AbstractTestCase):
    is_async = False
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

    @SyncDecoratorFactory()
    def run_test(self, *, level: int = 0) -> float:
        return self._bench_single()

    @SyncDecoratorFactory(True)
    def run_bench(self, iterations: int, *, level: int = 0) -> RESULT_TUPLE_MULTI:
        return _calc_multi_results([self._bench_single() for _ in ProgressBarPrinter(iterations)])


class FunctionTestCase(TestCase):
    ...


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
