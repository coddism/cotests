import io
import sys


class CoLogger(io.StringIO):
    CHR = '¦ '
    TERMINATOR = '\n'

    def __init__(self, level: int = 0):
        assert level >= 0
        super().__init__()
        self.__level = level
        self.__prefix = self.CHR * level
        self.__new_line = True
        self.__stream = sys.stdout

    @property
    def child(self):
        return CoLogger(self.__level+1)

    def write(self, msg: str):
        if self.__new_line:
            self.__stream.write(self.__prefix)
            self.__new_line = False
        self.__stream.write(msg)
        if msg.endswith(self.TERMINATOR):
            self.__new_line = True

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
