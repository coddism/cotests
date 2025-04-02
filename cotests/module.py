import inspect
import importlib.util
import os
import unittest
from typing import List, Optional, Collection
from .case import CoTestCase
from .cases import CoTestGroup, test_groups
from cotests.logger import logger


def test_module(
        dir_path: str,
        *,
        file_prefix: str = 't_',
        ignore_files: Optional[Collection[str]] = None,
):
    logger.writeln(f'Search tests in {dir_path}..')
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
                logger.writeln(f'{"*" * 10} {module_name}')

                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                # sys.modules[module_name] = module
                spec.loader.exec_module(module)

                tmp_tests = []
                tmp_groups = []
                tmp_unittests = []
                for k, v in module.__dict__.items():
                    if k.startswith('_'):
                        continue

                    if isinstance(v, CoTestGroup):
                        tmp_groups.append(v)
                    elif inspect.isfunction(v) and v.__module__ == module_name and v.__name__.startswith('test_'):
                        tmp_tests.append(v)
                    elif inspect.isclass(v) and v.__module__ == module_name:
                        if issubclass(v, CoTestCase):
                            tmp_tests.append(v)
                        elif issubclass(v, unittest.TestCase):
                            tmp_unittests.append(v)
                        else:
                            continue
                    else:
                        continue
                    logger.writeln(f' * {k} : {type(v)}')

                # tests.append(CoTestGroup(*tmp_groups, *tmp_tests, name=module_name))
                if tmp_groups:
                    tests.append(CoTestGroup(*tmp_groups, name=module_name))
                elif tmp_tests:
                    tests.append(CoTestGroup(*tmp_tests, name=module_name))

                if tmp_unittests:
                    tests.append(CoTestGroup(*tmp_unittests, name=module_name))
        else:
            logger.writeln(f'o_O {sd}')

    logger.writeln("""
    +---------------------+
    |    Start CoTests    |
    +---------------------+
    """)
    return test_groups(*tests)


__all__ = ('test_module', )
