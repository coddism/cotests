import asyncio
import time
from cotests import bench_batch, CoTestGroup

def test_0(): print('T0', end='-')
def test_1(): print('T1', end='-')
async def atest_0(): print('T0', end='-')
async def atest_1(): print('T1', end='-')

async def rba():
    await asyncio.sleep(.1)
    print('B', end='~')

def rb():
    time.sleep(.1)
    print('B', end='-')
def ra():
    time.sleep(.1)
    print('A', end=' ')

tests = (test_0, test_1, atest_0, atest_1)
g0 = CoTestGroup(*tests, pre_test=rb, post_test=ra, name='SYNC')
g1 = CoTestGroup(*tests, pre_test=rba, post_test=ra, name='ASYNC')

if __name__ == '__main__':
    bench_batch(
        *tests,
        pre_test=rb,
        post_test=ra,
        iterations=2,
    )

    bench_batch(
        *tests,
        pre_test=rba,
        post_test=ra,
        iterations=2,
    )
