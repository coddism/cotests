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
