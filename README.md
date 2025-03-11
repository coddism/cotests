# CoTests

`cotests` is a light set of tests and benchmarks for python. The main goal is ease of use.

## Features

* Python3.7+
* Can run sync functions, coroutines, coroutinefunctions, classes
* Convenient conversion between min, sec, ms, µs, etc.
* Comparison table in benchmarks
* Whole module test

## DOX

### test_batch() & arguments

Simple run all types of tests.
    
    # args
    :param funcs: all functions/cases/groups for test or benchmark
    # kwargs
    :param Optional[str] name: Title for test
    :param Optional[Iterable] global_args: arguments for each function
    :param Optional[Mapping] global_kwargs: keyword arguments for each function (can merge with own keyword arguments)
    :param Optional[Iterable[Iterable]] personal_args: list of arguments for each function
    :param Optional[Iterable[Mapping]] personal_kwargs: list of keyword arguments for each function
    :param Optional[Callable] pre_test: run before each function; is not added to benchmark time
    :param Optional[Callable] post_test: run after each function; is not added to benchmark time
    :return: None | Awaitable[None]

### bench_batch()

Like `test_batch()'`, but with output a results table, and you can set count of iterations - `:param int iterations`.

### CoTestCase

A class for tests. By default, it runs all methods (including `@classmethod` or `@staticmethod`) starting with `test_`.
It has method `run_tests` - is analog of `bench_batch`.

### CoTestGroup

The main entity - a class for group of tests. It can use all types of tests, as `bench_batch()`.
It has `go()` for test and `go_bench(int)` for benchmark.

### test_groups()

Function for run `CoTestGroup`s. 

### test_module

Function for searching and running all tests in the module by directory path.
Search for all files `t_(.*).py` and inside:
* `CoTestGroup` objects. If found, other types are ignoring.
* functions starting with `test_` 
* `CoTestCase` classes

```python
import os
from cotests import test_module

dir_path = os.path.dirname(os.path.realpath(__file__))
test_module(dir_path)
```

## Examples

### Base using

```python
from cotests import test_batch, bench_batch, CoTestGroup, CoTestCase, test_groups

def test_0(*_, **__): ...
def test_1(*_, **__): ...

async def test_a0(*_, **__): ...
async def test_a1(*_, **__): ...

# Example 1: just test
test_batch(test_0, test_1, test_a0, test_a1)
# Example 1.1: single-run benchmark
bench_batch(test_0, test_1, test_a0, test_a1)
# Example 1.2: benchmark
bench_batch(test_0, test_1, test_a0, test_a1, iterations=50)

# Example 2: CoTestCase
class Case0(CoTestCase):
    def test_0(self): ...
    def test_1(self): ...
    async def test_a0(self): ...
Case0().run_tests()
# Example 2.1: benchmark
Case0().run_tests(iterations=50)

# Example 3: CoTestGroup
g_sync = CoTestGroup(test_0, test_1, name='SYNC')
g_async = CoTestGroup(test_a0, test_a1, name='ASYNC')
g_all = CoTestGroup(test_0, test_1, test_a0, test_a1, Case0, name='ALL')

# Example 3.1 - single group
g_sync.go()
# Example 3.2 - multiple
test_groups(g_sync, g_async, g_all)

# Example 4: ALL
test_batch(
    test_0, test_1, test_a0, test_a1,
    Case0,
    g_sync, g_async, g_all,
)
```

### test_batch & bench_batch

```python
from cotests import test_batch, bench_batch

def test_0(): ...
def test_1(): ...
def test_2(): ...

# just test
test_batch(test_0, test_1, test_2,)

# benchy
bench_batch(test_0, test_1, test_2,)

# more benchy
bench_batch(
    test_0, test_1, test_2,
    iterations=1000,
)
```

