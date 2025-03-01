import inspect
from time import perf_counter
from typing import TYPE_CHECKING, Optional, Iterable, List

from .bench import AbstractCoCase, CoException, AbstractTestCase
from .bench.case import (
    CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase,
    FunctionTestCaseWithAsyncPrePost,
)
from .bench.case_ext import TestCaseExt
from .bench.co_test_args import CoTestArgs
from .bench.utils import format_sec_metrix, print_test_results, try_to_run, get_level_prefix

if TYPE_CHECKING:
    from .bench.typ import InTest, TestArgs, TestKwargs, PrePostTest, RunResult


def decorator_go_sync(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except CoException as ce:
            print('Has errors')
            print(ce)
    return wrapper

def decorator_go_async(func):
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except CoException as ce:
            print('Has errors')
            print(ce)
    return wrapper


class CoTestGroup(AbstractTestCase):
    NAME = ''

    def __init__(
            self,
            *tests: 'InTest',
            # iterations: int = 1,
            # raise_exceptions: bool = False,
            global_args: Optional['TestArgs'] = None,
            global_kwargs: Optional['TestKwargs'] = None,
            personal_args: Optional[Iterable['TestArgs']] = None,
            personal_kwargs: Optional[Iterable['TestKwargs']] = None,
            pre_test: Optional['PrePostTest'] = None,
            post_test: Optional['PrePostTest'] = None,
            name: Optional[str] = '',
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

    @property
    def __go_decorator(self):
        if self.is_async:
            return decorator_go_async
        else:
            return decorator_go_sync

    def go(self):
        return self.__go_decorator(self.run_test)()

    def go_bench(self, iterations: int):
        return self.__go_decorator(self.run_bench)(iterations)

    def run_test(self, *, level: int = 0):
        if self.is_async:
            return self.run_test_async(level=level)

        pref_ = get_level_prefix(level)
        print(pref_)
        print(f'{pref_}⌌', '-' * 14, ' Start CoTest ', self.name, '-' * 14, sep='')
        if not self.__tests:
            print(f'{pref_}⌎ Tests not found')
            return None

        s_start = perf_counter()
        errors = []
        for test_ in self.__tests:
            try:
                test_.run_test(level=level+1)
            except Exception as e_:
                errors.append(e_)

        sft = perf_counter() - s_start
        print(f'{pref_}⌎-- Full time: {format_sec_metrix(sft)}')
        if errors:
            raise CoException(errors)

    async def run_test_async(self, *, level: int = 0):
        pref_ = get_level_prefix(level)
        print(pref_)
        print(f'{pref_}⌌', '-' * 14, ' Start CoTest ', self.name, '-' * 14, sep='')
        if not self.__tests:
            print(f'{pref_}⌎ Tests not found')
            return None

        s_start = perf_counter()
        errors = []
        for test_ in self.__tests:
            try:
                if test_.is_async:
                    await test_.run_test(level=level+1)
                else:
                    test_.run_test(level=level+1)
            except Exception as e_:
                errors.append(e_)

        sft = perf_counter() - s_start
        print(f'{pref_}⌎-- Full time: {format_sec_metrix(sft)}')
        if errors:
            raise CoException(errors)

    def run_bench(self, iterations: int, *, level: int = 0):
        # print(self.__has_coroutines)
        if self.__has_coroutines:
            return self.run_bench_async(iterations, level=level)
        pref_ = get_level_prefix(level)
        pref_1 = get_level_prefix(level+1)
        print(pref_)
        print(f'{pref_}⌌', '-' * 14, ' Start CoBench ', self.name, '-' * 14, sep='')
        if not self.__tests:
            # raise Exception(f'{pref_}⌎ Tests not found')
            print(f'{pref_}⌎ Tests not found')
            return None

        s_start = perf_counter()
        errors = []
        exp = []

        for test_ in self.__tests:
            try:
                s = test_.run_bench(iterations, level=level+1)
            except Exception as e_:
                errors.append(e_)
            else:
                if s:
                    # todo
                    exp.append((test_.name, *s))

        sft = perf_counter() - s_start

        for str_row in print_test_results(
            exp,
            headers=('full', 'max', 'min', 'avg'),
            # headers=('time',) if single_run else ('full', 'max', 'min', 'avg'),
        ):
            print(pref_1, str_row)

        print(f'{pref_}⌎-- Full time: {format_sec_metrix(sft)}')
        if errors:
            raise CoException(errors)

    async def run_bench_async(self, iterations: int, *, level: int = 0):
        pref_ = get_level_prefix(level)
        pref_1 = get_level_prefix(level+1)
        print(pref_)
        print(f'{pref_}⌌', '-' * 14, ' Start CoBench ', self.name, '-' * 14, sep='')
        if not self.__tests:
            print(f'{pref_}⌎ Tests not found')
            return None

        s_start = perf_counter()
        errors = []
        exp = []

        for test_ in self.__tests:
            try:
                if test_.is_async:
                    s = await test_.run_bench(iterations, level=level + 1)
                else:
                    s = test_.run_bench(iterations, level=level + 1)
            except Exception as e_:
                errors.append(e_)
            else:
                if s:
                    # todo
                    exp.append((test_.name, *s))

        sft = perf_counter() - s_start

        for str_row in print_test_results(
            exp,
            headers=('full', 'max', 'min', 'avg'),
            # headers=('time',) if single_run else ('full', 'max', 'min', 'avg'),
        ):
            print(pref_1, str_row)

        print(f'{pref_}⌎-- Full time: {format_sec_metrix(sft)}')
        if errors:
            raise CoException(errors)


__greeting = """
+---------------------+
|    Start CoTests    |
+---------------------+
"""

def test_groups(*groups: CoTestGroup) -> 'RunResult':
    print(__greeting)
    g = CoTestGroup(*groups, name='__main__')
    return try_to_run(g.go())
