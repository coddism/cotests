from typing import Iterable


class CoLoggerLine:
    @staticmethod
    def log(msg: str): print(msg, end='')

    @staticmethod
    def finish(msg: str = ''): print(msg)


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
logger.log('LOGGER INIT')

__all__  = ('logger', 'CoLogger', )
