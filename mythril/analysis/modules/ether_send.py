from z3 import *
from mythril.analysis.ops import *
from mythril.analysis import solver
from mythril.analysis.report import Issue
from mythril.exceptions import UnsatError
import re
import logging


'''
MODULE DESCRIPTION:

Check for CALLs that send >0 Ether to either the transaction sender, or to an address provided as a function argument.
If msg.sender is checked against a value in storage, check whether that storage index is tainted (i.e. there's an unconstrained write
to that index).
'''


def execute(statespace):

    logging.debug("Executing module: ETHER_SEND")

    issues = []

    for call in statespace.calls:

        state = call.state
        address = state.get_current_instruction()['address']

        # if "callvalue" in str(call.value):
        #     logging.debug("[ETHER_SEND] Skipping refund function")
        #     continue

        # We're only interested in calls that send Ether
        # if call.value.type == VarType.CONCRETE and call.value.val == 0:
        #     continue

        not_creator_constraints = []
        if len(state.world_state.transaction_sequence) > 1:
            creator = state.world_state.transaction_sequence[0].caller
            for transaction in state.world_state.transaction_sequence[1:]:
                not_creator_constraints.append(Not(Extract(159, 0, transaction.caller) == Extract(159, 0, creator)))
                not_creator_constraints.append(Not(Extract(159, 0, transaction.caller) == 0))

        node = call.node
        instruction = call.state.instruction
        description = " "
        try:
            model = solver.get_model(node.constraints + not_creator_constraints)

            debug = "SOLVER OUTPUT:\n" + solver.pretty_print_model(model)

            issue = Issue(node.contract_name, node.function_name, instruction['address'], "Ether Send",
                          "Warning", description, debug)
            issues.append(issue)
        except UnsatError:
            logging.debug("[UNCHECKED_SUICIDE] no model found")

    return issues
