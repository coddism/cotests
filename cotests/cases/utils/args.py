from typing import TYPE_CHECKING, Optional, Tuple, Sequence, Dict, List, Set

if TYPE_CHECKING:
    from cotests.typ import CoArgsList, TestArgs, TestKwargs


class CoTestArgs:

    def __init__(
            self,
            # personal
            pa: Optional[Sequence['TestArgs']],
            pkw: Optional[Sequence['TestKwargs']],
            # global
            ga: Optional['TestArgs'],
            gkw: Optional['TestKwargs'],
    ):
        self.__params: 'CoArgsList' = []
        # have
        self.ha = bool(pa or ga)
        self.hkw = bool(pkw or gkw)

        if ga and not isinstance(ga, (List, Tuple, Set)):
            print('Better to use for args: list, tuple, set')

        ga = ga or ()
        gkw = gkw or {}

        if gkw:
            merge_kw = lambda pk: {**gkw, **pk}
        else:
            merge_kw = lambda pk: pk

        if pa:
            assert not ga, 'Personal & global args conflict'
            if pkw:
                assert len(pa) == len(pkw), 'Personal args & kwargs have different length'
                self.__params = [(a, merge_kw(pkw[i])) for i, a in enumerate(pa)]
            else:
                self.__params = [(a, gkw) for a in pa]
        elif pkw:
            self.__params = [(ga, merge_kw(k)) for k in pkw]
        else:
            self.__params = [(ga, gkw)]

    def __merge_kw(self,
                   k1: 'TestKwargs',
                   k2: 'TestKwargs',
    ) -> 'TestKwargs':
        if self.hkw:
            if k2:
                return {**k1, **k2}
            else:
                return k1
        else:
            return k2

    def get(self,
            args: Tuple,
            kwargs: Dict,
    ) -> 'CoArgsList':
        if args:
            if self.ha:
                raise ValueError('args conflict')
            if kwargs:
                return [(args, self.__merge_kw(p[1], kwargs)) for p in self.__params]
            else:
                return [(args, p[1]) for p in self.__params]
        elif kwargs:
            return [(p[0], self.__merge_kw(p[1], kwargs)) for p in self.__params]
        else:
            return self.__params


__all__ = (CoTestArgs,)
