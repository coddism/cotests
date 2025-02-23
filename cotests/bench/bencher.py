import asyncio
import inspect
from time import perf_counter
from typing import TYPE_CHECKING, Optional, Tuple, Set, Iterable, List, Union, Awaitable

from .case import CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase
from .co_test_args import CoTestArgs
from ..utils import print_test_results, format_sec_metrix

if TYPE_CHECKING:
    from .case import TestCase
    from .typ import TestArgs, TestKwargs, InTest


class Bencher:

    def __new__(
            cls,
            *tests: 'InTest',
            iterations: int = 1,
            global_args: Optional['TestArgs'] = None,
            global_kwargs: Optional['TestKwargs'] = None,
            personal_args: Optional[Iterable['TestArgs']] = None,
            personal_kwargs: Optional[Iterable['TestKwargs']] = None,
            raise_exceptions: bool = False,
    ) -> Union[None, Awaitable[None]]:
        print('\n', '-' * 14, 'Start Bencher', '-' * 14)
        if global_args and not isinstance(global_args, (List, Tuple, Set)):
            print('Better to use for args: list, tuple, set')

        c = super().__new__(cls)
        c.__init__(
            *tests,
            global_args=global_args,
            global_kwargs=global_kwargs,
            personal_args=personal_args,
            personal_kwargs=personal_kwargs,
        )
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

    def __init__(self, *tests, **kwargs):
        # print('INIT')
        self.__cta = CoTestArgs(
            kwargs.get('personal_args'),
            kwargs.get('personal_kwargs'),
            kwargs.get('global_args'),
            kwargs.get('global_kwargs'),
        )

        self.__tests: List['TestCase'] = []
        self.__has_coroutines = False

        for test in tests:
            self.__add_test(test)

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
            elif inspect.isfunction(test):
                tc = FunctionTestCase
            else:
                raise ValueError(f'Unknown test: {test}')

            self.__tests.append(tc(
                test,
                params=self.__cta.get(args, kwargs)
            ))

    def run_tests(self,
                  iterations: int = 1,
                  raise_exceptions: bool = False,
                  ):
        if not self.__tests:
            print('Tests not found')
            return
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
            print_res(exp)
            print(f'Full time: {format_sec_metrix(sft)}')
