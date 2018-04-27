from z3 import is_true
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

    return []


def _find_jumpi(statespace):
    """ Finds all jumpi instructions and returns their states """
    pass


def _get_conditions_for_jumpi(jumpi_states):
    """
    Returns a dictonary for each reachable jumpi instruction with
    key: address
    value: (constraints,condition_value)
    """
    pass

def _all_conditions_true( conditions ):
    """
    Verifies if all conditions always evaluate to true
    :param conditions: Array of (constraint, condition_value) elements
    :return: all conditions simplify to true
    """
    pass
