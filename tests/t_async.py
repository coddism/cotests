import asyncio
import time
from cotests import bench_batch


async def test0(sleep_time: float = .02):
    await asyncio.sleep(sleep_time)
async def test1():
    await test0(.01)
    # return test0(.01)
def test2(sleep_time: float = .03):
    time.sleep(sleep_time)

if __name__ == '__main__':
    print("START!")

    bench_batch(
        test0(.05),
        test0,
        (test0, (.15,)),
        test1,
        test2,
        (test2, .12),
        # iterations=2,
        # raise_exceptions=True,
        # with_args=(.4,),
    )
