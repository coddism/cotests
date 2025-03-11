import inspect
from time import perf_counter
from typing import Optional, Callable


def bench_decorator(func):
    def wrapper(*args, **kwargs):
        bench_start = perf_counter()
        func(*args, **kwargs)
        return perf_counter() - bench_start

    return wrapper


def bench_decorator_async(func, *_):
    async def wrapper(*args, **kwargs):
        bench_start = perf_counter()
        await func(*args, **kwargs)
        return perf_counter() - bench_start

    return wrapper


class TestCaseExt:
    @staticmethod
    def __empty_function(*_, **__):
        ...

    def __init__(self,
                 pre_test: Optional[Callable] = None,
                 post_test: Optional[Callable] = None,
                 ):
        self.pre_test = pre_test or self.__empty_function
        self.post_test = post_test or self.__empty_function
        self.is_async = False
        if pre_test or post_test:
            for x in (pre_test, post_test):
                self.__check_function(x)
            self.decor = self.__with_prepost
            self.decor_async = self.__with_prepost_async
        else:
            self.decor = bench_decorator
            self.decor_async = bench_decorator_async

    def __check_function(self, x):
        if x:
            if inspect.iscoroutine(x):
                raise Exception('Coroutine for pre-post test')
            if inspect.iscoroutinefunction(x):
                self.is_async = True
            elif not (inspect.isfunction(x) or inspect.ismethod(x)):
                raise Exception(f'Bad function {x}')

    def __with_prepost(self, func):
        def wrapper(*args, **kwargs):
            self.pre_test()
            res = bench_decorator(func)(*args, **kwargs)
            self.post_test()
            return res

        return wrapper

    def __with_prepost_async(self, func, asynch: bool = True):
        async def wrapper(*args, **kwargs):
            if inspect.iscoroutinefunction(self.pre_test):
                await self.pre_test()
            else:
                self.pre_test()

            if asynch:
                res = await bench_decorator_async(func)(*args, **kwargs)
            else:
                res = bench_decorator(func)(*args, **kwargs)

            if inspect.iscoroutinefunction(self.post_test):
                await self.post_test()
            else:
                self.post_test()
            return res

        return wrapper


__all__ = (TestCaseExt,)
