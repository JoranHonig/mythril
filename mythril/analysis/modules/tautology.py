from z3 import is_true, is_false, Not, simplify
from mythril.analysis.report import Issue
"""
MODULE DESCRIPTION:

Test to find invariant branch conditions in code i.e. conditional branches that are always taken

"""


def execute(statespace):
    """
    Executes analysis module to detect tautologies
    :param statespace: Statespace to analyse
    :return: Found issues
    """
    issues = []
    jumpi_instructions = _find_jumpi(statespace)
    jumpi_conditions = _get_conditions_for_jumpi(jumpi_instructions)

    for address, conditions in jumpi_conditions.items():
        if not _all_conditions_same(conditions):
            continue

        value, node, state = conditions[0]

        issue = Issue(node.contract_name, node.function_name, address, "Invariant branch condition", "Informational")
        issue.description = "Found a conditional jump which always follows the same branch"
        issues.append(issue)

    return issues


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
        value = jumpi_state.mstate.stack[-2]

        if key not in result.keys():
            result[key] = []
        result[key] += [(value, node, jumpi_state)]

    return result


def _all_conditions_same(conditions):
    """
    Verifies if all conditions always evaluate to the same
    :param conditions: Array of (constraint, condition_value) elements
    :return: all conditions simplify to true
    """
    _false, _true = False, False
    for value, _, _ in conditions:
        _false = _false or is_false(simplify(value))
        _true = _true or is_true(simplify(value))

    return _false ^ _true
