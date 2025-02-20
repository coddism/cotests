import asyncio
import inspect
from time import perf_counter
from typing import (Callable, Optional, Tuple, Any, Set, Mapping, Iterator,
                    Iterable, List, Union, Coroutine, Awaitable, TYPE_CHECKING)

from .case import TestCase, CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase
from ..utils import print_test_results, format_sec_metrix

if TYPE_CHECKING:
    import sys
    if sys.version_info[:2] >= (3, 11):
        from typing import Unpack
    else:
        from typing_extensions import Unpack

    TestFunction = Union[Callable, Coroutine]
    InTestTuple = Tuple[TestFunction, Unpack[Tuple[Any, ...]]]
    InTest = Union[TestFunction, InTestTuple]
    # TestArgs = Union[Tuple[Any,...], List[Any], Set[Any]]
    TestArgs = Iterable[Any]
    TestKwargs = Mapping[str, Any]
    TestTuple = Tuple[TestFunction, TestArgs, TestKwargs]


class Tester:

    def __init__(self,
                 global_args: Optional['TestArgs'] = None,
                 global_kwargs: Optional['TestKwargs'] = None,
                 personal_args: Optional[Iterable['TestArgs']] = None,
                 personal_kwargs: Optional[Iterable['TestKwargs']] = None,
    ):
        self.__t_tests: List[Tuple] = []
        # self.__tests: List[TestCase] = []
        self.__global_args = global_args or ()
        self.__global_kwargs = global_kwargs or {}
        self.__personal_args = personal_args or []
        self.__personal_kwargs = personal_kwargs or []
        self.__has_coroutines = False

    @property
    def has_coroutines(self) -> bool:
        return self.__has_coroutines

    def __bool__(self):
        return len(self.__t_tests) != 0

    def __len__(self):
        return len(self.__t_tests)

    def __iter__(self) -> Iterator[Tuple[str, TestCase]]:
        for test in self.__t_tests:
            if isinstance(test[3], Iterator):
                for i, a in enumerate(test[3]):
                    yield (f'{test[1].__name__}:{i}',
                           test[0](test[1], *test[2], **a))
            elif isinstance(test[2], Iterator):
                # todo 2&3
                for i, a in enumerate(test[2]):
                    yield (f'{test[1].__name__}:{i}',
                           test[0](test[1], *a, **test[3]))
            else:
                yield (test[1].__name__,
                       test[0](test[1], *test[2], **test[3]))

    def add(self, test: 'InTest', *args, **kwargs):
        def merge_args():
            if self.__personal_args:
                if args or self.__global_args:
                    raise Exception('PA args conflict')
                fa = self.__personal_args.__iter__()
            else:
                if self.__global_args and args:
                    raise Exception('args conflict')
                fa = self.__global_args or args or ()

            if self.__global_kwargs and kwargs:
                fkw = {**self.__global_kwargs, **kwargs}
            else:
                fkw = self.__global_kwargs or kwargs or {}
            if self.__personal_kwargs:
                bkw = fkw
                fkw = ({**x, **bkw} for x in self.__personal_kwargs)

            return fa, fkw

        if isinstance(test, tuple):
            if args or kwargs:
                raise Exception('InTest format Error')
            assert len(test) > 0
            f = test[0]
            a_, kw_ = (), {}
            for ti in test[1:]:
                if isinstance(ti, tuple):
                    if a_: raise ValueError('TestItem args conflict')
                    a_ = ti
                elif isinstance(ti, dict):
                    if kw_: raise ValueError('TestItem kwargs conflict')
                    kw_ = ti
                else:
                    raise ValueError('Unknown type')

            self.add(f, *a_, **kw_)
        else:
            a, k = merge_args()
            if inspect.iscoroutine(test):
                if a or k:
                    raise ValueError('Coroutine with args')
                tc = CoroutineTestCase
            elif inspect.iscoroutinefunction(test):
                tc = CoroutineFunctionTestCase
            elif inspect.isfunction(test):
                tc = FunctionTestCase
            else:
                raise ValueError(f'Unknown test: {test}')
            self.__t_tests.append((tc, test, a, k))


class Bencher:

    def __new__(
            cls,
            *tests: 'InTest',
            iterations: int = 1,
            global_args: Optional['TestArgs'] = None,
            global_kwargs: Optional['TestKwargs'] = None,
            personal_args: Optional[Iterable['TestArgs']] = None,
            personal_kwargs: Optional[Iterable['TestKwargs']] = None,
            raise_exceptions: bool = False,
    ) -> Union[None, Awaitable[None]]:
        print('\n', '-' * 14, 'Start Bencher', '-' * 14)
        if not isinstance(global_args, (List, Tuple, Set)):
            print('Better to use for args: list, tuple, set')
        if global_args and personal_args:
            raise Exception('Global & personal args conflict')

        c = super().__new__(cls)
        c.__init__(
            global_args=global_args,
            global_kwargs=global_kwargs,
            personal_args=personal_args,
            personal_kwargs=personal_kwargs,
        )
        c.add_tests(tests)
        t = c.run_tests(iterations, raise_exceptions)
        if inspect.iscoroutine(t):
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

    def __init__(self, *_, **kwargs):
        # print('INIT')
        self.__tester = Tester(
            *(kwargs.get(x) for x in (
                'global_args',
                'global_kwargs',
                'personal_args',
                'personal_kwargs',
            ))
        )

    def add_tests(self, tests: Iterable['InTest']):
        for test in tests:
            self.__tester.add(test)
            # print(
            #     inspect.isfunction(test),
            #     inspect.iscoroutine(test),
            #     inspect.isawaitable(test),
            #     inspect.iscoroutinefunction(test),
            # )

    def run_tests(self,
                  iterations: int = 1,
                  raise_exceptions: bool = False,
                  ):
        if not self.__tester:
            print('Tests not found')
            return
        single_run = iterations == 1

        def print_res(rexp: list):
            print_test_results(
                rexp,
                headers=('time',) if single_run else ('full', 'max', 'min', 'avg'),
            )

        if self.__tester.has_coroutines:
            async def do_async():
                a_start = perf_counter()

                exp_ = []
                for fun_name, test in self.__tester:
                    # fun_name = test.name
                    print(f' * {fun_name}:', end='', flush=True)
                    try:
                        s = test.run(iterations)
                        if inspect.iscoroutine(s):
                            s = await s
                    except Exception as e:
                        if raise_exceptions:
                            raise
                        print(f'error: {e}')
                    else:
                        # print(f'ok')
                        print(f'ok - {format_sec_metrix(s[0])}')
                        exp_.append((fun_name, *s))

                aft = perf_counter() - a_start
                print_res(exp_)
                print(f'Full time: {format_sec_metrix(aft)}')

            return do_async()
        else:
            def g_sync():
                for fun_name, test in self.__tester:
                    # fun_name = test.name
                    print(f' * {fun_name}:', end='', flush=True)
                    try:
                        s = test.run(iterations)
                    except Exception as e:
                        if raise_exceptions:
                            raise
                        print(f'error: {e}')
                    else:
                        # print(f'ok')
                        print(f'ok - {format_sec_metrix(s[0])}')
                        yield (fun_name, *s)

            s_start = perf_counter()
            exp = [x for x in g_sync()]
            sft = perf_counter() - s_start
            print_res(exp)
            print(f'Full time: {format_sec_metrix(sft)}')
