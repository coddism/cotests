import io
import sys


class CoLoggerStream(io.StringIO):
    CHR = '¦ '
    # terminator = '\n'

    def __init__(self, level: int = 0):
        super().__init__()
        self.__prefix = self.CHR * level
        self.__new_line = True
        self.__stream = sys.stdout

    def write(self, msg: str):
        if self.__new_line:
            print(self.__prefix, end='')
            self.__new_line = False
        print(msg, end='')
        if msg == '\n':
            self.__new_line = True

    def writeln(self, msg: str):
        self.write(msg + '\n')
        self.__new_line = True

    def flush(self):
        print('', end='', flush=True)


class CoLogger:
    CHR = '¦ '

    def __init__(self, level: int = 0):
        self.__prefix = ''
        self.__stream = CoLoggerStream(level)
        self.level = level

    @property
    def level(self):
        return self.__level

    @property
    def child(self):
        return CoLogger(self.level+1)

    @property
    def stream(self):
        return self.__stream

    @level.setter
    def level(self, val: int):
        assert val >= 0
        self.__level = val
        self.__prefix = self.CHR * val

    def log(self, msg: str):
        self.stream.writeln(msg)

    def __call__(self, *args, **kwargs): self.log(*args, **kwargs)
    def debug(self, *args, **kwargs): self.log(*args, **kwargs)
    def info(self, *args, **kwargs): self.log(*args, **kwargs)


logger = CoLogger()

__all__  = ('logger', 'CoLogger', )
