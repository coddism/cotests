from cotests import bench_batch

headers = ('full', 'max', 'min', 'avg')
lens = [10,10,10,10,13]
def test_01():
    return '| ' + ' | '.join(h.center(lens[i]) for i, h in enumerate(headers + ('f',))) + ' |'

def test_02():
    return '| ' + ' | '.join(h.center(lens[i]) for i, h in enumerate((*headers, 'f'))) + ' |'

def test_03():
    return ('| ' + ' | '.join(f'{{:^{l}}}' for l in lens) + ' |').format(*headers, 'f')


row_format = '| %7.3f ms | %6.3f µs | %5.3f µs | %5.3f µs | %-2s |'
multi = [.1**3, .1**6, .1**6, .1**6]
item = ('b1', 0.14885144161235075, 7.442000060109422e-05, 1.3700009731110185e-06, 1.4885144161235076e-06)

def test_11():
    printed_item = []
    for i, i_sec in enumerate(item[1:]):
        printed_item.append(i_sec / multi[i])
    printed_item.append(item[0])
    return row_format % tuple(printed_item)

def test_12():
    return row_format % (*(i_sec / multi[i] for i, i_sec in enumerate(item[1:])), item[0])

def xx(a): return a*2
def xx2(a): return a**2
def xx3(a): return a^2


if __name__ == '__main__':
    function_list = [value for key, value in globals().items()
                     if key.startswith('xx') and callable(value) and value.__module__ == __name__]

    bench_batch(
        *function_list,
        # iterations=100000
        # global_args=(1,),
        personal_args=[(4,),(88,),(89,)],
    )
