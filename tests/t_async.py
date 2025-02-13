import asyncio
import time
from cotests import bench_batch


async def test0():
    await asyncio.sleep(.02)
async def test1():
    await asyncio.sleep(.01)
def test2():
    time.sleep(.03)


if __name__ == '__main__':
    bench_batch(
        test0,
        test1,
        test2,
        iterations=10,
        raise_exceptions=True,
    )
