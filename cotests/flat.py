import inspect
from math import log10
from time import perf_counter
from typing import Callable, List, Tuple


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

def __float_len(x: float) -> int:
    return int(log10(x)) + 1


def print_test_results(exp: List[Tuple[str, float]]):
    iter_ = exp.__iter__()
    first = next(iter_)
    max_s, min_s, max_fn_len = first[1], first[1], len(first[0])
    for func_name, sec in iter_:
        if sec < min_s: min_s = sec
        if sec > max_s: max_s = sec
        if len(func_name) > max_fn_len:
            max_fn_len = len(func_name)


    for deci, metr in METRIX:
        if max_s > deci and min_s > deci:
            prefix = metr
            break
    else:
        deci, prefix = METRIX[-1]

    max_s_len = __float_len(max_s / deci) + 4
    row_format = f'| %{max_s_len}.3f {prefix} | %-{max_fn_len}s | '

    for func_name, sec in exp:
        print(row_format % (sec / deci, func_name))


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
                # bench_start = perf_counter()
                for _ in range(iterations):
                    bs0 = perf_counter()
                    f(*args, **kwargs)
                    benches.append(perf_counter() - bs0)
                    print('.', end='', flush=True)
                # s = perf_counter() - bench_start
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

    if iterations == 1:
        print_test_results(exp)
        # for func_name, sec in exp:
        #     print('| %.3f sec | %-20s | ' % (sec, func_name))
    else:
        for func_name, sec_full, sec_min, sec_max, sec_avg in exp:
            print('| %.3f sec | %.3f sec | %.3f sec | %.3f sec | %-20s | ' % (
                sec_full, sec_min, sec_max, sec_avg, func_name
            ))
