'''
Code taken from: https://stackoverflow.com/questions/2371436/evaluating-a-mathematical-expression-in-a-string
'''


#STL imports
import ast
import operator as op

# supported operators
_OPERATORS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

def eval_expr(expr:str)->float:
    '''

    '''
    res =_eval_(ast.parse(expr, mode='eval').body)
    return float(res)

def _eval_(node):
    '''
    '''
    match node:
        case ast.Constant(value) if isinstance(value, int):
            return value  # integer
        case ast.Constant(value) if isinstance(value, float):
            return value  # integer
        case ast.BinOp(left, op, right):
            return _OPERATORS[type(op)](_eval_(left), _eval_(right))
        case ast.UnaryOp(op, operand):  # e.g., -1
            return _OPERATORS[type(op)](_eval_(operand))
        case _:
            raise TypeError(node)
