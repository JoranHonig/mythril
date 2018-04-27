from z3 import is_true, Not, simplify
from mythril.analysis.modules import try_constraints
"""
MODULE DESCRIPTION:

Test to find tautologies in code i.e. conditional branches that are always taken

"""


def execute(statespace):
    """
    Executes analysis module to detect tautologies
    :param statespace: Statespace to analyse
    :return: Found issues
    """
    jumpi_instructions = _find_jumpi(statespace)
    jumpi_conditions = _get_conditions_for_jumpi(jumpi_instructions)

    for address, conditions in jumpi_conditions.items():
        if _all_conditions_true(conditions):
            print(address)
    return []


def _find_jumpi(statespace):
    """ Finds all jumpi instructions and returns their states as a generator """
    for k in statespace.nodes:
        node = statespace.nodes[k]
        for state in node.states:
            if state.get_current_instruction()['opcode'] == "JUMPI":
                yield state, node


def _get_conditions_for_jumpi(jumpi_states):
    """
    Returns a dictionary for each reachable jumpi instruction with
    key: address
    value: (constraints,condition_value)
    """
    result = {}
    for jumpi_state, node in jumpi_states:
        instruction = jumpi_state.get_current_instruction()
        key = instruction['address']
        constraint, value = node.constraints, jumpi_state.mstate.stack[-2]
        if key not in result.keys():
            result[key] = []

        result[key] += [(constraint, value)]

    return result


def _all_conditions_true( conditions ):
    """
    Verifies if all conditions always evaluate to true
    :param conditions: Array of (constraint, condition_value) elements
    :return: all conditions simplify to true
    """
    for constraints, value in conditions:
        if try_constraints(constraints, [value]):
            return False
    return True
