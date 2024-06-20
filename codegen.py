# pyright: reportUnboundVariable=none, reportUnusedFunction=none
# REMEMBER TO REMOVE THE pyright DIRECTIVE ABOVE!!!!!!

from tau import asts
from vm.vm_insns import *


def process(ast: asts.Program) -> list[Insn]:
    return _Program(ast)


def _Program(ast: asts.Program) -> list[Insn]:
    # ast.register_pool : list[str]
    # throw error if main exist or not
    if not any(decl.id.token.value == "main" for decl in ast.decls):
        raise NameError("main not found", ast.span)
    retval: list[Insn] = [
        Call(label="main"),
        Halt(),
    ]
    for decl in ast.decls:
        retval.extend(_FuncDecl(decl))
    return retval


def _Decl(ast: asts.Decl) -> list[Insn]:
    retval: list[Insn]
    match ast:
        case asts.FuncDecl():
            retval = _FuncDecl(ast)
        case asts.ParamDecl():
            retval = _ParamDecl(ast)
        case asts.VarDecl():
            retval = _VarDecl(ast)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")
    return retval


def _FuncDecl(ast: asts.FuncDecl) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.id : Id
    # ast.ret_type_ast : TypeAST
    # ast.size : int
    # ast.register_pool : list[str]
    retval: list[Insn] = []
    retval.append(
        Label(ast.id.token.value)
    )
    retval.append(Move("FP1", "SP"))
    retval.append(AddImmediate("SP1", "FP1", ast.size))
    retval.extend(pro())
    retval.append(Move("FP", "FP1"))
    retval.append(Move("SP", "SP1"))
    retval.append(AddImmediate("SP", "SP", 1))
    # register pool on the stack
    # for reg in ast.register_pool:
    #     retval.append(Store("SP", reg))
    #     retval.append(AddImmediate("SP", "SP", 1))
    for param in ast.params:
        retval.extend(_ParamDecl(param))
    # loop through the register pool
    # for i in range(len(ast.register_pool) - 1, -1, -1):
    #     retval.append(Load("SP", ast.register_pool[i]))
    #     retval.append(AddImmediate("SP", "SP", -1))
    retval.extend(_CompoundStmt(ast.body))
    retval.append(Label("EPILOGUE_" + ast.id.token.value))
    retval.extend(epi())
    return retval


def pro() -> list[Insn]:
    return [
        AddImmediate("temp", "FP1", 1),
        Store("temp", "FP"),
        AddImmediate("temp", "FP1", 2),
        Store("temp", "SP"),
        Store("FP1", "RA"),
    ]


def epi() -> list[Insn]:
    return [
        Load("RA", "FP"),
        AddImmediate("temp", "FP", 2),
        Load("SP", "temp"),
        AddImmediate("temp", "FP", 1),
        Load("FP", "temp"),
        JumpIndirect("RA"),
    ]


def _ParamDecl(ast: asts.ParamDecl) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.id : Id
    # ast.type_ast : TypeAST
    retval: list[Insn] = []
    return retval


def _VarDecl(ast: asts.VarDecl) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.id : Id
    # ast.type_ast : TypeAST
    # t154
    retval: list[Insn] = []
    return retval


def _Stmt(ast: asts.Stmt) -> list[Insn]:
    retval: list[Insn]
    match ast:
        case asts.AssignStmt():
            retval = _AssignStmt(ast)
        case asts.CallStmt():
            retval = _CallStmt(ast)
        case asts.CompoundStmt():
            retval = _CompoundStmt(ast)
        case asts.IfStmt():
            retval = _IfStmt(ast)
        case asts.PrintStmt():
            retval = _PrintStmt(ast)
        case asts.ReturnStmt():
            retval = _ReturnStmt(ast)
        case asts.WhileStmt():
            retval = _WhileStmt(ast)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")
    return retval


def _AssignStmt(ast: asts.AssignStmt) -> list[Insn]:
    # ast.lhs : Expr
    # ast.rhs : Expr
    retval: list[Insn] = []
    retval.extend(_rval_Expr(ast.rhs))
    retval.extend(_lval_Expr(ast.lhs))
    retval.append(Store(ast.lhs.register, ast.rhs.register))
    return retval


def _CallStmt(ast: asts.CallStmt) -> list[Insn]:
    # ast.call : CallExpr
    retval: list[Insn] = []
    retval.extend(_rval_CallExpr(ast.call))
    return retval


