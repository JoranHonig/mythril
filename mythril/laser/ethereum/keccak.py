from z3 import ExprRef

class KeccacFunctionManager:
    def __init__(self):
        self.keccac_expression_mapping = {}

    def is_keccac(self, expression) -> bool:
        return str(expression) in self.keccac_expression_mapping.keys()

    def get_argument(self, expression) -> ExprRef:
        if not self.is_keccac(expression):
            raise ValueError("Expression is not a recognized keccac result")
        return self.keccac_expression_mapping[str(expression)][1]

    def add_keccak(self, expression: ExprRef, argument: ExprRef):
        index = str(expression)
        self.keccac_expression_mapping[index] = (expression, argument)
