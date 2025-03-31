import io
import sys

from typing import Optional


class CoLogger(io.StringIO):
    CHR = '¦ '
    TERMINATOR = '\n'

    def __init__(self, parent: Optional['CoLogger'] = None):
        super().__init__()
        if parent:
            self.__prefix = parent.__prefix + self.CHR
            self.__stream = parent.__stream
        else:
            self.__prefix = ''
            self.__stream = sys.stdout

        self.__new_line = True

    @property
    def child(self):
        return CoLogger(self)

    def write(self, msg: str):
        if self.__new_line:
            self.__stream.write(self.__prefix)
        self.__stream.write(msg)
        self.__new_line = msg.endswith(self.TERMINATOR)

    def writeln(self, msg: str):
        self.write(msg + self.TERMINATOR)

    def flush(self):
        self.__stream.flush()

    def log(self, msg: str):
        self.writeln(msg)

    # def __call__(self, *args, **kwargs): self.log(*args, **kwargs)
    # def debug(self, *args, **kwargs): self.log(*args, **kwargs)
    # def info(self, *args, **kwargs): self.log(*args, **kwargs)


logger = CoLogger()

__all__  = ('logger', 'CoLogger', )
