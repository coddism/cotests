import asyncio
import inspect
from time import perf_counter
from typing import (Callable, Optional, Tuple, Any, Set, Mapping, Iterator,
                    Iterable, List, Union, Coroutine, Awaitable, TYPE_CHECKING)

from .case import TestCase, CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase
from .co_test_args import CoTestArgs
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
                 tests,
                 global_args: Optional['TestArgs'] = None,
                 global_kwargs: Optional['TestKwargs'] = None,
                 personal_args: Optional[Iterable['TestArgs']] = None,
                 personal_kwargs: Optional[Iterable['TestKwargs']] = None,
                 ):
        self.__cta = CoTestArgs(
            personal_args,
            personal_kwargs,
            global_args,
            global_kwargs,
        )

        self.__t_tests: List[Tuple] = []
        self.__has_coroutines = False

        for test in tests:
            self.__add(test)
            # print(
            #     inspect.isfunction(test),
            #     inspect.iscoroutine(test),
            #     inspect.isawaitable(test),
            #     inspect.iscoroutinefunction(test),
            # )

    @property
    def has_coroutines(self) -> bool:
        return self.__has_coroutines

    def __bool__(self):
        return len(self.__t_tests) != 0

    def __len__(self):
        return len(self.__t_tests)

    def __iter__(self) -> Iterator[Tuple[str, TestCase]]:
        for test in self.__t_tests:
            if len(test[2]) == 1:
                yield (test[1].__name__,
                       test[0](test[1], *test[2][0][0], **test[2][0][1]))
            else:
                for i, (a, kw) in enumerate(test[2]):
                    yield (f'{test[1].__name__}:{i}',
                           test[0](test[1], *a, **kw))

    def __add(self, test: 'InTest', *args, **kwargs):
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
                    raise ValueError(f'Unsupported type for InTest: {type(ti)}')

            self.__add(f, *a_, **kw_)
        else:
            if inspect.iscoroutine(test):
                tc = CoroutineTestCase
                self.__has_coroutines = True
            elif inspect.iscoroutinefunction(test):
                tc = CoroutineFunctionTestCase
                self.__has_coroutines = True
            elif inspect.isfunction(test):
                tc = FunctionTestCase
            else:
                raise ValueError(f'Unknown test: {test}')

            # add test
            # print('-------------------\nadd test:', tc)
            # print('AK', args, kwargs)
            pa = self.__cta.get(args, kwargs)
            # for p in pa:
            #     print('  ', p)
            self.__t_tests.append((tc, test, pa))


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
        if global_args and not isinstance(global_args, (List, Tuple, Set)):
            print('Better to use for args: list, tuple, set')

        t = Tester(
            tests,
            global_args=global_args,
            global_kwargs=global_kwargs,
            personal_args=personal_args,
            personal_kwargs=personal_kwargs,
        )

        c = super().__new__(cls)
        c.__init__(
            tester=t,
        )
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
        self.__tester = kwargs['tester']

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
