class AbstractTestCase:
    is_async: bool
    name: str

    def run_test(self, *, level: int = 0):
        raise NotImplementedError
    def run_bench(self, iterations: int, *, level: int = 0):
        raise NotImplementedError


class AbstractTestGroup(AbstractTestCase):
    is_empty: bool
