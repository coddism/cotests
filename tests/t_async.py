import asyncio
import time
from cotests import bench_batch


async def test0(sleep_time: float = .02):
    await asyncio.sleep(sleep_time)
async def test1():
    await test0(.01)
    # return test0(.01)
def test2():
    time.sleep(.03)


if __name__ == '__main__':
    bench_batch(
        test0(.05),
        test0,
        test1,
        test2,
        # iterations=10,
        raise_exceptions=True,
    )