def _CompoundStmt(ast: asts.CompoundStmt) -> list[Insn]:
    retval: list[Insn] = []
    for decl in ast.decls:
        _VarDecl(decl)
    for stmt in ast.stmts:
        retval.extend(_Stmt(stmt))
    return retval


# flow version
def _IfStmt(ast: asts.IfStmt) -> list[Insn]:
    # ast.expr : Expr
    retval: list[Insn] = []
    retval.extend(flow(ast.expr, "ELSE_" + str(id(ast)), False))
    retval.extend(_CompoundStmt(ast.thenStmt))
    retval.append(Jump("BOTTOM_" + str(id(ast))))
    retval.append(Label("ELSE_" + str(id(ast))))
    if ast.elseStmt:
        retval.extend(_CompoundStmt(ast.elseStmt))
    retval.append(Label("BOTTOM_" + str(id(ast))))
    return retval


def _PrintStmt(ast: asts.PrintStmt) -> list[Insn]:
    # ast.expr : Expr
    retval: list[Insn] = []
    retval.extend(_rval_Expr(ast.expr))
    retval.append(Print(ast.expr.register))
    return retval


def _ReturnStmt(ast: asts.ReturnStmt) -> list[Insn]:
    # ast.expr : Optional[Expr]
    # ast.enclosing_function : FuncDecl
    retval: list[Insn] = []
    if ast.expr:
        retval.extend(_rval_Expr(ast.expr))
        retval.append(AddImmediate("FP1", "FP", -1))
        retval.append(Store("FP1", ast.expr.register))
    retval.append(Jump("EPILOGUE_" + ast.enclosing_function.id.token.value))
    return retval


# flow version
def _WhileStmt(ast: asts.WhileStmt) -> list[Insn]:
    # ast.expr : Expr
    retval: list[Insn] = []
    retval.append(Label("START_LOOP_" + str(id(ast))))
    retval.extend(flow(ast.expr, "EXIT_LOOP_" + str(id(ast)), False))
    retval.extend(_CompoundStmt(ast.stmt))
    retval.append(Jump("START_LOOP_" + str(id(ast))))
    retval.append(Label("EXIT_LOOP_" + str(id(ast))))
    return retval


def _rval_Expr(ast: asts.Expr) -> list[Insn]:
    retval: list[Insn]
    match ast:
        case asts.ArrayCell():
            retval = _rval_ArrayCell(ast)
        case asts.BinaryOp():
            retval = _rval_BinaryOp(ast)
        case asts.BoolLiteral():
            retval = _rval_BoolLiteral(ast)
        case asts.CallExpr():
            retval = _rval_CallExpr(ast)
        case asts.IdExpr():
            retval = _rval_IdExpr(ast)
        case asts.IntLiteral():
            retval = _rval_IntLiteral(ast)
        case asts.UnaryOp():
            retval = _rval_UnaryOp(ast)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")
    return retval


def _rval_ArrayCell(ast: asts.ArrayCell) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    retval: list[Insn]
    _rval_Expr(ast.arr)
    _rval_Expr(ast.idx)
    return retval


def _rval_BinaryOp(ast: asts.BinaryOp) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.op : Token
    retval: list[Insn] = []
    if ast.op.value == "or":
        retval.extend(_rval_Expr(ast.left))
        retval.append(JumpIfNotZero(ast.left.register, "OR_TRUE_" + str(id(ast))))
        retval.extend(_rval_Expr(ast.right))
        retval.append(JumpIfNotZero(ast.right.register, "OR_TRUE_" + str(id(ast))))
        retval.append(Immediate(ast.register, 0))
        retval.append(Jump("OR_EXIT_" + str(id(ast))))
        retval.append(Label("OR_TRUE_" + str(id(ast))))
        retval.append(Immediate(ast.register, 1))
        retval.append(Label("OR_EXIT_" + str(id(ast))))
        return retval
    elif ast.op.value == "and":
        retval.extend(_rval_Expr(ast.left))
        retval.append(JumpIfZero(ast.left.register, "AND_FALSE_" + str(id(ast))))
        retval.extend(_rval_Expr(ast.right))
        retval.append(JumpIfZero(ast.right.register, "AND_FALSE_" + str(id(ast))))
        retval.append(Immediate(ast.register, 1))
        retval.append(Jump("AND_EXIT_" + str(id(ast))))
        retval.append(Label("AND_FALSE_" + str(id(ast))))
        retval.append(Immediate(ast.register, 0))
        retval.append(Label("AND_EXIT_" + str(id(ast))))
        return retval
    retval.extend(_rval_Expr(ast.left))
    retval.extend(_rval_Expr(ast.right))
    match ast.op.value:
        case "+":
            retval.append(Add(ast.register, ast.left.register, ast.right.register))
        case "-":
            retval.append(Sub(ast.register, ast.left.register, ast.right.register))
        case "*":
            retval.append(Mul(ast.register, ast.left.register, ast.right.register))
        case "/":
            retval.append(Div(ast.register, ast.left.register, ast.right.register))
        case "==":
            retval.append(Equal(ast.register, ast.left.register, ast.right.register))
        case "!=":
            retval.append(NotEqual(ast.register, ast.left.register, ast.right.register))
        case "<":
            retval.append(LessThan(ast.register, ast.left.register, ast.right.register))
        case "<=":
            retval.append(
                LessThanEqual(ast.register, ast.left.register, ast.right.register)
            )
        case ">":
            retval.append(
                GreaterThan(ast.register, ast.left.register, ast.right.register)
            )
        case ">=":
            retval.append(
                GreaterThanEqual(ast.register, ast.left.register, ast.right.register)
            )
    return retval


