import inspect
import unittest
from typing import TYPE_CHECKING, Optional, Iterable, List, Type

from cotests.case.case import CoTestCase
from cotests.exceptions import UnknownTestTypeError
from .abstract import AbstractTestCase, AbstractTestGroup
from .cases import (
    CoroutineTestCase, CoroutineFunctionTestCase, FunctionTestCase, FunctionTestCaseWithAsyncPrePost
)
from .runner import RootGroupRunner
from .unit_case import UnitTestCase
from .utils.args import CoTestArgs
from .utils.case_ext import TestCaseExt

if TYPE_CHECKING:
    from cotests.typ import InTest, TestArgs, TestKwargs, TestCallable
    from .cases import TestCase


class CoTestGroup(AbstractTestGroup):
    NAME = ''

    def __init__(
            self,
            *tests: 'InTest',
            name: Optional[str] = '',
            global_args: Optional['TestArgs'] = None,
            global_kwargs: Optional['TestKwargs'] = None,
            personal_args: Optional[Iterable['TestArgs']] = None,
            personal_kwargs: Optional[Iterable['TestKwargs']] = None,
            pre_test: Optional['TestCallable'] = None,
            post_test: Optional['TestCallable'] = None,
            cotest_args: Optional['CoTestArgs'] = None,
            cotest_ext: Optional['TestCaseExt'] = None,

            constructor: Optional['TestCallable'] = None,
            destructor: Optional['TestCallable'] = None,
    ):
        # if len(tests) == 0:
        #     raise ValueError('Empty tests list')
        self.__tests: List['AbstractTestCase'] = []
        self.__has_coroutines = False
        self.name = name or self.NAME
        self._init_errors = []

        if cotest_args:
            if any((global_args, global_kwargs, personal_args, personal_kwargs)):
                raise Exception('Args conflict')
            self.__cta = cotest_args
        else:
            self.__cta = CoTestArgs(
                personal_args,
                personal_kwargs,
                global_args,
                global_kwargs,
        )

        if cotest_ext:
            if any((pre_test, post_test)):
                raise Exception('Test Case extension conflict')
            self.__tce = cotest_ext
        else:
            self.__tce = TestCaseExt(
                pre_test=pre_test,
                post_test=post_test,
            )

        if constructor:
            try:
                self.constructor = self.__check_ac(constructor)
            except ValueError:
                raise ValueError('Incorrect group constructor')

        if destructor:
            try:
                self.destructor = self.__check_ac(destructor)
            except ValueError:
                raise ValueError('Incorrect group destructor')

        for test in tests:
            try:
                self.__add_test(test)
            except UnknownTestTypeError as e:
                self._init_errors.append(e)

    def __check_ac(self, cd):
        if inspect.iscoroutinefunction(cd):
            self.__has_coroutines = True
            return cd
        elif callable(cd):
            return cd
        else:
            raise ValueError

    def _clone(self, case: CoTestCase) -> 'CoTestGroup':
        return case.create_group(
            cotest_args=self.__cta,
            cotest_ext=self.__tce,
        )

    @property
    def is_empty(self):
        return self.__tests == []

    @property
    def is_async(self):
        return self.__has_coroutines

    @property
    def init_errors(self):
        return self._init_errors

    @property
    def tests(self):
        return iter(self.__tests)

    def __get_function_test_case(self, test: 'InTest') -> Optional[Type['TestCase']]:
        if inspect.iscoroutine(test):
            return CoroutineTestCase
        elif inspect.iscoroutinefunction(test):
            return CoroutineFunctionTestCase
        elif inspect.isfunction(test) or inspect.ismethod(test):
            if self.__tce.is_async:
                return FunctionTestCaseWithAsyncPrePost
            else:
                return FunctionTestCase

    def __add_test(self, test: 'InTest', *args, **kwargs):
        if isinstance(test, tuple):
            if args or kwargs:
                raise Exception('InTest format Error')
            assert len(test) > 0
            f = test[0]
            a_, kw_ = (), {}
            for ti in test[1:]:
                if isinstance(ti, tuple):
                    if a_: raise ValueError('TestItem args conflict')
                    a_ = ti
                elif isinstance(ti, dict):
                    if kw_: raise ValueError('TestItem kwargs conflict')
                    kw_ = ti
                else:
                    raise ValueError(f'Unsupported type for InTest: {type(ti)}')

            self.__add_test(f, *a_, **kw_)
        else:
            tc = self.__get_function_test_case(test)
            if tc:
                return self.__add_test_case(tc(
                    test,
                    params=self.__cta.get(args, kwargs),
                    ext=self.__tce,
                ))
            elif isinstance(test, CoTestGroup):
                return self.__add_test_case(test)
            elif isinstance(test, CoTestCase):
                return self.__add_test_case(self._clone(test))
            elif inspect.isclass(test):
                if issubclass(test, CoTestCase):
                    return self.__add_test_case(self._clone(test()))
                if issubclass(test, unittest.TestCase):
                    return self.__add_test_case(UnitTestCase(test))

            raise UnknownTestTypeError(f'Unknown test: {type(test)} {test}')

    def __add_test_case(self, case: AbstractTestCase):
        if case.is_async:
            self.__has_coroutines = True
        self.__tests.append(case)

    def run_test(self):
        return RootGroupRunner(self).run()

    def run_bench(self, iterations: int):
        assert iterations >= 1, 'Incorrect iterations count'
        return RootGroupRunner(self).bench(iterations)


def test_groups(*groups: CoTestGroup, name='__main__'):
    g = CoTestGroup(*groups, name=name)
    return g.run_test()
