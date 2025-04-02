from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from cotests.logger import CoLogger


class ProgressBarPrinter:
    PRINT_CHAR: str = '.'

    def __init__(self,
                 iterations_count: int,
                 *,
                 logger: 'CoLogger',
                 max_width: int = 50,
                 ):
        self.__ic = iterations_count
        self.__max_width = max_width
        self.__logger = logger

    def __print(self):
        self.__logger.write_raw(self.PRINT_CHAR)
        self.__logger.flush()

    def __counter(self) -> Iterator[None]:
        print_every_val = self.__ic / self.__max_width
        pv = .0
        pv_next = 0

        for i in range(self.__ic):
            yield
            if i == pv_next:
                self.__print()
                pv += print_every_val
                pv_next = int(pv)

    def __counter_every(self) -> Iterator[None]:
        for i in range(self.__ic):
            yield
            self.__print()

    def __iter__(self):
        if self.__ic <= self.__max_width:
            return self.__counter_every()
        else:
            return self.__counter()


__all__ = ('ProgressBarPrinter',)
