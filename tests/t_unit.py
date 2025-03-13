import sys
import unittest

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

class MyTestCase(unittest.TestCase):

    @unittest.skip("demonstrating skipping")
    def test_nothing(self):
        self.fail("shouldn't happen")

    def test_format(self):
        # Tests that work for only a certain version of the library.
        pass

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_windows_support(self):
        # windows specific testing code
        pass

    def test_maybe_skipped(self):
        # test code that depends on the external resource
        self.skipTest("external resource not available")


class EmptyTC(unittest.TestCase):
    ...


if __name__ == '__main__':
    # unittest.main(verbosity=2)

    loader = unittest.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in (TestStringMethods,)
    ]
    suite = unittest.TestSuite(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
