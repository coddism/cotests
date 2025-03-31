import io
import sys


class CoLoggerStream(io.StringIO):
    CHR = '¦ '
    TERMINATOR = '\n'

    def __init__(self, level: int = 0):
        super().__init__()
        self.__prefix = self.CHR * level
        self.__new_line = True
        self.__stream = sys.stdout

    def write(self, msg: str):
        if self.__new_line:
            self.__stream.write(self.__prefix)
            self.__new_line = False
        self.__stream.write(msg)
        if msg == self.TERMINATOR:
            self.__new_line = True

    def writeln(self, msg: str):
        self.write(msg + self.TERMINATOR)
        self.__new_line = True

    def flush(self):
        self.__stream.flush()


class CoLogger:

    def __init__(self, level: int = 0):
        assert level >= 0
        self.__stream = CoLoggerStream(level)
        self.__level = level

    @property
    def child(self):
        return CoLogger(self.__level+1)

    @property
    def stream(self):
        return self.__stream

    def log(self, msg: str):
        self.stream.writeln(msg)

    def __call__(self, *args, **kwargs): self.log(*args, **kwargs)
    def debug(self, *args, **kwargs): self.log(*args, **kwargs)
    def info(self, *args, **kwargs): self.log(*args, **kwargs)


logger = CoLogger()

__all__  = ('logger', 'CoLogger', )
