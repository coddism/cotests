import os

from cotests import test_module

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    test_module(dir_path)
