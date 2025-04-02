from cotests import CoTestGroup
from .t_obj import TObj, TObjA


if __name__ == '__main__':

    def ttt(x = 7): return x+7
    async def att(x = 4): return x//5

    gl0 = CoTestGroup(
        lambda x: x*x,
        lambda x: x^3,
        global_args=(40,),
        name='lambda0',
    )

    gl = CoTestGroup(
        lambda x: x*x,
        lambda x: x^3,
        gl0,
        ttt,
        global_args=(4,),
        name='lambda1',
    )
    # gl.run_test()
    # gl.run_bench(1)
    # gl.run_bench(10)

    g = CoTestGroup(
        TObj,
        TObjA,
        gl,
        ttt,
        att,
        att(4),
        456,
        CoTestGroup(name='EMPTY'),
        gl0,
        name='ROOT',
    )
    # g.run_test()
    # g.run_bench(1)
    g.run_bench(2)
