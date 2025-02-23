# CoTests

`cotests` is a light set of tests and benchmarks for python. The main goal is ease of use.

## Features

* Python3.7+
* Can run sync functions, coroutines and coroutinefunctions
* Convenient conversion between min, sec, ms, µs, etc.

## DOX

### bench_batch()
    
    # args
    :param funcs: all functions for test or benchmark
    # kwargs
    :param int iterations: count of iterations for all functions
    :param Optional[Iterable] global_args: arguments for each function
    :param Optional[Mapping] global_kwargs: keyword arguments for each function (can merge with own keyword arguments)
    :param Optional[Iterable[Iterable]] personal_args: list of arguments for each function
    :param Optional[Iterable[Mapping]] personal_kwargs: list of keyword arguments for each function
    :param bool raise_exceptions: set True if you want to stop `bench_batch()` by exception
    :return: None | Awaitable[None]

## Examples

### Simple

```python
from cotests import bench_batch

def test_0(): ...
def test_1(): ...
def test_2(): ...

# just test
bench_batch(
    test_0, test_1, test_2,
)

# more benchy
bench_batch(
    test_0, test_1, test_2,
    iterations=1000,
)
```

Output:
```
 -------------- Start Bencher --------------
 * test_0:ok - 790.002 ns
 * test_1:ok - 520.005 ns
 * test_2:ok - 430.002 ns

+-----------------------------+
|    time    |   f    |   %   |
| 790.002 ns | test_0 | 183.7 |
| 520.005 ns | test_1 | 120.9 |
| 430.002 ns | test_2 | 100.0 |
+-----------------------------+
Full time: 42.870 µs

 -------------- Start Bencher --------------
 * test_0:..................................................ok - 256.518 µs
 * test_1:..................................................ok - 267.469 µs
 * test_2:..................................................ok - 265.210 µs

+---------------------------------------------------------------------+
|    full    |     max     |    min     |    avg     |   f    |   %   |
| 256.518 µs |  429.995 ns | 200.002 ns | 256.518 ns | test_0 | 100.0 |
| 267.469 µs |  560.001 ns | 230.000 ns | 267.469 ns | test_1 | 104.3 |
| 265.210 µs | 1280.001 ns | 230.000 ns | 265.210 ns | test_2 | 103.4 |
+---------------------------------------------------------------------+
Full time: 2.261 ms
```

### Almost simple

```python
from cotests import bench_batch

def test_0(*args, **kwargs): ...
def test_1(*args, **kwargs): ...
def test_2(*args, **kwargs): ...
def test_3(*args, **kwargs): ...

# base test: enumeration, run 1 time
bench_batch(test_0, test_1, test_2, test_3)

# just for convenience, all to 1 list
tests_list = [value for key, value in globals().items()
              if key.startswith('test_') and callable(value) and value.__module__ == __name__]

# to stop tests if raise exceptions & print traceback
bench_batch(
    *tests_list,
    raise_exceptions=True
)

# benchmarks: run all 100 times
bench_batch(
    *tests_list,
    iterations=100,
)

# test with args: like test_0(1), test_1(1), etc...
bench_batch(
    *tests_list,
    global_args=(1,)
)

# test with kwargs: like test_0(a=1), test_1(a=1), etc...
bench_batch(
    *tests_list,
    global_kwargs={'a': 1}
)

# It can be combined: like test_0(1, a=1), test_1(1, a=1), etc...
bench_batch(
    *tests_list,
    global_args=(1,),
    global_kwargs={'a': 1}
)

async def test_a0(*args, **kwargs): ...
async def test_a1(*args, **kwargs): ...

# different ways to set test function & combo kwargs
bench_batch(
    test_0,  # test_0()
    (test_1, (1, 2,)),  # test_1(1, 2)
    (test_2, {'a': 1}),  # test_2(a=1)
    (test_3, (1, 2), {'a': 1}),  # test_3(1, 2, a=1)
    # async
    test_a0,  # and other options above are available
    test_a0(),  # run like coroutine
    test_a1(1, 2, a=1),  # run like coroutine with arguments
    # optional
    raise_exceptions=True,  # raise exceptions, print traceback; default False
    # iterations=1,  # count of iterations you want; default 1 = just test; don't work with coroutines
)
# ... with global args
function_list = [value for key, value in globals().items()
                 if key.startswith('test_') and callable(value) and value.__module__ == __name__]
bench_batch(
    *function_list,
    global_args=(1, 2),
    global_kwargs={'a': 1},
    # test_0(1, 2, a=1), test_1(1, 2, a=1), etc...
)
# ... with personal args
bench_batch(
    *function_list,
    personal_args=[(x,) for x in range(len(function_list))],
    personal_kwargs=[{'a': x} for x in range(len(function_list))],
    # test_0(0, a=0), test_0(1, a=1), ..., test_0(5, a=5), test_1(0, a=0), test_0(1, a=1), ..., test_a1(5, a=5)
)
```