Output:
```
⌌-------------- Start CoTest --------------
¦  * test_0:ok - 309.999 ns
¦  * test_1:ok - 320.000 ns
¦  * test_2:ok - 250.000 ns
⌎-- Full time: 122.440 µs

⌌-------------- Start CoBench --------------
¦  * test_0:.ok - 250.000 ns
¦  * test_1:.ok - 210.001 ns
¦  * test_2:.ok - 210.001 ns
¦  +-----------------------------+
¦  |    time    |   f    |   %   |
¦  | 250.000 ns | test_0 | 119.0 |
¦  | 210.001 ns | test_1 | 100.0 |
¦  | 210.001 ns | test_2 | 100.0 |
¦  +-----------------------------+
⌎-- Full time: 84.820 µs

⌌-------------- Start CoBench --------------
¦  * test_0:..................................................ok - 219.999 ns
¦  * test_1:..................................................ok - 239.999 ns
¦  * test_2:..................................................ok - 190.001 ns
¦  +-------------------------------------------------------------------+
¦  |    full    |    max     |    min    |    avg     |   f    |   %   |
¦  | 127.119 µs | 290.001 ns | 90.000 ns | 127.119 ns | test_0 | 119.5 |
¦  | 106.339 µs | 239.999 ns | 90.000 ns | 106.339 ns | test_1 | 100.0 |
¦  | 125.599 µs | 530.001 ns | 90.000 ns | 125.599 ns | test_2 | 118.1 |
¦  +-------------------------------------------------------------------+
⌎-- Full time: 3.417 ms
```

### bench_batch: arguments

```python
from cotests import test_batch

def test_0(*_, **__): ...
def test_1(*_, **__): ...
def test_2(*_, **__): ...
def test_3(*_, **__): ...
async def test_a0(*_, **__): ...
async def test_a1(*_, **__): ...

# just for convenience, all to 1 list
tests_list = [value for key, value in globals().items()
              if key.startswith('test_') and callable(value) and value.__module__ == __name__]

# test with args: like test_0(1), test_1(1), etc...
test_batch(
    *tests_list,
    global_args=(1,)
)

# test with kwargs: like test_0(a=1), test_1(a=1), etc...
test_batch(
    *tests_list,
    global_kwargs={'a': 1}
)

# It can be combined: like test_0(1, a=1), test_1(1, a=1), etc...
test_batch(
    *tests_list,
    global_args=(1,),
    global_kwargs={'a': 1}
)

# different ways to set test function & combo kwargs
test_batch(
    test_0,  # test_0()
    (test_1, (1, 2,)),  # test_1(1, 2)
    (test_2, {'a': 1}),  # test_2(a=1)
    (test_3, (1, 2), {'a': 1}),  # test_3(1, 2, a=1)
    # async
    test_a0,  # and other options above are available
    test_a0(),  # run like coroutine
    test_a1(1, 2, a=1),  # run like coroutine with arguments
)

# ... with personal args
# test_0(0, a=0), test_0(1, a=1), ..., test_0(5, a=5), test_1(0, a=0), test_0(1, a=1), ..., test_a1(5, a=5)
test_batch(
    *tests_list,
    personal_args=[(x,) for x in range(len(tests_list))],
    personal_kwargs=[{'a': x} for x in range(len(tests_list))],
)
```

### CoTestCase

```python
import asyncio
import time

from cotests import CoTestCase, test_batch


class TObj(CoTestCase):
    # test functions should start with "test_"
    def __init__(self): print('Init Case')
    def __del__(self): print('Del Case')

    def test_0(self, t: float = .1): time.sleep(t)

    @staticmethod
    def test_1(t: float = .2): time.sleep(t)

    @classmethod
    def test_2(cls, t: float = .3): time.sleep(t)

    def function_no_test(self): ...  # will be ignored

    async def test_a0(self, t: float = .1): await asyncio.sleep(t)

    @classmethod
    async def test_a1(cls, t: float = .2): await asyncio.sleep(t)


TObj().run_tests(
    global_args=(.1,),
)
# or
test_batch(
    TObj(),
    global_args=(.1,),
)
# or
test_batch(
    TObj,
    global_args=(.1,),
)
```

Partial output:

```
Init Case

⌌-------------- Start CoTest TObj--------------
¦  * test_0:ok - 100.095 ms
¦  * test_1:ok - 100.085 ms
¦  * test_2:ok - 100.085 ms
¦  * test_a0:ok - 100.307 ms
¦  * test_a1:ok - 100.278 ms
⌎-- Full time: 501.431 ms
Del Case
```

### errors?

```python
from cotests import test_batch, CoTestCase

def test_0(): ...
def test_1(): raise Exception('I want error!')

class T0(CoTestCase):
    def test_t0(self): ...
    def test_t1(self): raise ValueError('I want ValueError in case!')

test_batch(test_0, test_1, T0)
```

