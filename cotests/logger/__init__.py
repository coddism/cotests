import io
from typing import Iterable


class CoLoggerLine:
    @staticmethod
    def log(msg: str): print(msg, end='', flush=True)

    @staticmethod
    def finish(msg: str = ''): print(msg)


class CoLoggerStream(io.StringIO):
    CHR = '¦ '

    def __init__(self, level: int = 0):
        super().__init__()
        self.__prefix = self.CHR * level
        self.__new_line = True

    def write(self, msg: str):
        if self.__new_line:
            print(self.__prefix, end='')
            self.__new_line = False
        print(msg, end='')
        if msg == '\n':
            self.__new_line = True
    def flush(self):
        print('', end='', flush=True)


class CoLogger:
    CHR = '¦ '
    # terminator = '\n'

    def __init__(self, level: int = 0):
        self.__prefix = ''
        self.level = level

    @property
    def level(self):
        return self.__level

    @property
    def child(self):
        return CoLogger(self.level+1)

    @property
    def stream(self):
        return CoLoggerStream(self.level)

    @level.setter
    def level(self, val: int):
        assert val >= 0
        self.__level = val
        self.__prefix = self.CHR * val

    @property
    def line(self):
        print(self.__prefix, end='')
        return CoLoggerLine

    def log(self, msg: str):
        print(self.__prefix + msg)

    def log_iter(self, msgs: Iterable[str]):
        print(self.__prefix, end='')
        try:
            for msg in msgs:
                print(msg, end='', flush=True)
        finally:
            print()

    def __call__(self, *args, **kwargs): self.log(*args, **kwargs)
    def debug(self, *args, **kwargs): self.log(*args, **kwargs)
    def info(self, *args, **kwargs): self.log(*args, **kwargs)


logger = CoLogger()

__all__  = ('logger', 'CoLogger', )
