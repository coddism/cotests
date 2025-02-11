import inspect
from time import perf_counter
from typing import Callable, Optional, Tuple, Dict, Any, Iterable, List

from .progress_bar import ProgressBarPrinter
from .utils import format_sec_metrix, print_test_results

TestTuple = Tuple[Callable, Optional[Tuple[Any]], Optional[Dict[str, Any]]]


class Tester:
    PROGRESS_BAR_LEN = 50

    def __init__(self,
                 global_args: Optional[Tuple[Any]] = None,
                 global_kwargs: Optional[Dict[str, Any]] = None
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
                 fn: Callable,
                 args: Optional[Tuple[Any]] = None,
                 kwargs: Optional[Dict[str, Any]] = None
                 ):
        if self.__global_args and args:
            raise Exception('args conflict')
        if self.__global_kwargs and kwargs:
            raise Exception('kwargs conflict')

        self.__tests.append(
            (fn, args, kwargs)
        )

    # def __run_single_test(self, test: TestTuple):
    #     f, args, kwargs = test

    def run_tests(self, iterations: int = 1):
        if not self.__tests:
            raise Exception('Tests not found')
        f_start = perf_counter()
        exp = []
        for test in self.__tests:
            f = test[0]
            args = self.__global_args or test[1] or ()
            kwargs = self.__global_kwargs or test[2] or {}

            fun_name = f.__name__
            print(f'{fun_name}:', end='', flush=True)
            try:
                if iterations == 1:
                    bench_start = perf_counter()
                    f(*args, **kwargs)
                    s = perf_counter() - bench_start
                    exp.append((fun_name, s))
                else:
                    benches = []
                    for _ in ProgressBarPrinter(iterations, self.PROGRESS_BAR_LEN):
                        bs0 = perf_counter()
                        f(*args, **kwargs)
                        benches.append(perf_counter() - bs0)
                    s = sum(benches)
                    mx, mn, avg = max(benches), min(benches), s / iterations
                    exp.append((fun_name, s, mx, mn, avg))
            except Exception as e:
                print(f'error: {e}')
            else:
                print('ok')

        print_test_results(
            exp,
            headers=('time',) if iterations == 1 else ('full', 'max', 'min', 'avg')
        )

        print(f'Full time: {format_sec_metrix(perf_counter() - f_start)}')
