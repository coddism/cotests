from typing import TYPE_CHECKING

from .abstract import AbstractRunner

if TYPE_CHECKING:
    from ..unit_case import UnitTestCase


class UnitCaseRunner(AbstractRunner):
    test: 'UnitTestCase'

    def run(self):
        start_line = '-' * 14
        block_header = f'{start_line} UnitTest {self.test.name} {start_line}'

        self.logger.log('')
        self.logger.log(
            f'⌌{block_header}'
        )

        self.test.run(self.logger.child)

        self.logger.log('⌎' + '-'*len(block_header))
