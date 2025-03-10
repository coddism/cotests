import asyncio
import time
from cotests import bench_batch


async def test_0(sleep_time: float = .02):
    await asyncio.sleep(sleep_time)
def test_1(sleep_time: float = .03):
    time.sleep(sleep_time)


if __name__ == '__main__':
    fun_async = (
        test_0,
        (test_0, (.15,)),  # set custom args
    )
    fun_sync = (
        test_1,
        (test_1, (.12,)),
    )

    bench_batch(*fun_sync, name='ONLY SYNC')

    bench_batch(
        *fun_async,  # coroutinefunctions can reuse
        test_0(.05),  # coroutine with reuse - error
        iterations=2,
        name='ASYNC W\T LOOP',
    )

    async def main():
        # if `bench_batch()` with coroutines run in running loop, you need to use `await`
        await bench_batch(
            *fun_async,
            *fun_sync,
            test_0(.05),  # coroutine without reuse - ok
            name='ASYNC WITH LOOP',
        )
        # without coroutines = without await
        bench_batch(*fun_sync, name='SYNC WITH LOOP',)
    asyncio.run(main())
