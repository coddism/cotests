from cotests import bench_batch

def test_0(): ...
def test_1(): ...
def test_2(): ...

# just test
bench_batch(
    test_0, test_1, test_2,
)

# more benchy
bench_batch(
    test_0, test_1, test_2,
    iterations=1000,
)