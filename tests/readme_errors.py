from cotests import test_batch, CoTestCase

def test_0(): ...
def test_1(): raise Exception('I want error!')

class T0(CoTestCase):
    def test_t0(self): ...
    def test_t1(self): raise ValueError('I want ValueError in case!')

test_batch(test_0, test_1, T0)
