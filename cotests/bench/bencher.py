import inspect
from time import perf_counter
from typing import (Callable, Optional, Tuple, Dict, Any,
                    Iterable, List, Union, Coroutine)

from .case import TestCase, CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase
from ..utils import print_test_results, format_sec_metrix

TestFunction = Union[Callable, Coroutine]
TestArgs = Tuple[Any, ...]
TestKwargs = Dict[str, Any]
TestTuple = Tuple[TestFunction, TestArgs, TestKwargs]


class Bencher:

    def __new__(
        cls,
        *tests,
        iterations: int = 1,
        with_args: Optional[TestArgs] = None,
        with_kwargs: Optional[TestKwargs] = None,
        raise_exceptions: bool = False,
    ):
        c = super().__new__(cls)
        c.__init__(
            with_args=with_args,
            with_kwargs=with_kwargs,
        )
        c.add_tests(tests)
        c.run_tests(iterations, raise_exceptions)
        # return c

    def __init__(self, *args, **kwargs):
        # print('INIT')
        self.__tests: List[TestCase] = []
        self.__global_args = kwargs.get('with_args', ())
        self.__global_kwargs = kwargs.get('with_kwargs', ())
        self.__has_coroutines = False

    @property
    def tests(self):
        return self.__tests

    def add_test(self, test, *args, **kwargs):
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
        elif inspect.iscoroutinefunction(test):
            a, k = merge_args()
            self.__tests.append(
                CoroutineFunctionTestCase(test, *a, **k)
            )
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

    def add_tests(self, tests: Iterable):
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

        exp = []
        f_start = perf_counter()
        for test in self.__tests:
            fun_name = test.name
            print(f'{fun_name}:', end='', flush=True)
            try:
                s = test.run()
                exp.append((fun_name, s))
            except Exception as e:
                if raise_exceptions:
                    raise
                print(f'error: {e}')
            else:
                print(f'ok - {format_sec_metrix(s)}')

        print_test_results(
            exp,
            # headers=self.headers
        )
        print(f'Full time: {format_sec_metrix(perf_counter() - f_start)}')
