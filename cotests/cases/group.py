import inspect
from typing import TYPE_CHECKING, Optional, Iterable, List

from .abstract import AbstractTestGroup
from .cases import (
    AbstractTestCase,
    CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase, FunctionTestCaseWithAsyncPrePost
)
from .utils.args import CoTestArgs
from .utils.ctx import TestCTX, BenchCTX
from .utils.ttr import try_to_run
from .utils.case_ext import TestCaseExt
from cotests.case.abstract import AbstractCoCase
from cotests.exceptions import CoException

if TYPE_CHECKING:
    from cotests.typ import InTest, TestArgs, TestKwargs, PrePostTest


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


class CoTestGroup(AbstractTestGroup):
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
    def is_empty(self):
        return self.__tests == []

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
        return try_to_run(_decorator_go(self, self.run_test)())

    def go_bench(self, iterations: int):
        assert iterations >= 1
        return try_to_run(_decorator_go(self, self.run_bench)(iterations))

    def run_test(self, *, level: int = 0):
        if self.is_async:
            return self.run_test_async(level=level)

        with TestCTX(self, level) as m:
            for test_ in self.__tests:
                with m.ctx():
                    test_.run_test(level=level + 1)

    async def run_test_async(self, *, level: int = 0):

        with TestCTX(self, level) as m:
            for test_ in self.__tests:
                with m.ctx():
                    if test_.is_async:
                        await test_.run_test(level=level+1)
                    else:
                        test_.run_test(level=level+1)

    def run_bench(self, iterations: int, *, level: int = 0):
        if self.is_async:
            return self.run_bench_async(iterations, level=level)

        with BenchCTX(self, level, iterations=iterations) as m:
            for test_ in self.__tests:
                with m.ctx():
                    s = test_.run_bench(iterations, level=level+1)
                    if s:
                        m.add_exp(test_.name, s)

    async def run_bench_async(self, iterations: int, *, level: int = 0):

        with BenchCTX(self, level, iterations=iterations) as m:
            for test_ in self.__tests:
                with m.ctx():
                    if test_.is_async:
                        s = await test_.run_bench(iterations, level=level + 1)
                    else:
                        s = test_.run_bench(iterations, level=level + 1)

                    if s:
                        m.add_exp(test_.name, s)


def test_groups(*groups: CoTestGroup, name='__main__'):
    g = CoTestGroup(*groups, name=name)
    return g.go()
