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
