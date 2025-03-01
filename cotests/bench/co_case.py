import inspect
from typing import Callable, List


def _case_predicate(obj):
    return ((inspect.ismethod(obj) or inspect.isfunction(obj))
            and obj.__name__.startswith('test_'))


class AbstractCoCase:
    def get_tests(self) -> List[Callable]:
        return [x[1] for x in inspect.getmembers(self, _case_predicate)]

    @property
    def name(self) -> str:
        return type(self).__name__
