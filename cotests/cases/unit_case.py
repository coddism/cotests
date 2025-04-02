import unittest
from typing import Type, TextIO
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

    def run(self, stream: TextIO):
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=stream,
        )
        runner.run(self.__suite)
