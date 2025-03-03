import asyncio
import time

from cotests import CoCase, bench_batch


class TObj(CoCase):
    # test functions should start with "test_"

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
