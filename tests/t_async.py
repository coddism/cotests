import asyncio
import time
from cotests import bench_batch


async def test0(sleep_time: float = .02):
    await asyncio.sleep(sleep_time)
def test1(sleep_time: float = .03):
    time.sleep(sleep_time)


if __name__ == '__main__':
    fun_async = (
        test0,
        (test0, (.15,)),  # set custom args
    )
    fun_sync = (
        test1,
        (test1, (.12,)),
    )

    print(' ---------------ONLY SYNC-------------------')
    bench_batch(*fun_sync)

    print(' ---------------ASYNC W\T LOOP--------------')
    bench_batch(
        *fun_async,  # coroutinefunctions can reuse
        test0(.05),  # coroutine with reuse - error
        iterations=2,
    )

    async def main():
        print(' ---------------ASYNC WITH LOOP-------------')
        # if `bench_batch()` with coroutines run in running loop, you need to use `await`
        await bench_batch(
            *fun_async,
            *fun_sync,
            test0(.05),  # coroutine without reuse - ok
        )
        # without coroutines = without await
        bench_batch(*fun_sync)
    asyncio.run(main())
