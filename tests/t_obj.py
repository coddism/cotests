import asyncio
import time

from cotests import CoCase


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
    iterations=10,
    global_args=(.1,),
    # personal_args=[(.2,), (.1,)],
)
