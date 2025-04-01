import sys

from cotests import CoTestCase


_STREAM = sys.stdout


class LoggingTestCase(CoTestCase):
    TERMINATOR = '\n'

    def __init__(self):
        self.__new_line = True
        self.__prefix = '| '

    def write(self, msg: str):
        if self.__new_line:
            _STREAM.write(self.__prefix)
        lines = iter(msg.splitlines(True))

        line = next(lines)
        _STREAM.write(line)

        for line in lines:
            _STREAM.write(self.__prefix + line)

        self.__new_line = line.endswith(self.TERMINATOR)

    def _test_logger00(self):
        _STREAM.write('test' + '_logger0' + '\n')

    def _test_logger01(self):
        _STREAM.write('test')
        _STREAM.write('_logger0')
        _STREAM.write('\n')

    def _test_logger12(self, msg: str):
        self.write(f'* {msg}:')

    def _test_logger11(self, msg: str):
        _STREAM.write(self.__prefix + f'* {msg}:')
        self.__new_line = False

    def test_logger20(self, msg: str):
        self.write(msg)

    def test_logger21(self, msg: str):
        _STREAM.write(msg)


LoggingTestCase().run_bench(
    # global_args=('RUN NEW FUN\n * \n {self.__runner.test.name}:',),
    global_args=('tn',),
    iterations=100,
)
