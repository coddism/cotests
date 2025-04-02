import io
import sys

from typing import Optional


_STREAM = sys.stdout


class CoLogger(io.StringIO):
    CHR = '¦ '
    TERMINATOR = '\n'

    def __init__(self, parent: Optional['CoLogger'] = None):
        super().__init__()
        if parent:
            self.__prefix = parent.__prefix + self.CHR
        else:
            self.__prefix = ''

        self.__new_line = True
        self.__child = None

    @property
    def child(self) -> 'CoLogger':
        if self.__child is None:
            self.__child = CoLogger(self)
        return self.__child

    # STD

    def write(self, msg: str):
        # support multi-line messages
        if self.__new_line:
            _STREAM.write(self.__prefix)
        lines = iter(msg.splitlines(True))

        line = next(lines)
        _STREAM.write(line)

        for line in lines:
            _STREAM.write(self.__prefix + line)

        self.__new_line = line.endswith(self.TERMINATOR)

    def flush(self):
        _STREAM.flush()

    # CUSTOM

    def writeln(self, msg: str):
        # self.write(msg + self.TERMINATOR)
        _STREAM.write(self.__prefix + msg + self.TERMINATOR)
        self.__new_line = True

    # RAW

    @staticmethod
    def write_raw(msg: str):
        _STREAM.write(msg)

    def end_line(self, msg: str):
        _STREAM.write(msg + self.TERMINATOR)
        self.__new_line = True

    def new_line(self, msg: str):
        _STREAM.write(self.__prefix + msg)
        self.__new_line = False


logger = CoLogger()

__all__  = ('logger', 'CoLogger', )
