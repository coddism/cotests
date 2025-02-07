import inspect

from .flat import bench


def _case_predicate(obj):
    return inspect.ismethod(obj) and obj.__name__.startswith('test_')


class Case:

    def __init__(self):
        tests = inspect.getmembers(self, _case_predicate)
        exp = []
        for (func_name, func) in tests:
            print(f'{func_name}.. ', end='')
            try:
                sec = bench(func)()
            except Exception as e:
                print(f'error: {e}')
            else:
                exp.append((sec, func_name))
                print('ok')

        for sec, func_name in exp:
            print('| %.3f sec | %-20s | ' % (sec, func_name))

    # def __new__(cls, *args, **kwargs):
    #     instance = super().__new__(cls)
    #     return instance

    # def __await__(self):
    #     print('AWAIT')
