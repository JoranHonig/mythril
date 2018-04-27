from mythril.analysis import solver
from mythril.exceptions import UnsatError
import copy

def try_constraints(constraints, new_constraints):
    """
    Tries new constraints
    :return Model if satisfiable otherwise None
    """
    _constraints = copy.deepcopy(constraints)
    for constraint in new_constraints:
        _constraints.append(copy.deepcopy(constraint))
    try:
        model = solver.get_model(_constraints)
        return model
    except UnsatError:
        return None
