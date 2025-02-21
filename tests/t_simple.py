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


async def atest_0(*args, **kwargs): ...
async def atest_1(*args, **kwargs): ...


# different ways to set test function & combo kwargs
bench_batch(
    test_0,  # test_0()
    (test_1, (1, 2,)),  # test_1(1, 2)
    (test_2, {'a': 1}),  # test_2(a=1)
    (test_3, (1, 2), {'a': 1}),  # test_3(1, 2, a=1)
    # async
    atest_0,  # and other options above are available
    atest_0(),  # run like coroutine
    atest_1(1, 2, a=1),  # run like coroutine with arguments
    # optional
    # global_args=(1,2),  # error in this example - args have already been set, but you can use it in other examples
    # global_kwargs={'b': 2},  # will be merged to existing kwargs
    raise_exceptions=True,  # raise exceptions, print traceback; default False
    # iterations=1,  # count of iterations you want; default 1 = just test
)