### classes

```python
import asyncio
import time

from cotests import CoCase, bench_batch


class TObj(CoCase):

    def test_0(self, t: float = .1): time.sleep(t)

    @staticmethod
    def test_1(t: float = .2): time.sleep(t)

    @classmethod
    def test_2(cls, t: float = .3): time.sleep(t)

    async def test_a0(self, t: float = .1): await asyncio.sleep(t)

    @classmethod
    async def test_a1(cls, t: float = .2): await asyncio.sleep(t)


TObj().run_tests(
    iterations=5,
    global_args=(.1,),
)
# or
bench_batch(
    TObj(),
    iterations=5,
    global_args=(.1,),
)
# or
bench_batch(
    TObj,
    iterations=5,
    global_args=(.1,),
)
```


### errors?

```python
from cotests import bench_batch

def test_0():
    ...
def test_1():
    raise Exception('I want error!')

bench_batch(test_0, test_1,)

# need to stop?
bench_batch(
    test_0, test_1,
    raise_exceptions=True,
)
```

```
 -------------- Start Bencher --------------
 * test_0:ok - 849.999 ns
 * test_1:error: I want error!

+-----------------------------+
|    time    |   f    |   %   |
| 849.999 ns | test_0 | 100.0 |
+-----------------------------+
Full time: 30.750 µs

 -------------- Start Bencher --------------
 * test_0:ok - 549.997 ns
 * test_1:Traceback (most recent call last):
  ... *here is standart python traceback*
    raise Exception('I want error!')
Exception: I want error!
```

### is orjson faster?

```python
# content of tests/t_json.py

import json
import orjson
import os.path
from argparse import ArgumentParser
from cotests import bench_batch


def bench_json(file_path: str):
    with open(file_path, 'rb') as f:
        json.load(f)

def bench_orjson(file_path: str):
    with open(file_path, 'rb') as f:
        orjson.loads(f.read())


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('path_file')
    args = parser.parse_args()

    if not os.path.isfile(args.path_file):
        raise FileNotFoundError

    bench_batch(
        bench_json,
        bench_orjson,
        iterations=50,
        global_args=(args.path_file,),
        # or you can use:
        # global_kwargs={'file_path': args.path_file},
    )
```

Run:
```sh
python -m tests.t_json /path/to/large-file.json
```

Output:
```
 -------------- Start Bencher --------------
 * bench_json:..................................................ok - 11.745 sec
 * bench_orjson:..................................................ok - 7.983 sec

+--------------------------------------------------------------------------+
|    full    |    max     |    min     |    avg     |      f       |   %   |
| 11.745 sec | 254.484 ms | 220.911 ms | 234.896 ms | bench_json   | 147.1 |
|  7.983 sec | 182.397 ms | 152.058 ms | 159.662 ms | bench_orjson | 100.0 |
+--------------------------------------------------------------------------+
Full time: 19.733 sec

```

### async

```python
import asyncio
import time
from cotests import bench_batch


async def test0(sleep_time: float = .02):
    await asyncio.sleep(sleep_time)
def test1(sleep_time: float = .03):
    time.sleep(sleep_time)


if __name__ == '__main__':
    fun_async = (
        test0,
        (test0, (.15,)),  # set custom args
    )
    fun_sync = (
        test1,
        (test1, (.12,)),
    )

    print(' ---------------ONLY SYNC-------------------')
    bench_batch(*fun_sync)

    print(' ---------------ASYNC W\T LOOP--------------')
    bench_batch(
        *fun_async,  # coroutinefunctions can reuse
        test0(.05),  # coroutine with reuse - error
        iterations=2,
    )

    async def main():
        print(' ---------------ASYNC WITH LOOP-------------')
        # if `bench_batch()` with coroutines run in running loop, you need to use `await`
        await bench_batch(
            *fun_async,
            *fun_sync,
            test0(.05),  # coroutine without reuse - ok
        )
        # without coroutines = without await
        bench_batch(*fun_sync)
    asyncio.run(main())
```
