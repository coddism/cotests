import asyncio
import inspect
from typing import Union, Awaitable


def try_to_run(t) -> Union[None, Awaitable[None]]:
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
