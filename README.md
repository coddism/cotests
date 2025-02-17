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
        iterations=10,
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
 * bench_json:..........ok - 4.202 sec
 * bench_orjson:..........ok - 2.212 sec

+-----------------------------------------------------------------+
|    full   |    max     |    min     |    avg     |      f       |
| 4.202 sec | 442.286 ms | 405.153 ms | 420.238 ms | bench_json   |
| 2.212 sec | 233.752 ms | 200.718 ms | 221.202 ms | bench_orjson |
+-----------------------------------------------------------------+
Full time: 6.418 sec
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
