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

    fun_async = (
        test0,
        (test0, (.15,)),
        test1,
    )
    fun_sync = (
        test2,
        (test2, .12),
    )
    fun_full = (*fun_async, *fun_sync)

    print(' ---------------ONLY SYNC-------------------')
    bench_batch(
        *fun_sync,
        (test2, .12, 45)
    )
    bench_batch(
        *fun_sync,
        iterations=3
    )

    print(' ---------------ASYNC W\T LOOP--------------')
    bench_batch(*fun_async, test0(.05))
    bench_batch(
        *fun_full,
        iterations=2,
    )

    async def main():
        print(' ---------------ASYNC WiTH LOOP-------------')
        await bench_batch(*fun_full)
    asyncio.run(main())
