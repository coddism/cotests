from typing import TYPE_CHECKING

from .printer import format_sec_metrix, get_level_prefix
from cotests.exceptions import CoException

if TYPE_CHECKING:
    from ..abstract import AbstractTestCase
    from cotests.typ import RESULT_TUPLE_MULTI


def b_sec_s(ts: float) -> float:
    return ts


def b_sec_m(ts: 'RESULT_TUPLE_MULTI') -> float:
    return ts[0]


class __DecoratorFactory:
    def __init__(self, multi: bool = False):
        if multi:
            self.bs = b_sec_m
        else:
            self.bs = b_sec_s

    def __call__(self, func):
        return self.wrapper(self, func)

    @staticmethod
    def _print_start(cls: 'AbstractTestCase', **kwargs):
        level = kwargs.get('level', 0)
        print(f'{get_level_prefix(level)} * {cls.name}:', end='', flush=True)

    @staticmethod
    def wrapper(self: '__DecoratorFactory', func):
        raise NotImplementedError


class SyncDecoratorFactory(__DecoratorFactory):
    @staticmethod
    def wrapper(self: '__DecoratorFactory', func):
        def w(cls: 'AbstractTestCase', *args, **kwargs):
            self._print_start(cls, **kwargs)
            try:
                ts = func(cls, *args, **kwargs)
            except Exception as e_:
                print(f'error: {e_}')
                raise CoException([e_], cls.name)
            else:
                print(f'ok - {format_sec_metrix(self.bs(ts))}')
                return ts

        return w


class AsyncDecoratorFactory(__DecoratorFactory):
    @staticmethod
    def wrapper(self: '__DecoratorFactory', func):
        async def wa(cls: 'AbstractTestCase', *args, **kwargs):
            self._print_start(cls, **kwargs)
            try:
                ts = await func(cls, *args, **kwargs)
            except Exception as e_:
                print(f'error: {e_}')
                raise CoException([e_], cls.name)
            else:
                print(f'ok - {format_sec_metrix(self.bs(ts))}')
                return ts

        return wa
