import asyncio
import inspect
from time import perf_counter
from typing import Callable, Optional, Tuple, Dict, Any, Iterable, List

from .progress_bar import ProgressBarPrinter
from .utils import format_sec_metrix, print_test_results


TestFunction = Callable
TestArgs = Tuple[Any]
TestKwargs = Dict[str, Any]
TestTuple = Tuple[TestFunction, TestArgs, TestKwargs]


PROGRESS_BAR_LEN = 50


class Tester:

    def __init__(self,
                 global_args: Optional[TestArgs] = None,
                 global_kwargs: Optional[TestKwargs] = None,
                 ):
        self.__tests: List[TestTuple] = []
        self.__global_args = global_args
        self.__global_kwargs = global_kwargs

        self.__async = False

    def add_tests(self, functions: Iterable):
        for func_item in functions:
            if inspect.isfunction(func_item):
                self.add_test(func_item)
            elif isinstance(func_item, tuple):
                ff = [None, (), {}]
                for fi in func_item:
                    if inspect.isfunction(fi):
                        ff[0] = fi
                    elif isinstance(fi, tuple):
                        ff[1] = fi
                    elif isinstance(fi, dict):
                        ff[2] = fi
                    else:
                        raise ValueError
                assert ff[0] is not None
                self.add_test(*ff)
            else:
                raise ValueError(f'Unknown function: {func_item}')

    def add_test(self,
                 fn: TestFunction,
                 args: Optional[TestArgs] = None,
                 kwargs: Optional[TestKwargs] = None,
                 ):
        assert inspect.isfunction(fn)
        # print(inspect.iscoroutine(fn))
        # print(inspect.isawaitable(fn))
        # print(inspect.iscoroutinefunction(fn))
        if inspect.iscoroutinefunction(fn):
            self.__async = True
            # raise RuntimeError('You need to use async tester')

        if self.__global_args and args:
            raise Exception('args conflict')
        fa = self.__global_args or args or ()

        if self.__global_kwargs and kwargs:
            fkw = {**self.__global_kwargs, **kwargs}
        else:
            fkw = self.__global_kwargs or kwargs or {}

        self.__tests.append(
            (fn, fa, fkw)
        )

    def run_tests(self,
                  iterations: int = 1,
                  raise_exceptions: bool = False,
                  ):
        if not self.__tests:
            raise Exception('Tests not found')

        if iterations == 1:
            runner = SingleRunner(raise_exceptions)
        else:
            runner = MultiRunner(raise_exceptions, iterations)

        return runner.run(self.__tests)


class AbstractTestRunner:
    headers: Tuple[str,...]

    def __init__(self,
                 raise_exceptions: bool = False,
                 iterations: int = 1,):
        self._iterations = iterations
        self.__raise_exceptions = raise_exceptions

    def run(self,
            tests: List[TestTuple]):
        exp = []
        f_start = perf_counter()
        for test in tests:
            fun_name = test[0].__name__
            print(f'{fun_name}:', end='', flush=True)
            try:
                s = self._run(test)
                exp.append((fun_name, *s))
            except Exception as e:
                if self.__raise_exceptions:
                    raise
                print(f'error: {e}')
            else:
                print(f'ok - {format_sec_metrix(s[0])}')

        print_test_results(
            exp,
            headers=self.headers
        )
        print(f'Full time: {format_sec_metrix(perf_counter() - f_start)}')

    @staticmethod
    def _run_single(test: TestTuple) -> float:
        bench_start = perf_counter()
        if inspect.iscoroutinefunction(test[0]):
            asyncio.run(test[0](*test[1], **test[2]))
        else:
            test[0](*test[1], **test[2])
        return perf_counter() - bench_start

    def _run(self, test: TestTuple) -> Tuple[float, ...]:
        raise NotImplementedError


class SingleRunner(AbstractTestRunner):
    headers = ('time',)

    def _run(self, test: TestTuple) -> Tuple[float, ...]:
        t = self._run_single(test)
        return (t,)

class MultiRunner(AbstractTestRunner):
    headers = ('full', 'max', 'min', 'avg')

    def _run(self, test: TestTuple) -> Tuple[float, ...]:
        benches = [self._run_single(test)
                for _ in ProgressBarPrinter(
                self._iterations, PROGRESS_BAR_LEN
            )]
        s = sum(benches)
        mx, mn, avg = max(benches), min(benches), s / self._iterations
        return s, mx, mn, avg