def _rval_BoolLiteral(ast: asts.BoolLiteral) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.token : Token
    # ast.value : bool
    retval: list[Insn] = []
    if str(ast.token.value) == "true":
        retval.append(Immediate(ast.register, 1))
    else:
        retval.append(Immediate(ast.register, 0))
    return retval


def _rval_CallExpr(ast: asts.CallExpr) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    retval: list[Insn] = []
    retval.append(AddImmediate("SP", "SP", len(ast.args) + 1))
    counter = -2
    for arg in ast.args:
        retval.extend(_rval_Argument(arg))
        retval.append(AddImmediate("curr", "SP", counter))
        retval.append(Store("curr", arg.expr.register))
        counter -= 1
    # this fixes mypy issue
    assert isinstance(ast.fn, asts.IdExpr)
    retval.append(Call(label=ast.fn.id.token.value))
    retval.append(AddImmediate("SP2", "SP", -1))
    retval.append(Load(ast.register, "SP2"))
    retval.append(AddImmediate("SP", "SP", -len(ast.args) - 1))
    return retval


def _rval_IdExpr(ast: asts.IdExpr) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.id : Id
    retval: list[Insn] = []
    retval.extend(_lval_Expr(ast))
    retval.append(Load(ast.register, ast.register))
    return retval


def _rval_IntLiteral(ast: asts.IntLiteral) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.token : Token
    retval: list[Insn] = []
    retval.append(Immediate(ast.register, int(ast.token.value)))
    return retval


def _rval_UnaryOp(ast: asts.UnaryOp) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.op : Token
    retval: list[Insn] = []
    retval.extend(_rval_Expr(ast.expr))
    match ast.op.value:
        case "-":
            retval.append(Sub(ast.register, "0", ast.expr.register))
        case "not":
            retval.append(Not(ast.register, ast.expr.register))
    return retval


def _rval_Argument(ast: asts.Argument) -> list[Insn]:
    # ast.semantic_type : SemanticType
    retval: list[Insn] = []
    retval.extend(_rval_Expr(ast.expr))
    return retval


def _lval_Expr(ast: asts.Expr) -> list[Insn]:
    retval: list[Insn]
    match ast:
        case asts.ArrayCell():
            retval = _lval_ArrayCell(ast)
        case asts.BinaryOp():
            retval = _lval_BinaryOp(ast)
        case asts.BoolLiteral():
            retval = _lval_BoolLiteral(ast)
        case asts.CallExpr():
            retval = _lval_CallExpr(ast)
        case asts.IdExpr():
            retval = _lval_IdExpr(ast)
        case asts.IntLiteral():
            retval = _lval_IntLiteral(ast)
        case asts.UnaryOp():
            retval = _lval_UnaryOp(ast)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")
    return retval


def _lval_ArrayCell(ast: asts.ArrayCell) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    retval: list[Insn]
    _lval_Expr(ast.arr)
    _lval_Expr(ast.idx)
    return retval


def _lval_BinaryOp(ast: asts.BinaryOp) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.op : Token
    retval: list[Insn]
    _lval_Expr(ast.left)
    _lval_Expr(ast.right)
    return retval


def _lval_BoolLiteral(ast: asts.BoolLiteral) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.token : Token
    # ast.value : bool
    retval: list[Insn]
    return retval


