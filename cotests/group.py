import inspect
from contextlib import contextmanager
from time import perf_counter
from typing import TYPE_CHECKING, Optional, Iterable, List, Tuple

from .bench import AbstractCoCase, CoException, AbstractTestCase
from .bench.case import (
    CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase, FunctionTestCaseWithAsyncPrePost,
)
from .bench.case_ext import TestCaseExt
from .bench.co_test_args import CoTestArgs
from .bench.utils import format_sec_metrix, print_test_results, try_to_run, get_level_prefix

if TYPE_CHECKING:
    from .bench.typ import InTest, TestArgs, TestKwargs, PrePostTest, RunResult


def _decorator_go(cls: 'CoTestGroup', func):
    def wrapper_sync(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except CoException as ce:
            ce.print_errors()

    async def wrapper_async(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except CoException as ce:
            ce.print_errors()

    if cls.is_async:
        return wrapper_async
    else:
        return wrapper_sync


class _TestCTX:
    _GREETINGS: str = 'CoTest'

    def __init__(self, cls: 'CoTestGroup', level: int):
        self._group = cls
        self._level = level
        self.__pref = get_level_prefix(level)
        self.__start: float = .0
        self.__finish: float = .0
        self.__errors = []

    def add_error(self, e: Exception):
        self.__errors.append(e)

    def __enter__(self):
        self.__pre()
        self.__start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__finish = perf_counter() - self.__start
        self._final_print()

        if self.__errors:
            raise CoException(self.__errors, self._group.name)

        if exc_type:
            print(exc_type, exc_value, exc_traceback)

    @contextmanager
    def ctx(self):
        try:
            yield
        except Exception as e_:
            self.add_error(e_)

    def __pre(self):
        print(self.__pref)
        print(f'{self.__pref}⌌', '-' * 14, f' Start {self._GREETINGS} ', self._group.name, '-' * 14, sep='')
        if not self._group.tests:
            print(f'{self.__pref}⌎ Tests not found')
            raise CoException(
                [Exception('Tests not found')],
                where=self._group.name
            )

    def _final_print(self):
        print(f'{self.__pref}⌎-- Full time: {format_sec_metrix(self.__finish)}')


class _BenchCTX(_TestCTX):
    _GREETINGS: str = 'CoBench'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__exp = []

    def add_exp(self, s: Tuple):
        self.__exp.append(s)

    def _final_print(self):
        pref_1 = get_level_prefix(self._level + 1)
        for str_row in print_test_results(
                self.__exp,
                headers=('full', 'max', 'min', 'avg'),
                # headers=('time', ) if single_run else ('full', 'max', 'min', 'avg'),
        ):
            print(pref_1, str_row)
        super()._final_print()


class CoTestGroup(AbstractTestCase):
    NAME = ''

    def __init__(
            self,
            *tests: 'InTest',
            name: Optional[str] = '',
            global_args: Optional['TestArgs'] = None,
            global_kwargs: Optional['TestKwargs'] = None,
            personal_args: Optional[Iterable['TestArgs']] = None,
            personal_kwargs: Optional[Iterable['TestKwargs']] = None,
            pre_test: Optional['PrePostTest'] = None,
            post_test: Optional['PrePostTest'] = None,
            cotest_args: Optional['CoTestArgs'] = None,
            cotest_ext: Optional['TestCaseExt'] = None,
    ):
        # if len(tests) == 0:
        #     raise ValueError('Empty tests list')
        self.__tests: List['AbstractTestCase'] = []
        self.__has_coroutines = False
        self.name = name or self.NAME

        if cotest_args:
            if any((global_args, global_kwargs, personal_args, personal_kwargs)):
                raise Exception('Args conflict')
            self.__cta = cotest_args
        else:
            self.__cta = CoTestArgs(
                personal_args,
                personal_kwargs,
                global_args,
                global_kwargs,
        )

        if cotest_ext:
            if any((pre_test, post_test)):
                raise Exception('Test Case extension conflict')
            self.__tce = cotest_ext
        else:
            self.__tce = TestCaseExt(
                pre_test=pre_test,
                post_test=post_test,
            )

        for test in tests:
            self.__add_test(test)

    def _clone(self, case: AbstractCoCase) -> 'CoTestGroup':
        return CoTestGroup(
            *case.get_tests(),
            cotest_args=self.__cta,
            cotest_ext=self.__tce,
            name=case.name,
        )

    @property
    def tests(self):
        return self.__tests

    @property
    def is_async(self):
        return self.__has_coroutines

    @property
    def has_coroutines(self) -> bool:
        return self.__has_coroutines

    def __add_test(self, test: 'InTest', *args, **kwargs):
        if isinstance(test, tuple):
            if args or kwargs:
                raise Exception('InTest format Error')
            assert len(test) > 0
            f = test[0]
            a_, kw_ = (), {}
            for ti in test[1:]:
                if isinstance(ti, tuple):
                    if a_: raise ValueError('TestItem args conflict')
                    a_ = ti
                elif isinstance(ti, dict):
                    if kw_: raise ValueError('TestItem kwargs conflict')
                    kw_ = ti
                else:
                    raise ValueError(f'Unsupported type for InTest: {type(ti)}')

            self.__add_test(f, *a_, **kw_)
        else:
            if inspect.iscoroutine(test):
                tc = CoroutineTestCase
            elif inspect.iscoroutinefunction(test):
                tc = CoroutineFunctionTestCase
            elif inspect.isfunction(test) or inspect.ismethod(test):
                if self.__tce.is_async:
                    tc = FunctionTestCaseWithAsyncPrePost
                else:
                    tc = FunctionTestCase
            elif isinstance(test, CoTestGroup):
                return self.__add_test_case(test)
            elif isinstance(test, AbstractCoCase):
                return self.__add_test_case(self._clone(test))
            elif inspect.isclass(test) and issubclass(test, AbstractCoCase):
                return self.__add_test_case(self._clone(test()))
            else:
                raise ValueError(f'Unknown test: {test}')

            return self.__add_test_case(tc(
                test,
                params=self.__cta.get(args, kwargs),
                ext=self.__tce,
            ))

    def __add_test_case(self, case: AbstractTestCase):
        if case.is_async:
            self.__has_coroutines = True
        self.__tests.append(case)

    def go(self):
        return _decorator_go(self, self.run_test)()

    def go_bench(self, iterations: int):
        return _decorator_go(self, self.run_bench)(iterations)

    def run_test(self, *, level: int = 0):
        if self.is_async:
            return self.run_test_async(level=level)

        with _TestCTX(self, level) as m:
            for test_ in self.__tests:
                with m.ctx():
                    test_.run_test(level=level + 1)

    async def run_test_async(self, *, level: int = 0):

        with _TestCTX(self, level) as m:
            for test_ in self.__tests:
                with m.ctx():
                    if test_.is_async:
                        await test_.run_test(level=level+1)
                    else:
                        test_.run_test(level=level+1)

    def run_bench(self, iterations: int, *, level: int = 0):
        if self.is_async:
            return self.run_bench_async(iterations, level=level)

        with _BenchCTX(self, level) as m:
            for test_ in self.__tests:
                with m.ctx():
                    s = test_.run_bench(iterations, level=level+1)
                    if s:
                        m.add_exp((test_.name, *s))

    async def run_bench_async(self, iterations: int, *, level: int = 0):

        with _BenchCTX(self, level) as m:
            for test_ in self.__tests:
                with m.ctx():
                    if test_.is_async:
                        s = await test_.run_bench(iterations, level=level + 1)
                    else:
                        s = test_.run_bench(iterations, level=level + 1)

                    if s:
                        m.add_exp((test_.name, *s))


__greeting = """
+---------------------+
|    Start CoTests    |
+---------------------+
"""

def test_groups(*groups: CoTestGroup, name='__main__') -> 'RunResult':
    print(__greeting)
    g = CoTestGroup(*groups, name=name)
    return try_to_run(g.go())
