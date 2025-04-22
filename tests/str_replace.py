import re
from functools import reduce
from typing import Tuple, Dict

from cotests import CoTestCase


class StrReplaceCase(CoTestCase):

    def __init__(self, replace: Dict[str, str]):
        self.__rep = replace
        self.__finder = re.compile("|".join(re.escape(k) for k in replace.keys()))
        self.__trans = str.maketrans(replace)

    # STRING REPLACE

    def _test_0(self, line: str):
        # return (line.
        #         replace('\n', '')
        #         .replace('+', '-')
        #         .replace('/', '_')
        #         .replace('=', '')
        # )
        return (line.
                replace('0', '!')
                .replace('b', '@')
                .replace('c', '#')
                .replace('d', '$')
        )

    def test_01(self, line: str):
        for k, v in self.__rep.items():
            line = line.replace(k, v)
        return line

    def test_011(self, line: str):
        for r in self.__rep.items():
            line = line.replace(*r)
        return line

    # REGEX

    # https://stackoverflow.com/a/6117350
    def test_re_search0(self, line: str):
        result = []
        pos = 0
        while True:
            match = self.__finder.search(line, pos)
            if match:
                # cut off the part up until match
                result.append(line[pos: match.start()])
                # cut off the matched part and replace it in place
                result.append(self.__rep[line[match.start(): match.end()]])
                pos = match.end()
            else:
                # the rest after the last match
                result.append(line[pos:])
                break
        return "".join(result)

    def test_re_search1(self, line: str):
        res = ''
        pos = 0
        while True:
            match = self.__finder.search(line, pos)
            if match:
                res += line[pos: match.start()] + self.__rep[match[0]]
                pos = match.end()
            else:
                res += line[pos:]
                break
        return res

    def test_re_finditer(self, line: str):
        res = ''
        pos = 0
        for match in self.__finder.finditer(line):
            res += line[pos: match.start()] + self.__rep[match.group(0)]
            pos = match.end()
        res += line[pos:]
        return res

    def test_re_sub_lambda(self, line: str):
        return self.__finder.sub(lambda m: self.__rep[m.group(0)], line)

    def __re0(self, match: re.Match): return self.__rep[match.group(0)]
    def test_re_sub_function(self, line: str):
        return self.__finder.sub(self.__re0, line)

    # TRANSLATE

    def test_translate(self, line: str):
        return line.translate(self.__trans)

    # REDUCE

    def __red0(self, text: str, repl: Tuple[str, str]):
        return text.replace(*repl)
    def __red1(self, text: str, repl: Tuple[str, str]):
        return text.replace(repl[0], repl[1])

    def test_reduce_lambda(self, line: str):
        return reduce(lambda a, kv: a.replace(*kv), self.__rep.items(), line)
    def test_reduce_function(self, line: str):
        return reduce(self.__red0, self.__rep.items(), line)
    def test_reduce_function2(self, line: str):
        return reduce(self.__red1, self.__rep.items(), line)


if __name__ == '__main__':

    # large string
    with open('/path/to/large/file.txt', 'r') as file:
        data = file.read()
        print(len(data))
        StrReplaceCase({
            '0': '!',
            'b': '@',
            'c': '#',
            'd': '$',
        }).run_bench(
            global_args=(data,),
            iterations=10,
        )

    # short strings

    strings = (
        ('YIZ+4CRZZ7UAaAJ50Xj4nL9KZxvaYYYQhBsNzFfjDkE=',),
        ('cPqvSUPlp5YGAyU1rtazTz6gDnqMIRfdE1Y64FIPlzo=',),
        ('XJuoQ8vDD8bq4krP98gegw==',),
        ('uKuNih2MZlGXm7Je4F5gyu8TubQ5/mALIwX3nOTxhOU=',),
        ('N8kwxfNuSwDTTe7YI1ipRgvUaqJqs3JTCFqRyePbrqM=',),
        ('XGhMYAF4NUqDZZjaISOAww==',),
        ('uEgu79p1wbr9Lb6iLeSuA4RxLcgiGQFFc8SjO7rvAGw=',),
        ('cBmMRYgTaJ6/j1dIOm+9yg==',),
    )

    StrReplaceCase({
        '\n': '',
        '+': '-',
        '/': '_',
        '=': '',
    }).run_bench(
        personal_args=strings,
        iterations=10,
    )
