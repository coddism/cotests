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

    def write(self, msg: str):
        for line in msg.splitlines(True):
            self.__write_1line(line)

    def flush(self):
        _STREAM.flush()

    def __write_1line(self, line: str):  # no-multiline
        if self.__new_line:
            _STREAM.write(self.__prefix)
        _STREAM.write(line)
        self.__new_line = line.endswith(self.TERMINATOR)

    def writeln(self, msg: str):
        self.write(msg + self.TERMINATOR)


logger = CoLogger()

__all__  = ('logger', 'CoLogger', )
