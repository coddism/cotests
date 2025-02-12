import asyncio
import time
from cotests import bench_batch


async def test0():
    await asyncio.sleep(.2)
async def test1():
    await asyncio.sleep(.1)
def test2():
    time.sleep(.3)


if __name__ == '__main__':
    bench_batch(
        test0,
        test1,
        # test2,
        iterations=4,
        raise_exceptions=True,
    )
