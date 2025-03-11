import inspect
import importlib.util
import os
from typing import List, Optional, Collection
from .case.abstract import AbstractCoCase
from .cases.group import CoTestGroup, test_groups


def test_module(
        dir_path: str,
        *,
        file_prefix: str = 't_',
        ignore_files: Optional[Collection[str]] = None,
):
    print(f'Search tests in {dir_path}..')
    tests: List[CoTestGroup] = []

    for sd in os.scandir(dir_path):
        if sd.is_dir():
            ...
        elif sd.is_file():
            if sd.name.startswith(file_prefix) and sd.name.endswith('.py'):
                if ignore_files and sd.name in ignore_files:
                    continue
                module_name = sd.name
                file_path = sd.path
                print('*' * 10, module_name)

                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                # sys.modules[module_name] = module
                spec.loader.exec_module(module)

                tmp_tests = []
                tmp_groups = []
                for k, v in module.__dict__.items():
                    if k.startswith('_'):
                        continue

                    if isinstance(v, CoTestGroup):
                        tmp_groups.append(v)
                    elif inspect.isfunction(v) and v.__module__ == module_name and v.__name__.startswith('test_'):
                        tmp_tests.append(v)
                    elif inspect.isclass(v) and v.__module__ == module_name and issubclass(v, AbstractCoCase):
                        tmp_tests.append(v)
                    else:
                        continue
                    print(' *', k, type(v))

                # tests.append(CoTestGroup(*tmp_groups, *tmp_tests, name=module_name))
                if tmp_groups:
                    tests.append(CoTestGroup(*tmp_groups, name=module_name))
                elif tmp_tests:
                    tests.append(CoTestGroup(*tmp_tests, name=module_name))
        else:
            print('o_O', sd)

    print("""
    +---------------------+
    |    Start CoTests    |
    +---------------------+
    """)
    return test_groups(*tests)


__all__ = (test_module, )
