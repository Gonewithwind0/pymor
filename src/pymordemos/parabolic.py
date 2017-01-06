#!/usr/bin/env python
# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright 2013-2016 pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

"""Simple demonstration of solving parabolic equations using pyMOR's builtin discretization toolkit.

Usage:
    parabolic.py [options] heat TOP
    parabolic.py [options] dar SPEED

Arguments:
    TOP          The heat diffusion coefficient for the top bars.
    SPEED        The advection speed.

Options:
    -h, --help   Show this message.

    --fv         Use finite volume discretization instead of finite elements.

    --rect       Use RectGrid instead of TriaGrid.

    --grid=NI    Use grid with NIxNI intervals [default: 100].

    --nt=COUNT   Number of time steps [default: 100].
"""

from docopt import docopt
import numpy as np

from pymor.basic import *


def parabolic_demo(args):
    args['--nt'] = int(args['--nt'])
    args['--grid'] = int(args['--grid'])

    grid_name = '{1}(({0},{0}))'.format(args['--grid'], 'RectGrid' if args['--rect'] else 'TriaGrid')
    print('Solving on {0}'.format(grid_name))

    if args['heat']:
        args['TOP'] = float(args['TOP'])
        problem = InstationaryProblem(

            EllipticProblem(
                domain=RectDomain(top='dirichlet', bottom='neumann'),

                diffusion=LincombFunction(
                    [ConstantFunction(1., dim_domain=2),
                     ExpressionFunction('(x[..., 0] > 0.45) * (x[..., 0] < 0.55) * (x[..., 1] < 0.7) * 1.',
                                        dim_domain=2),
                     ExpressionFunction('(x[..., 0] > 0.35) * (x[..., 0] < 0.40) * (x[..., 1] > 0.3) * 1. + ' +
                                        '(x[..., 0] > 0.60) * (x[..., 0] < 0.65) * (x[..., 1] > 0.3) * 1.',
                                        dim_domain=2)],
                    [1.,
                     100. - 1.,
                     ExpressionParameterFunctional('top - 1.', {'top': 0})]
                ),

                rhs=ConstantFunction(value=0., dim_domain=2),

                dirichlet_data=ConstantFunction(value=0., dim_domain=2),

                neumann_data=ExpressionFunction('(x[..., 0] > 0.45) * (x[..., 0] < 0.55) * -1000.',
                                                dim_domain=2),
            ),

            T=1.,

            initial_data=ExpressionFunction('(x[..., 0] > 0.45) * (x[..., 0] < 0.55) * (x[..., 1] < 0.7) * 10.',
                                            dim_domain=2),

            parameter_space=CubicParameterSpace({'top': 0}, minimum=1, maximum=100.)
        )
    else:
        args['SPEED'] = float(args['SPEED'])
        problem = InstationaryProblem(

            EllipticProblem(
                domain=RectDomain(),

                diffusion=ConstantFunction(0.01, dim_domain=2),

                advection=LincombFunction([ConstantFunction(np.array([-1., 0]), dim_domain=2)],
                                          [ProjectionParameterFunctional('speed', ())]),

                reaction=ConstantFunction(0.5, dim_domain=2),

                rhs=ExpressionFunction('(x[..., 0] > 0.3) * (x[..., 0] < 0.7) * (x[..., 1] > 0.3)*(x[...,1]<0.7) * 0.',
                                       dim_domain=2),

                dirichlet_data=ConstantFunction(value=0., dim_domain=2),
            ),

            T=1.,

            initial_data=ExpressionFunction('(x[..., 0] > 0.3) * (x[..., 0] < 0.7) * (x[...,1]>0.3) * (x[..., 1] < 0.7) * 10.',
                                            dim_domain=2),
        )

    print('Discretize ...')
    if args['--rect']:
        grid, bi = discretize_domain_default(problem.stationary_part.domain, diameter=np.sqrt(2) / args['--grid'],
                                             grid_type=RectGrid)
    else:
        grid, bi = discretize_domain_default(problem.stationary_part.domain, diameter=1. / args['--grid'],
                                             grid_type=TriaGrid)
    discretizer = discretize_parabolic_fv if args['--fv'] else discretize_parabolic_cg
    discretization, _ = discretizer(analytical_problem=problem, grid=grid, boundary_info=bi, nt=args['--nt'])

    print('The parameter type is {}'.format(discretization.parameter_type))

    U = discretization.solve({'top': args['TOP']} if args['heat'] else {'speed': args['SPEED']})

    print('Plot ...')
    discretization.visualize(U, title=grid_name)

    print('')


if __name__ == '__main__':
    args = docopt(__doc__)
    parabolic_demo(args)