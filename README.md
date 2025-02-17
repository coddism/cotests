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
    :param Optional[Tuple] with_args: arguments for each function
    :param Optional[Dict] with_kwargs: keyword arguments for each function (can merge with own keyword arguments)
    :param bool raise_exceptions: set True if you want to stop `bench_batch()` by exception
    :return: None | Awaitable

## Examples

### Simple

```python
from cotests import bench_batch

def test_0():
    ...
def test_1():
    ...
def test_2():
    ...

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
 * test_0:ok - 3.300 µs
 * test_1:ok - 1.900 µs
 * test_2:ok - 1.800 µs

+-------------------+
|   time   |   f    |
| 3.300 µs | test_0 |
| 1.900 µs | test_1 |
| 1.800 µs | test_2 |
+-------------------+
Full time: 333.300 µs

 -------------- Start Bencher --------------
 * test_0:..................................................ok - 531.200 µs
 * test_1:..................................................ok - 533.000 µs
 * test_2:..................................................ok - 805.300 µs

+------------------------------------------------------------+
|    full    |    max     |    min     |    avg     |   f    |
| 531.200 µs |   2.000 µs | 400.000 ns | 531.200 ns | test_0 |
| 533.000 µs |   2.200 µs | 300.000 ns | 533.000 ns | test_1 |
| 805.300 µs | 255.100 µs | 300.000 ns | 805.300 ns | test_2 |
+------------------------------------------------------------+
Full time: 19.713 ms
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
    with_args=(1,)
)

# test with kwargs: like test_0(a=1), test_1(a=1), etc...
bench_batch(
    *tests_list,
    with_kwargs={'a':1}
)

# It can be combined: like test_0(1, a=1), test_1(1, a=1), etc...
bench_batch(
    *tests_list,
    with_args=(1,),
    with_kwargs={'a':1}
)

async def atest_0(*args, **kwargs): ...
async def atest_1(*args, **kwargs): ...

# different ways to set test function & combo kwargs
bench_batch(
    test_0,  # test_0()
    (test_1, (1,2,)),  # test_1(1, 2)
    (test_1, 1, 2),  # also test_1(1, 2)
    (test_2, {'a': 1}),  # test_2(a=1)
    (test_3, (1,2), {'a': 1}),  # test_3(1, 2, a=1)
    (test_3, 1, 2, {'a': 1}),  # also test_3(1, 2, a=1)
    # async
    atest_0,  # and other options above are available
    atest_0(),  # run like coroutine
    atest_1(1, 2, a=1),  # run like coroutine with arguments
    # optional
    # with_args=(1,2),  # error in this example - args have already been set, but you can use it in other examples
    with_kwargs={'b':2},  # will be merged to existing kwargs
    raise_exceptions=True,  # raise exceptions, print traceback; default False
    iterations=1,  # count of iterations you want; default 1 = just test
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
 * test_0:ok - 1.900 µs
 * test_1:error: I want error!

+-------------------+
|   time   |   f    |
| 1.900 µs | test_0 |
+-------------------+
Full time: 185.300 µs

 -------------- Start Bencher --------------
 * test_0:ok - 1.100 µs
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
        with_args=(args.path_file,),
        # or you can use:
        # with_kwargs={'file_path': args.path_file},
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
        (test1, .12),  # set custom args without tuple
    )

    print(' ---------------ONLY SYNC-------------------')
    bench_batch(*fun_sync)

    print(' ---------------ASYNC W\T LOOP--------------')
    bench_batch(
        *fun_async,  # coroutinefunctions can reuse
        test0(.05),  # coroutine with reuse - error
        iterations=2
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
