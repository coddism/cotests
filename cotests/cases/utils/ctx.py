from time import perf_counter
from contextlib import contextmanager
from typing import TYPE_CHECKING, List, Iterable

from cotests.exceptions import CoException
from .printer import get_level_prefix, format_sec_metrix, print_test_results

if TYPE_CHECKING:
    from ..abstract import AbstractTestGroup


class TestCTX:
    _GREETINGS: str = 'CoTest'

    def __init__(self, cls: 'AbstractTestGroup', level: int):
        self._group = cls
        self._level = level
        self.__pref = get_level_prefix(level)
        self.__start: float = .0
        self.__finish: float = .0
        self.__errors = []

    def add_error(self, e: Exception):
        self.__errors.append(e)

    def __enter__(self):
        self.__pre()
        self.__start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__finish = perf_counter() - self.__start
        self._final_print()

        if self.__errors:
            raise CoException(self.__errors, self._group.name)

        if exc_type:
            print('EXC!')
            print(exc_type, exc_value, exc_traceback)

    @contextmanager
    def ctx(self):
        try:
            yield
        except Exception as e_:
            self.add_error(e_)

    def __pre(self):
        print(self.__pref)
        print(f'{self.__pref}⌌', '-' * 14, f' Start {self._GREETINGS} ', self._group.name, '-' * 14, sep='')
        if self._group.is_empty:
            print(f'{self.__pref}⌎ Tests not found')
            raise CoException(
                [Exception('Tests not found')],
                where=self._group.name
            )

    def _final_print(self):
        print(f'{self.__pref}⌎-- Full time: {format_sec_metrix(self.__finish)}')


class BenchCTX(TestCTX):
    _GREETINGS: str = 'CoBench'
    def __init__(self, *args, iterations: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.__exp = []
        self.__iterations = iterations
        if iterations == 1:
            self.__headers = ('time',)
            self.__calc = lambda b: b
        else:
            self.__headers = ('full', 'max', 'min', 'avg')
            self.__calc = self.__calc_multi

    @staticmethod
    def __calc_multi(benches: List[float]) -> Iterable[float]:
        s = sum(benches)
        mx, mn, avg = (
            max(benches),
            min(benches),
            s / len(benches),
        )
        return s, mx, mn, avg

    def add_exp(self, test_name: str, benches: List[float]):
        assert len(benches) == self.__iterations
        self.__exp.append((test_name, *self.__calc(benches)))

    def _final_print(self):
        pref_1 = get_level_prefix(self._level + 1)
        for str_row in print_test_results(
            self.__exp,
            headers=self.__headers,
        ):
            print(pref_1, str_row)
        super()._final_print()


__all__ = (TestCTX, BenchCTX)
