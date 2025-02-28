from typing import TYPE_CHECKING, Callable, Tuple, Any, Mapping, Iterable, Union, Coroutine, List, Type, Awaitable

TestFunction = Union[Callable, Coroutine]
# TestArgs = Union[Tuple[Any,...], List[Any], Set[Any]]
TestArgs = Iterable[Any]
TestKwargs = Mapping[str, Any]
TestTuple = Tuple[TestFunction, TestArgs, TestKwargs]
CoArgsList = List[Tuple['TestArgs', 'TestKwargs']]
PrePostTest = Callable[[], Union[None, Awaitable[None]]]
RunResult = Union[None, Awaitable[None]]

if TYPE_CHECKING:
    import sys
    from . import AbstractCoCase

    if sys.version_info[:2] >= (3, 11):
        from typing import Unpack
    else:
        from typing_extensions import Unpack

    InTestTuple = Tuple[TestFunction, Unpack[Tuple[Any, ...]]]
    InTest = Union[TestFunction, InTestTuple, AbstractCoCase, Type[AbstractCoCase], 'AbstractTestCase']


class CoException(Exception):
    def __init__(self, errors: List):
        self.__errors = errors


class AbstractTestCase:
    is_async: bool
    name: str

    def run_test(self, *, level: int = 0):
        raise NotImplementedError
    def run_bench(self, iterations: int, *, level: int = 0):
        raise NotImplementedError