```
⌌-------------- Start CoTest --------------
¦  * test_0:ok - 350.003 ns
¦  * test_1:error: I want error!
¦ 
¦ ⌌-------------- Start CoTest T0--------------
¦ ¦  * test_t0:ok - 460.001 ns
¦ ¦  * test_t1:error: I want ValueError in case!
¦ ⌎-- Full time: 42.750 µs
⌎-- Full time: 139.400 µs
! Errors:
! * test_1 
!   Exception : I want error!
! * T0 / test_t1 
!   ValueError : I want ValueError in case!
⌎----------------------------
```

### is orjson faster?

```python
# content of tests/json.py
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
        global_args={args.path_file},
    )
```

Run:
```sh
python3 -m tests.json /path/to/large-file.json
```

Output:
```
⌌-------------- Start CoBench --------------
¦  * bench_json:..................................................ok - 11.288 sec
¦  * bench_orjson:..................................................ok - 7.796 sec
¦  +--------------------------------------------------------------------------+
¦  |    full    |    max     |    min     |    avg     |      f       |   %   |
¦  | 11.288 sec | 235.821 ms | 208.986 ms | 225.759 ms | bench_json   | 144.8 |
¦  |  7.796 sec | 167.107 ms | 149.568 ms | 155.927 ms | bench_orjson | 100.0 |
¦  +--------------------------------------------------------------------------+
⌎-- Full time: 19.091 sec
```

### async

```python
import asyncio
import time
from cotests import test_batch, bench_batch


async def test_0(sleep_time: float = .02):
    await asyncio.sleep(sleep_time)
def test_1(sleep_time: float = .03):
    time.sleep(sleep_time)


if __name__ == '__main__':
    fun_async = (
        test_0,
        (test_0, (.15,)),  # set custom args
    )
    fun_sync = (
        test_1,
        (test_1, (.12,)),
    )

    test_batch(*fun_sync, name='ONLY SYNC')

    bench_batch(
        *fun_async,  # coroutinefunctions can reuse
        test_0(.05),  # coroutine with reuse - error
        iterations=2,
        name='ASYNC W/T LOOP',
    )

    async def main():
        # if `bench_batch()` with coroutines run in running loop, you need to use `await`
        await bench_batch(
            *fun_async,
            *fun_sync,
            test_0(.05),  # coroutine without reuse - ok
            name='ASYNC WITH LOOP',
        )
        # without coroutines = without await
        test_batch(*fun_sync, name='SYNC WITH LOOP',)
    asyncio.run(main())
```

### PreTest & PostTest

```python
import asyncio
import time
from cotests import bench_batch, CoTestGroup

def test_0(): print('T0', end='-')
def test_1(): print('T1', end='-')
async def atest_0(): print('T0', end='-')
async def atest_1(): print('T1', end='-')

async def rba():
    await asyncio.sleep(.1)
    print('B', end='~')

def rb():
    time.sleep(.1)
    print('B', end='-')
def ra():
    time.sleep(.1)
    print('A', end=' ')

tests = (test_0, test_1, atest_0, atest_1)

# groups to use in test_module()
g0 = CoTestGroup(*tests, pre_test=rb, post_test=ra, name='SYNC')
g1 = CoTestGroup(*tests, pre_test=rba, post_test=ra, name='ASYNC')

if __name__ == '__main__':
    bench_batch(g0, g1, iterations=3)
```

Partial output:
```
¦ ⌌-------------- Start CoBench SYNC--------------
¦ ¦  * test_0:B-T0-A .B-T0-A .B-T0-A .ok - 11.700 µs
¦ ¦  * test_1:B-T1-A .B-T1-A .B-T1-A .ok - 10.380 µs
¦ ¦  * atest_0:B-T0-A .B-T0-A .B-T0-A .ok - 51.610 µs
¦ ¦  * atest_1:B-T1-A .B-T1-A .B-T1-A .ok - 44.270 µs
...
¦ ⌌-------------- Start CoBench ASYNC--------------
¦ ¦  * test_0:B~T0-A .B~T0-A .B~T0-A .ok - 10.680 µs
¦ ¦  * test_1:B~T1-A .B~T1-A .B~T1-A .ok - 16.020 µs
¦ ¦  * atest_0:B~T0-A .B~T0-A .B~T0-A .ok - 22.160 µs
¦ ¦  * atest_1:B~T1-A .B~T1-A .B~T1-A .ok - 21.009 µs
...
```
