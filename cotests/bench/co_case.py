import inspect


def _case_predicate(obj):
    return ((inspect.ismethod(obj) or inspect.isfunction(obj))
            and obj.__name__.startswith('test_'))


class AbstractCoCase:
    def get_tests(self):
        return (
            x[1] for x in inspect.getmembers(self, _case_predicate)
        )
