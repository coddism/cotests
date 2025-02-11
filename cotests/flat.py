import inspect
from time import perf_counter
from typing import Callable, List, Tuple, Optional, Dict

from .progress_bar import ProgressBarPrinter
from .utils import format_sec_metrix, print_test_results


def bench(func):
    def wrapper(*args, **kwargs):
        bench_start = perf_counter()
        func(*args, **kwargs)
        return perf_counter() - bench_start
    return wrapper


__PROGRESS_BAR_LEN = 50


def bench_batch(
        *funcs,
        iterations: int = 1,
        with_args: Optional[Tuple] = None,
        with_kwargs: Optional[Dict] = None,
):
    assert iterations >= 1
    if len(funcs) == 0:
        print('Nothing to test')
        return
    f_start = perf_counter()
    exp = []

    def bf(f: Callable, *args, **kwargs):
        fun_name = f.__name__
        print(f'{fun_name}.', end='', flush=True)
        try:
            if iterations == 1:
                bench_start = perf_counter()
                f(*args, **kwargs)
                s = perf_counter() - bench_start
                exp.append((fun_name, s))
            else:
                benches = []
                for _ in ProgressBarPrinter(iterations, __PROGRESS_BAR_LEN):
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

    to_run: List[Tuple] = []
    def add_test(fn, args = None, kwargs = None):
        if args and with_args:
            raise Exception('args conflict')
        if kwargs and with_kwargs:
            raise Exception('kwargs conflict')

        to_run.append((
            fn,
            args or with_args or (),
            kwargs or with_kwargs or {},
        ))

    for func_item in funcs:
        if inspect.isfunction(func_item):
            add_test(func_item)
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
            add_test(*ff)
        else:
            raise ValueError(f'Unknown function: {func_item}')

    for f0, f1, f2 in to_run:
        bf(f0, *f1, **f2)

    print_test_results(
        exp,
        headers=('time',) if iterations == 1 else ('full', 'max', 'min', 'avg')
    )

    print(f'Full time: {format_sec_metrix(perf_counter() - f_start)}')


__all__ = (bench, bench_batch)
