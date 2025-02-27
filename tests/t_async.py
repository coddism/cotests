import asyncio
import time
from cotests import bench_batch, CoTestGroup


async def test0(sleep_time: float = .02):
    await asyncio.sleep(sleep_time)
def test1(sleep_time: float = .03):
    time.sleep(sleep_time)
def test2(*_):
    raise Exception('test2')


ga = CoTestGroup(
        test0,
        (test0, (.15,)),  # set custom args
        name='ASYNC',
    )
gs = CoTestGroup(
    test1,
    (test1, (.12,)),
    test2,
    name='SYNC'
)


if __name__ == '__main__':
    fun_async = (
        test0,
        (test0, (.15,)),  # set custom args
    )
    fun_sync = (
        test1,
        (test1, (.12,)),
    )

    bench_batch(
        ga,
        gs,
        CoTestGroup(name='Empty'),
        iterations=4
    )

    bench_batch(*fun_sync, name='ONLY SYNC')

    bench_batch(
        *fun_async,  # coroutinefunctions can reuse
        test0(.05),  # coroutine with reuse - error
        iterations=2,
        name='ASYNC W\T LOOP',
    )

    async def main():
        # if `bench_batch()` with coroutines run in running loop, you need to use `await`
        await bench_batch(
            *fun_async,
            *fun_sync,
            test0(.05),  # coroutine without reuse - ok
            name='ASYNC WITH LOOP',
        )
        # without coroutines = without await
        bench_batch(*fun_sync, name='SYNC WITH LOOP',)
    asyncio.run(main())
