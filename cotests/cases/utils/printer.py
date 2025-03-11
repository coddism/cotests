from math import log10
from typing import Tuple, Optional, List


__METRIX = (
    (60, 'min'),
    (1, 'sec'),
    (.1 ** 3, 'ms'),
    (.1 ** 6, 'µs'),
    (.1 ** 9, 'ns'),
    (.1 ** 12, 'ps'),
    (.1 ** 15, 'fs'),
)

def get_level_prefix(level: int, char: str = '¦ ') -> str:
    return char * level


def get_sec_metrix(sec: float) -> Tuple[float, str]:
    for deci, metr in __METRIX:
        if sec >= deci:
            return deci, metr
    return __METRIX[-1]


def format_sec_metrix(sec: float) -> str:
    deci, metr = get_sec_metrix(sec)
    return f'{sec / deci:.3f} {metr}'


def __float_len(x: float) -> int:
    return int(log10(x)) + 1


def print_test_results(
        exp: List[Tuple[str, float]],
        *,
        headers: Optional[Tuple] = None,
) -> List[str]:
    if not exp:
        return ['! No results.']
        # print('No results.')
        # return

    iter_ = exp.__iter__()
    first = next(iter_)
    max_fn_len = len(first[0])
    minmax = [[m, m] for m in first[1:]]

    if headers:
        assert len(headers) + 1 == len(first)

    res = []

    for i in iter_:
        if len(i[0]) > max_fn_len:
            max_fn_len = len(i[0])
        for im, sec in enumerate(i[1:]):
            if minmax[im][0] > sec:
                minmax[im][0] = sec
            elif minmax[im][1] < sec:
                minmax[im][1] = sec

    multi = []
    row_format = ''
    lens = []
    min_full = minmax[0][0]

    def get_percent(val: float) -> str:
        d = val / min_full
        if d < 10:
            return f'{d * 100:.1f}'
        return ' 999+'

    for min_s, max_s in minmax:
        deci, prefix = get_sec_metrix(min_s)

        max_s_len = __float_len(max_s / deci) + 4
        row_format += f'| %{max_s_len}.3f {prefix} '
        multi.append(deci)
        lens.append(max_s_len + len(prefix) + 1)

    row_format += f'| %-{max_fn_len}s | %s |'
    lens.extend([max_fn_len, 5])

    fr = '+' + '-' * (sum(lens) + len(lens) * 3 - 1) + '+'
    res.append(fr)
    if headers:
        res.append('| ' + ' | '.join(h.center(lens[i]) for i, h in enumerate((*headers, 'f', '%'))) + ' |')

    for item in exp:
        res.append(row_format % (*(i_sec / multi[i] for i, i_sec in enumerate(item[1:])), item[0], get_percent(item[1])))

    res.append(fr)
    return res
