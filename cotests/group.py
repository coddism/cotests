import inspect
from time import perf_counter
from typing import TYPE_CHECKING, Optional, Iterable, List

from .bench import AbstractCoCase
from .bench.case import (
    CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase,
    FunctionTestCaseWithAsyncPrePost
)
from .bench.case_ext import TestCaseExt
from .bench.co_test_args import CoTestArgs
from .utils import format_sec_metrix, print_test_results, try_to_run

if TYPE_CHECKING:
    from .bench.case import TestCase
    from .bench.typ import InTest, TestArgs, TestKwargs, PrePostTest, RunResult


class CoTestGroup:
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
    ):
        if len(tests) == 0:
            raise ValueError('Empty tests list')
        self.__tests: List['TestCase'] = []
        self.__has_coroutines = False
        self.name = name or self.NAME

        self.__cta = CoTestArgs(
            personal_args,
            personal_kwargs,
            global_args,
            global_kwargs,
        )
        self.__tce = TestCaseExt(
            pre_test=pre_test,
            post_test=post_test,
        )

        for test in tests:
            self.__add_test(test)

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
                self.__has_coroutines = True
            elif inspect.iscoroutinefunction(test):
                tc = CoroutineFunctionTestCase
                self.__has_coroutines = True
            elif inspect.isfunction(test) or inspect.ismethod(test):
                if self.__tce.is_async:
                    tc = FunctionTestCaseWithAsyncPrePost
                    self.__has_coroutines = True
                else:
                    tc = FunctionTestCase
            elif isinstance(test, AbstractCoCase):
                for test in test.get_tests():
                    self.__add_test(test, *args, **kwargs)
                return
            elif inspect.isclass(test) and issubclass(test, AbstractCoCase):
                for test in test().get_tests():
                    self.__add_test(test, *args, **kwargs)
                return
            else:
                raise ValueError(f'Unknown test: {test}')

            self.__tests.append(tc(
                test,
                params=self.__cta.get(args, kwargs),
                ext=self.__tce,
            ))

    def run_tests(self,
                  iterations: int = 1,
                  raise_exceptions: bool = False,
                  ) -> 'RunResult':
        print('\n', '-' * 14, 'Start CoTest', self.name, '-' * 14)
        if not self.__tests:
            print('Tests not found')
            return None
        single_run = iterations == 1

        def print_res(rexp: list):
            print_test_results(
                rexp,
                headers=('time',) if single_run else ('full', 'max', 'min', 'avg'),
            )

        if self.__has_coroutines:
            async def do_async():
                a_start = perf_counter()
                exp_ = []
                for test_ in self.__tests:
                    print(f' * {test_.name}:', end='', flush=True)
                    try:
                        if test_.IS_ASYNC:
                            s_ = await test_.run(iterations)
                        else:
                            s_ = test_.run(iterations)
                    except Exception as e_:
                        if raise_exceptions:
                            raise
                        print(f'error: {e_}')
                    else:
                        print(f'ok - {format_sec_metrix(s_[0])}')
                        exp_.append((test_.name, *s_))

                aft = perf_counter() - a_start
                if not single_run:
                    print_res(exp_)
                print(f'Full time: {format_sec_metrix(aft)}')

            return do_async()
        else:
            s_start = perf_counter()
            exp = []
            for test in self.__tests:
                assert test.IS_ASYNC is False
                print(f' * {test.name}:', end='', flush=True)
                try:
                    s = test.run(iterations)
                except Exception as e:
                    if raise_exceptions:
                        raise
                    print(f'error: {e}')
                else:
                    print(f'ok - {format_sec_metrix(s[0])}')
                    exp.append((test.name, *s))

            sft = perf_counter() - s_start
            if not single_run:
                print_res(exp)
            print(f'Full time: {format_sec_metrix(sft)}')


def test_groups(*groups: CoTestGroup) -> 'RunResult':

    coro = any(x.has_coroutines for x in groups)
    if coro:
        async def run():
            print('\n', '-' * 14, 'Start CoTests', '-' * 14)
            for group_ in groups:
                if group_.has_coroutines:
                    await group_.run_tests()
                else:
                    group_.run_tests()
        return try_to_run(run())
    else:
        print('\n', '-' * 14, 'Start CoTests', '-' * 14)
        for group in groups:
            group.run_tests()
