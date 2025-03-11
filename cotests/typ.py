from typing import TYPE_CHECKING, Callable, Tuple, Any, Mapping, Iterable, Union, Coroutine, List, Type, Awaitable


# RESULT_TUPLE_SINGLE = Tuple[float]
RESULT_TUPLE_MULTI = Tuple[float, float, float, float]

TestFunction = Union[Callable, Coroutine]
# TestArgs = Union[Tuple[Any,...], List[Any], Set[Any]]
TestArgs = Iterable[Any]
TestKwargs = Mapping[str, Any]
# TestTuple = Tuple[TestFunction, TestArgs, TestKwargs]
CoArgsList = List[Tuple['TestArgs', 'TestKwargs']]
PrePostTest = Callable[[], Union[None, Awaitable[None]]]


if TYPE_CHECKING:
    import sys
    from cotests.case.abstract import AbstractCoCase
    from cotests.cases.abstract import AbstractTestCase

    if sys.version_info[:2] >= (3, 11):
        from typing import Unpack
    else:
        from typing_extensions import Unpack

    InTestTuple = Tuple[TestFunction, Unpack[Tuple[Any, ...]]]
    InTest = Union[TestFunction, InTestTuple, AbstractCoCase, Type[AbstractCoCase], AbstractTestCase]