def _lval_CallExpr(ast: asts.CallExpr) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    retval: list[Insn]
    _lval_Expr(ast.fn)
    for arg in ast.args:
        _lval_Argument(arg)
    return retval


def _lval_IdExpr(ast: asts.IdExpr) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.id : Id
    retval: list[Insn] = []
    retval.append(AddImmediate(ast.register, "FP", ast.id.symbol.offset))
    return retval


def _lval_IntLiteral(ast: asts.IntLiteral) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.token : Token
    retval: list[Insn]
    return retval


def _lval_UnaryOp(ast: asts.UnaryOp) -> list[Insn]:
    # ast.semantic_type : SemanticType
    # ast.register : str
    # ast.op : Token
    retval: list[Insn]
    _lval_Expr(ast.expr)
    return retval


def _lval_Argument(ast: asts.Argument) -> list[Insn]:
    # ast.semantic_type : SemanticType
    retval: list[Insn] = []
    retval.extend(_lval_Expr(ast.expr))
    return retval


# TODO: fill out flow
def flow(ast: asts.Expr, lab: str, condition: bool) -> list[Insn]:
    retval: list[Insn] = []
    match ast:
        case asts.ArrayCell():
            retval = _flow_ArrayCell(ast, lab, condition)
        case asts.BinaryOp():
            retval = _flow_BinaryOp(ast, lab, condition)
        case asts.BoolLiteral():
            retval = _flow_BoolLiteral(ast, lab, condition)
        case asts.CallExpr():
            retval = _flow_CallExpr(ast, lab, condition)
        case asts.IdExpr():
            retval = _flow_IdExpr(ast, lab, condition)
        case asts.IntLiteral():
            retval = _flow_IntLiteral(ast, lab, condition)
        case asts.UnaryOp():
            retval = _flow_UnaryOp(ast, lab, condition)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")
    return retval


def _flow_ArrayCell(ast: asts.ArrayCell, lab: str, condition: bool) -> list[Insn]:
    # ast.register : str
    retval: list[Insn]
    return retval


def _flow_BinaryOp(ast: asts.BinaryOp, lab: str, condition: bool) -> list[Insn]:
    # ast.register : str
    # ast.op : Token
    retval: list[Insn] = []
    op = ast.op.value
    match op:
        case "and":
            if condition:
                retval.extend(flow(ast.left, "AND_LAB_" + str(id(ast)), False))
                retval.extend(flow(ast.right, lab, True))
                retval.append(Label("AND_LAB_" + str(id(ast))))
            else:
                retval.extend(flow(ast.left, lab, False))
                retval.extend(flow(ast.right, lab, False))
        case "or":
            if condition:
                retval.extend(flow(ast.left, lab, True))
                retval.extend(flow(ast.right, lab, True))
            else:
                retval.extend(flow(ast.left, "OR_LAB_" + str(id(ast)), True))
                retval.extend(flow(ast.right, lab, False))
                retval.append(Label("OR_LAB_" + str(id(ast))))
        case _:
            if condition:
                retval.extend(_rval_Expr(ast))
                retval.append(JumpIfNotZero(ast.register, lab))
            else:
                retval.extend(_rval_Expr(ast))
                retval.append(JumpIfZero(ast.register, lab))
    return retval


def _flow_BoolLiteral(ast: asts.BoolLiteral, lab: str, condition: bool) -> list[Insn]:
    # ast.register : str
    # ast.value : bool
    retval: list[Insn] = []
    if condition == ast.value:
        retval.append(Jump(lab))
    return retval


def _flow_CallExpr(ast: asts.CallExpr, lab: str, condition: bool) -> list[Insn]:
    # ast.register : str
    retval: list[Insn]
    # ast.fn, ast.args
    return retval


def _flow_IdExpr(ast: asts.IdExpr, lab: str, condition: bool) -> list[Insn]:
    # ast.register : str
    retval: list[Insn]
    return retval


def _flow_IntLiteral(ast: asts.IntLiteral, lab: str, condition: bool) -> list[Insn]:
    # ast.register : str
    retval: list[Insn]
    return retval


def _flow_UnaryOp(ast: asts.UnaryOp, lab: str, condition: bool) -> list[Insn]:
    # ast.register : str
    # ast.op : Token
    retval: list[Insn] = []
    if ast.op.value == "not":
        retval.extend(flow(ast.expr, lab, not condition))
    else:
        raise NotImplementedError(f"Unknown type {ast}")
    return retval
