import asyncio
import time

from cotests import CoTestCase, bench_batch, test_batch


class TObj(CoTestCase):
    # test functions should start with "test_"

    def test_0(self, t: float = .1): time.sleep(t)

    @staticmethod
    def test_1(t: float = .2): time.sleep(t)

    @classmethod
    def test_2(cls, t: float = .3): time.sleep(t)

    def test_3(self): ...

class TObjA(CoTestCase):
    async def test_a0(self, t: float = .1): await asyncio.sleep(t)

    @classmethod
    async def test_a1(cls, t: float = .2): await asyncio.sleep(t)

    @staticmethod
    async def test_a2(t: float = .15): await asyncio.sleep(t)

    async def test_a3(self): ...
    async def test_a4(self, t: float): await asyncio.sleep(t)


if __name__ == '__main__':
    iterations = 5
    TObj().run_bench(
        iterations=iterations,
        global_args=(.05,),
    )
    TObjA().run_bench(
        iterations=iterations,
        global_args=(.05,),
    )
    # or
    bench_batch(
        TObj(),
        iterations=5,
        global_args=(.1,),
    )
    # or
    def tt0(t: float = .2): time.sleep(t)
    def tt1(t: float = .2): time.sleep(t)

    test_batch(
        TObj, tt0, TObjA(), tt1,
        global_args=(.03,),
        name='t_obj',
    )
