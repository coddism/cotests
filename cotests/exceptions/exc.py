from typing import List, Tuple, Iterator


class CoException(Exception):
    def __init__(self,
                 errors: List[Exception],
                 where: str,
                 ):
        self.__errors = errors
        self.__where = where

    @property
    def errors(self):
        return self.__errors_iter(())

    def __errors_iter(
            self,
            parents: Tuple[str, ...]
    ) -> Iterator[Tuple[Tuple[str, ...], Exception]]:
        if self.__errors:
            for e in self.__errors:
                if isinstance(e, CoException):
                    yield from e.__errors_iter((*parents, e.__where))
                else:
                    yield parents, e


class InitGroupErrors(CoException):
    def __init__(self, errors: List[Exception]):
        super().__init__(errors, '__init__')


class UnknownTestTypeError(Exception):
    ...


__all__ = ('CoException', 'InitGroupErrors', 'UnknownTestTypeError',)
