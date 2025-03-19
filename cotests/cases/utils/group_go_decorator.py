from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable

from cotests.exceptions import CoException
from .ttr import try_to_run

if TYPE_CHECKING:
    from ..abstract import AbstractTestGroup


class GoDecor:
    def __init__(self, group: 'AbstractTestGroup', func: Callable):
        self.__group = group
        self.__func = func

    def __call__(self, *args, **kwargs):
        if self.__group.is_async:
            return self.__async(*args, **kwargs)
        else:
            self.__sync(*args, **kwargs)

    @contextmanager
    def __ctxm(self):
        try:
            yield
        except CoException as ce:
            ce.print_errors()
        # except Exception as e:
        #     ce = CoException([e], self.__group.name)
        #     ce.print_errors()

    def __sync(self, *args, **kwargs):
        with self.__ctxm():
            self.__func(*args, **kwargs)

    def __async(self, *args, **kwargs):
        async def _async_wrapper():
            with self.__ctxm():
                await self.__func(*args, **kwargs)
        return try_to_run(_async_wrapper())
