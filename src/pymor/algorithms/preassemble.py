# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright 2013-2017 pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from pymor.algorithms.rules import RuleTable, match_class, match_generic
from pymor.discretizations.interfaces import DiscretizationInterface
from pymor.operators.basic import ProjectedOperator
from pymor.operators.constructions import (LincombOperator, Concatenation,
                                           AffineOperator, AdjointOperator, SelectionOperator)
from pymor.operators.interfaces import OperatorInterface


def preassemble(obj):
    return PreAssembleRules.apply(obj)


class PreAssembleRules(RuleTable):

    @match_class(DiscretizationInterface, AffineOperator, Concatenation, SelectionOperator)
    def action_recurse(self, op):
        return self.replace_children(op)

    @match_class(LincombOperator)
    def action_recurse_and_assemble(self, op):
        op = self.replace_children(op)
        if not op.parametric:
            return op.assemble()
        else:
            return op

    @match_class(AdjointOperator, ProjectedOperator)
    def action_AdjointOperator(self, op, *args, **kwargs):
        new_operator = self.apply(op.operator, *args, **kwargs)
        if new_operator is op.operator:
            return op
        elif not (op.source_product or op.range_product):
            return new_operator.T
        else:
            return op.with_(operator=new_operator)

    @match_generic(lambda op: not op.parametric, 'non-parametric operator')
    def action_assemble(self, op):
        return op.assemble()

    @match_class(OperatorInterface)
    def action_identity(self, op):
        return op
