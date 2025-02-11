import inspect
from time import perf_counter
from typing import Callable, Optional, Tuple, Dict, Any, Iterable, List

from .progress_bar import ProgressBarPrinter
from .utils import format_sec_metrix, print_test_results


TestFunction = Callable
TestArgs = Tuple[Any]
TestKwargs = Dict[str, Any]
TestTuple = Tuple[TestFunction, TestArgs, TestKwargs]


class Tester:
    PROGRESS_BAR_LEN = 50

    def __init__(self,
                 global_args: Optional[TestArgs] = None,
                 global_kwargs: Optional[TestKwargs] = None,
                 ):
        self.__tests: List[TestTuple] = []
        self.__global_args = global_args
        self.__global_kwargs = global_kwargs

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

    @staticmethod
    def __run_single_test(fn: TestFunction,
                          args: Optional[TestArgs] = None,
                          kwargs: Optional[TestKwargs] = None,
                          ) -> float:
        bench_start = perf_counter()
        fn(*args, **kwargs)
        return perf_counter() - bench_start

    @classmethod
    def __run_multiple_tests(cls,
                             fn: TestFunction,
                             args: Optional[TestArgs] = None,
                             kwargs: Optional[TestKwargs] = None,
                             *,
                             iterations: int
                             ) -> Tuple[float, float, float, float]:
        benches = [cls.__run_single_test(fn, args, kwargs)
                for _ in ProgressBarPrinter(iterations, cls.PROGRESS_BAR_LEN)]
        s = sum(benches)
        mx, mn, avg = max(benches), min(benches), s / iterations
        return s, mx, mn, avg


    def run_tests(self,
                  iterations: int = 1,
                  raise_exceptions: bool = False,
                  ):
        if not self.__tests:
            raise Exception('Tests not found')
        f_start = perf_counter()
        exp = []
        for test in self.__tests:
            f, args, kwargs = test

            fun_name = f.__name__
            print(f'{fun_name}:', end='', flush=True)
            try:
                if iterations == 1:
                    s = self.__run_single_test(f, args, kwargs)
                    exp.append((fun_name, s))
                    t_sec = s
                else:
                    s = self.__run_multiple_tests(
                        f, args, kwargs,
                        iterations=iterations
                    )
                    exp.append((fun_name, *s))
                    t_sec = s[0]
            except Exception as e:
                if raise_exceptions:
                    raise
                print(f'error: {e}')
            else:
                print(f'ok - {format_sec_metrix(t_sec)}')

        print_test_results(
            exp,
            headers=('time',) if iterations == 1 else ('full', 'max', 'min', 'avg')
        )

        print(f'Full time: {format_sec_metrix(perf_counter() - f_start)}')
