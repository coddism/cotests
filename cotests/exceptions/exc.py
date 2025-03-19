from typing import List, Tuple


class CoException(Exception):
    def __init__(self,
                 errors: List[Exception],
                 where: str,
                 ):
        self.__errors = errors
        self.__where = where

    # todo arg logger / or move
    def print_errors(self):
        if self.__errors:
            print('! Errors:')
            self._r_print(())
            print('⌎' + '-' * 28)

    def _r_print(self,
                 parents: Tuple[str, ...]):
        for e in self.__errors:
            if isinstance(e, CoException):
                e._r_print((*parents, e.__where))
            else:
                print('! *', ' / '.join(parents), '\n!  ', type(e).__name__, ':', e)


class InitGroupErrors(CoException):
    def __init__(self, errors: List[Exception]):
        super().__init__(errors, '__init__')


class UnknownTestTypeError(Exception):
    ...


__all__ = ('CoException', 'InitGroupErrors', 'UnknownTestTypeError',)
