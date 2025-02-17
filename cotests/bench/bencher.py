import asyncio
import inspect
import sys
from time import perf_counter
from typing import (Callable, Optional, Tuple, Dict, Any,
                    Iterable, List, Union, Coroutine, Awaitable, TYPE_CHECKING)

from .case import TestCase, CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase
from ..utils import print_test_results, format_sec_metrix

if TYPE_CHECKING:
    if sys.version_info[:2] >= (3,11):
        from typing import Unpack
    else:
        from typing_extensions import Unpack

    TestFunction = Union[Callable, Coroutine]
    InTestTuple = Tuple[TestFunction, Unpack[Tuple[Any,...]]]
    InTest = Union[TestFunction, InTestTuple]
    TestArgs = Tuple[Any, ...]
    TestKwargs = Dict[str, Any]
    TestTuple = Tuple[TestFunction, TestArgs, TestKwargs]


class Bencher:

    def __new__(
        cls,
        *tests: 'InTest',
        iterations: int = 1,
        with_args: Optional['TestArgs'] = None,
        with_kwargs: Optional['TestKwargs'] = None,
        raise_exceptions: bool = False,
    ) -> Union[None, Awaitable[None]]:
        print('\n', '-'*14, 'Start Bencher', '-'*14)
        c = super().__new__(cls)
        c.__init__(
            with_args=with_args,
            with_kwargs=with_kwargs,
        )
        c.add_tests(tests)
        t = c.run_tests(iterations, raise_exceptions)
        if inspect.iscoroutine(t):
            # try to run
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                # print('Run in new loop')
                asyncio.run(t)
            else:
                # print('Cannot run. Return coroutine')
                return t
        # else:
        #     print('No coroutines')

    def __init__(self, *_, **kwargs):
        # print('INIT')
        self.__tests: List[TestCase] = []
        self.__global_args = kwargs.get('with_args', ())
        self.__global_kwargs = kwargs.get('with_kwargs', ())
        self.__has_coroutines = False

    def add_test(self, test: 'InTest', *args, **kwargs):
        def merge_args():
            if self.__global_args and args:
                raise Exception('args conflict')
            fa = self.__global_args or args or ()

            if self.__global_kwargs and kwargs:
                fkw = {**self.__global_kwargs, **kwargs}
            else:
                fkw = self.__global_kwargs or kwargs or {}

            return fa, fkw

        if inspect.iscoroutine(test):
            if args or kwargs:
                raise ValueError('Coroutine with args')
            self.__tests.append(
                CoroutineTestCase(test)
            )
            self.__has_coroutines = True
        elif inspect.iscoroutinefunction(test):
            a, k = merge_args()
            self.__tests.append(
                CoroutineFunctionTestCase(test, *a, **k)
            )
            self.__has_coroutines = True
        elif inspect.isfunction(test):
            a, k = merge_args()
            self.__tests.append(
                FunctionTestCase(test, *a, **k)
            )
        elif isinstance(test, tuple):
            f = test[0]
            a_, kw_ = (), {}
            ta_ = []
            for ti in test[1:]:
                if isinstance(ti, tuple):
                    if a_ or ta_: raise ValueError('TestItem args conflict')
                    a_ = ti
                elif isinstance(ti, dict):
                    if kw_: raise ValueError('TestItem kwargs conflict')
                    kw_ = ti
                else:
                    if a_: raise ValueError('TestItem args conflict')
                    ta_.append(ti)

            self.add_test(f, *a_, *ta_, **kw_)
        else:
            raise ValueError(f'Unknown test: {test}')

    def add_tests(self, tests: Iterable['InTest']):
        for test in tests:
            self.add_test(test)
            # print(
            #     inspect.isfunction(test),
            #     inspect.iscoroutine(test),
            #     inspect.isawaitable(test),
            #     inspect.iscoroutinefunction(test),
            # )

    def run_tests(self,
                  iterations: int = 1,
                  raise_exceptions: bool = False,
                  ):
        if not self.__tests:
            raise Exception('Tests not found')
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
                for test in self.__tests:
                    fun_name = test.name
                    print(f' * {fun_name}:', end='', flush=True)
                    try:
                        s = test.run(iterations)
                        if inspect.iscoroutine(s):
                            s = await s
                    except Exception as e:
                        if raise_exceptions:
                            raise
                        print(f'error: {e}')
                    else:
                        # print(f'ok')
                        print(f'ok - {format_sec_metrix(s[0])}')
                        exp_.append((fun_name, *s))

                aft = perf_counter() - a_start
                print_res(exp_)
                print(f'Full time: {format_sec_metrix(aft)}')

            return do_async()
        else:
            def g_sync():
                for test in self.__tests:
                    fun_name = test.name
                    print(f' * {fun_name}:', end='', flush=True)
                    try:
                        s = test.run(iterations)
                    except Exception as e:
                        if raise_exceptions:
                            raise
                        print(f'error: {e}')
                    else:
                        # print(f'ok')
                        print(f'ok - {format_sec_metrix(s[0])}')
                        yield (fun_name, *s)

            s_start = perf_counter()
            exp = [x for x in g_sync()]
            sft = perf_counter() - s_start
            print_res(exp)
            print(f'Full time: {format_sec_metrix(sft)}')
