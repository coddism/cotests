import asyncio
import inspect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cotests.typ import RunResult


def try_to_run(t) -> 'RunResult':
    if t and inspect.iscoroutine(t):
        # try to run
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # print('Run in new loop')
            asyncio.run(t)
        else:
            # print('Cannot run. Return coroutine')
            return t
    # else:
    #     print('No coroutines')


async def run_fun(fun):
    if fun is None:
        return
    if inspect.iscoroutine(fun):
        await fun
    else:
        raise ValueError(f'Fun {fun} is not supportable')
