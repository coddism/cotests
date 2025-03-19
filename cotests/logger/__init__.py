from typing import Iterable

class CoLogger:
    CHR = '¦ '

    def __init__(self, level: int = 0):
        self.__pref = ''
        self.level = level

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, val: int):
        assert val >= 0
        self.__level = val
        if val > 0:
            self.__pref = self.CHR * val

    def __call__(self, msg: str):
        self.log(msg)

    def log(self, msg: str):
        print(self.__pref + msg)

    def log_iter(self, msgs: Iterable[str]):
        print(self.__pref, end='')
        try:
            for msg in msgs:
                print(msg, end='', flush=True)
        finally:
            print()

    def debug(self, *args, **kwargs): self.log(*args, **kwargs)
    def info(self, *args, **kwargs): self.log(*args, **kwargs)


logger = CoLogger()
logger.log('LOGGER INIT')

__all__  = ('logger', 'CoLogger', )
