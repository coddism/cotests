import unittest
from typing import Type, Tuple
from .abstract import AbstractTestCase
from .runner.unit import UnitCaseRunner


class UnitTestCase(AbstractTestCase):
    is_async = False
    _RUNNER = UnitCaseRunner

    def __init__(self, test: Type[unittest.TestCase]):
        self.name = test.__name__
        loader = unittest.TestLoader()
        self.__suite = unittest.TestSuite(
            loader.loadTestsFromTestCase(test)
        )

    def __prints(self) -> Tuple[str, str]:
        p_len = 50
        block_name = f'UnitTest {self.name} block'
        s_len = (p_len - len(block_name)) // 2
        s_pp = '~'*s_len
        start = f'{s_pp} {block_name} {s_pp}'
        return start, '~'*len(start)

    def run_test(self):
        pp = self.__prints()
        print(pp[0])
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(self.__suite)
        print(pp[1])
