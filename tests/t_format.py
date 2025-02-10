from cotests import bench_batch

headers = ('full', 'max', 'min', 'avg')
lens = [10,10,10,10,13]
def b01():
    return '| ' + ' | '.join(h.center(lens[i]) for i, h in enumerate(headers + ('f',))) + ' |'

def b02():
    return '| ' + ' | '.join(h.center(lens[i]) for i, h in enumerate((*headers, 'f'))) + ' |'

def b03():
    return ('| ' + ' | '.join(f'{{:^{l}}}' for l in lens) + ' |').format(*headers, 'f')


row_format = '| %7.3f ms | %6.3f µs | %5.3f µs | %5.3f µs | %-2s |'
multi = [.1**3, .1**6, .1**6, .1**6]
item = ('b1', 0.14885144161235075, 7.442000060109422e-05, 1.3700009731110185e-06, 1.4885144161235076e-06)

def b11():
    printed_item = []
    for i, i_sec in enumerate(item[1:]):
        printed_item.append(i_sec / multi[i])
    printed_item.append(item[0])
    return row_format % tuple(printed_item)

def b12():
    return row_format % (*(i_sec / multi[i] for i, i_sec in enumerate(item[1:])), item[0])


if __name__ == '__main__':

    bench_batch(
        b01, b02, b03,
        b11, b12,
        iterations=100000
    )
