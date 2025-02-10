from typing import Tuple


__METRIX = (
    (60, 'min'),
    (1, 'sec'),
    (.1**3, 'ms'),
    (.1**6, 'µs'),
    (.1**9, 'ns'),
    (.1**12, 'ps'),
    (.1**15, 'fs'),
)


def get_sec_metrix(sec: float) -> Tuple[float, str]:
    for deci, metr in __METRIX:
        if sec > deci:
            return deci, metr
    else:
        return __METRIX[-1]


def format_sec_metrix(sec: float) -> str:
    deci, metr = get_sec_metrix(sec)
    return f'{sec / deci:.3f} {metr}'
