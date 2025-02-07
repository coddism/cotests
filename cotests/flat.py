import inspect
from time import perf_counter
from typing import Callable


def bench(func):
    def wrapper(*args, **kwargs):
        bench_start = perf_counter()
        func(*args, **kwargs)
        return perf_counter() - bench_start
    return wrapper


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
        for func_name, sec in exp:
            print('| %.3f sec | %-20s | ' % (sec, func_name))
    else:
        for func_name, sec_full, sec_min, sec_max, sec_avg in exp:
            print('| %.3f sec | %.3f sec | %.3f sec | %.3f sec | %-20s | ' % (
                sec_full, sec_min, sec_max, sec_avg, func_name
            ))
