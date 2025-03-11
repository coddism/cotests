from typing import Iterator


class ProgressBarPrinter:
    PRINT_CHAR: str = '.'

    def __init__(self,
                 iterations_count: int,
                 max_width: int = 50,
                 ):
        self.__ic = iterations_count
        self.__max_width = max_width

    def __counter(self) -> Iterator[None]:
        print_every_val = self.__ic / self.__max_width
        pv = .0
        pv_next = 0

        for i in range(self.__ic):
            yield
            if i == pv_next:
                print(self.PRINT_CHAR, end='', flush=True)
                pv += print_every_val
                pv_next = int(pv)

    def __counter_every(self) -> Iterator[None]:
        for i in range(self.__ic):
            yield
            print(self.PRINT_CHAR, end='', flush=True)

    def __iter__(self):
        if self.__ic <= self.__max_width:
            return self.__counter_every()
        else:
            return self.__counter()
