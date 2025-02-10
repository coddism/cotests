import inspect
from math import log10
from time import perf_counter
from typing import Callable, List, Tuple, Optional
from .progress_bar import ProgressBarPrinter


def bench(func):
    def wrapper(*args, **kwargs):
        bench_start = perf_counter()
        func(*args, **kwargs)
        return perf_counter() - bench_start
    return wrapper


METRIX = (
    (60, 'min'),
    (1, 'sec'),
    (.1**3, 'ms'),
    (.1**6, 'µs'),
    (.1**9, 'ns'),
    (.1**12, 'ps'),
    (.1**15, 'fs'),
)
__PROGRESS_BAR_LEN = 50


def __float_len(x: float) -> int:
    return int(log10(x)) + 1


def print_test_results(
        exp: List[Tuple[str, float]],
        *,
        headers: Optional[Tuple] = None,
):
    iter_ = exp.__iter__()
    first = next(iter_)
    max_fn_len = len(first[0])
    minmax = [[m,m] for m in first[1:]]

    if headers:
        assert len(headers) + 1 == len(first)

    for i in iter_:
        if len(i[0]) > max_fn_len:
            max_fn_len = len(i[0])
        for im, sec in enumerate(i[1:]):
            if minmax[im][0] > sec:
                minmax[im][0] = sec
            elif minmax[im][1] < sec:
                minmax[im][1] = sec

    multi = []
    row_format = ''
    lens = []

    for min_s, max_s in minmax:
        for deci, metr in METRIX:
            if min_s > deci:
                prefix = metr
                break
        else:
            deci, prefix = METRIX[-1]

        max_s_len = __float_len(max_s / deci) + 4
        row_format += f'| %{max_s_len}.3f {prefix} '
        multi.append(deci)
        lens.append(max_s_len + len(prefix) + 1)

    row_format += f'| %-{max_fn_len}s |'
    lens.append(max_fn_len)

    print('\n+' + '-' * (sum(lens) + len(lens)*3 - 1) + '+')
    if headers:
        print('| ' + ' | '.join(h.center(lens[i]) for i, h in enumerate((*headers, 'f'))) + ' |')

    for item in exp:
        print(row_format % (*(i_sec / multi[i] for i, i_sec in enumerate(item[1:])), item[0]))


def bench_batch(
        *funcs,
        iterations: int = 1,
):
    assert iterations >= 1
    if len(funcs) == 0:
        print('Nothing to test')
        return
    exp = []

    def bf(f: Callable, *args, **kwargs):
        fn = f.__name__
        print(f'{fn}.', end='', flush=True)
        try:
            if iterations == 1:
                bench_start = perf_counter()
                f(*args, **kwargs)
                s = perf_counter() - bench_start
                exp.append((fn, s))
            else:
                benches = []
                for _ in ProgressBarPrinter(iterations, __PROGRESS_BAR_LEN):
                    bs0 = perf_counter()
                    f(*args, **kwargs)
                    benches.append(perf_counter() - bs0)
                s = sum(benches)
                mx, mn, avg = max(benches), min(benches), s / iterations
                exp.append((fn, s, mx, mn, avg))
        except Exception as e:
            print(f'error: {e}')
        else:
            print('ok')

    for func_item in funcs:
        if inspect.isfunction(func_item):
            bf(func_item)
        elif isinstance(func_item, tuple):
            ff = [None, None, None]
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
            bf(ff[0],
               *(ff[1] or ()),
               **(ff[2] or {})
               )
        else:
            print('unknown')

    print_test_results(
        exp,
        headers=('time',) if iterations == 1 else ('full', 'max', 'min', 'avg')
    )


__all__ = (bench, bench_batch)
