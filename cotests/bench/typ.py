from typing import TYPE_CHECKING, Callable, Tuple, Any, Mapping, Iterable, Union, Coroutine, List, Type, Awaitable


RESULT_TUPLE_SINGLE = Tuple[float]
RESULT_TUPLE_MULTI = Tuple[float, float, float, float]

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
    def __init__(self,
                 errors: List[Exception],
                 where: str,
                 ):
        self.__errors = errors
        self.__where = where

    def print_errors(self):
        if self.__errors:
            print('! Errors:')
            self._r_print(())
            print('⌎' + '-' * 28)

    def _r_print(self,
                 parents: Tuple[str, ...]):
        for e in self.__errors:
            if isinstance(e, CoException):
                e._r_print((*parents, e.__where))
            else:
                print('! *', ' / '.join(parents), '\n!  ', type(e).__name__, ':', e)
