from cotests import test_batch, bench_batch

def test_0(): ...
def test_1(): ...
def test_2(): ...

# just test
test_batch(test_0, test_1, test_2,)

# benchy
bench_batch(test_0, test_1, test_2, name='benchy')

# more benchy
bench_batch(
    test_0, test_1, test_2,
    iterations=1000,
    name='more benchy',
)
