from cotests import bench_batch, CoTestGroup, CoTestCase, test_groups

def test_0(*_, **__): ...
def test_1(*_, **__): ...

async def test_a0(*_, **__): ...
async def test_a1(*_, **__): ...

# Example 1: bench_batch
bench_batch(test_0, test_1, test_a0, test_a1)
# Example 1.1: benchmark
bench_batch(test_0, test_1, test_a0, test_a1, iterations=50)

# Example 2: CoTestCase
class Case0(CoTestCase):
    def test_0(self): ...
    def test_1(self): ...
    async def test_a0(self): ...
Case0().run_tests()
# Example 2.1: benchmark
Case0().run_tests(iterations=50)

# Example 3: CoTestGroup
g_sync = CoTestGroup(test_0, test_1)
g_async = CoTestGroup(test_a0, test_a1)
g_all = CoTestGroup(test_0, test_1, test_a0, test_a1, Case0)

# Example 3.1 - single group
g_sync.go()
# Example 3.2 - multiple
test_groups(g_sync, g_async, g_all)

# Example 4: ALL
bench_batch(
    test_0, test_1, test_a0, test_a1,
    Case0,
    g_sync, g_async, g_all,
)
