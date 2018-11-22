from mythril.analysis import solver
from mythril.analysis.analysis_utils import get_non_creator_constraints
from mythril.analysis.ops import *
from mythril.analysis.report import Issue
from mythril.analysis.swc_data import SIGNATURE_REPLAY
from mythril.exceptions import UnsatError
from mythril.analysis.modules.base import DetectionModule
from mythril.laser.ethereum.transaction import ContractCreationTransaction
import re
import logging
from mythril.laser.ethereum.state.global_state import GlobalState
from mythril.laser.ethereum.call import get_call_data
from mythril.laser.ethereum.cfg import Node

"""
MODULE DESCRIPTION:


"""


class StateMalleabilityAnnotation:
    def __init__(self, ecrecover_call_state, subject):
        self.has_state_mod = False
        self.original_state = ecrecover_call_state
        self.subject = subject


class MalleabilityModule(DetectionModule):
    def __init__(self):
        super().__init__(
            name="Signature Malleability",
            swc_id=SIGNATURE_REPLAY,
            hooks=["CALL", "SSTORE", "STOP", "RETURN"],  # , "SSTORE", "SUICIDE", "DELEGATECALL"],
            description=(
                "Check for SUICIDE instructions that either can be reached by anyone, "
                "or where msg.sender is checked against a tainted storage index (i.e. "
                "there's a write to that index is unconstrained by msg.sender)."
            ),
            entrypoint="callback"
        )
        self.issues = []

    def execute(self, state):
        self.issues += self._analyze_state(state)
        return self.issues

    def _analyze_state(self, state: GlobalState):
        if state.get_current_instruction()["opcode"] == "CALL":
            return self.call_hook(state)
        if state.get_current_instruction()["opcode"] == "SSTORE":
            return self.sstore_hook(state)
        if state.get_current_instruction()["opcode"] in ("STOP", "RETURN"):
            stop_result = self.stop_hook(state)
            return stop_result

    def call_hook(self, state):
        if not self._is_ecrecover(state):
            logging.info("This is not an ecrecover call")
            return []

        memory_input_offset, memory_input_size = state.mstate.stack[2:4]
        call_data, _ = get_call_data(state, memory_input_offset, memory_input_size)

        subject, _ = call_data[0:32]
        state.annotation += [StateMalleabilityAnnotation(state, subject)]

        return []

    def sstore_hook(self, state):
        for annotation in [annotation for annotation in state.annotation if
                           isinstance(annotation, StateMalleabilityAnnotation)]:
            logging.info("STORE_HOOK: Found state with annotation")
            annotation.has_state_mod = True
        for annotation in state.annotation:
            print (annotation.has_state_mod)
        return []

    def stop_hook(self, state):
        for annotation in [annotation for annotation in state.annotation if
                           isinstance(annotation, StateMalleabilityAnnotation)]:
            if not annotation.has_state_mod:
                continue
            logging.info("STOP_HOOK: Found state with annotation")
            if self._is_checked(annotation, state):
                continue
            issue = Issue(
                contract=annotation.original_state.node.contract_name,
                function_name=annotation.original_state.node.function_name,
                address=annotation.original_state.get_current_instruction()["address"],
                swc_id=SIGNATURE_REPLAY,
                bytecode=state.environment.code.bytecode,
                title=self.name,
                _type="Warning",
                description=self.description,
                debug="",
                gas_used=(state.mstate.min_gas_used, state.mstate.max_gas_used),
            )
            return [issue]
        return []

    def _is_checked(self, annotation, state):
        c = annotation.subject
        for constraint in state.mstate.constraints:
            if str(c) in str(constraint):
                return True
        return False

    @staticmethod
    def _is_ecrecover(state):
        instruction = state.get_current_instruction()
        # print(instruction)
        if instruction["opcode"] != "CALL":
            logging.debug("Not a call instruction. Actual {}".format(instruction["opcode"]))
            return False

        target = state.mstate.stack[-2]
        if not (isinstance(target, BitVecNumRef) or isinstance(target, int)):
            logging.debug("Symbolic call target")
            return False
        if isinstance(target, BitVecNumRef):
            target = int(target.as_long())
        logging.debug("Call target: {}".format(target))
        if target != 1:
            return False
        return True


detector = MalleabilityModule()
