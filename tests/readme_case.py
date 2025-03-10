import asyncio
import time

from cotests import CoTestCase, bench_batch


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
bench_batch(
    TObj(),
    global_args=(.1,),
)
# or
bench_batch(
    TObj,
    global_args=(.1,),
)
