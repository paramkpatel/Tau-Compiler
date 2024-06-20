# pyright: reportUnboundVariable=none, reportUnusedFunction=none
# REMEMBER TO REMOVE THE pyright DIRECTIVE ABOVE!!!!!!

from tau import asts


def process(ast: asts.Program) -> None:
    _Program(ast)


def _Program(ast: asts.Program) -> int:
    current = -2
    retval: int = 0
    for decl in ast.decls:
        _FuncDecl(decl, current)
    return retval


def _Decl(ast: asts.Decl, current: int) -> int:
    retval: int
    match ast:
        case asts.FuncDecl():
            retval = _FuncDecl(ast, current)
        case asts.ParamDecl():
            retval = _ParamDecl(ast, current)
        case asts.VarDecl():
            retval = _VarDecl(ast, current)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")
    return retval


def _FuncDecl(ast: asts.FuncDecl, current: int) -> int:
    # ast.id : Id
    # ast.ret_type_ast : TypeAST
    retval: int = 0
    for param in ast.params:
        current = _ParamDecl(param, current)
    current = 0
    retval = _CompoundStmt(ast.body, current)
    ast.size = retval + 3
    return retval


def _ParamDecl(ast: asts.ParamDecl, current: int) -> int:
    # ast.id : Id
    # ast.type_ast : TypeAST
    retval: int = current
    ast.id.symbol.offset = current
    retval = current - 1
    return retval


def _VarDecl(ast: asts.VarDecl, current: int) -> int:
    # ast.id : Id
    # ast.type_ast : TypeAST
    retval: int = current
    ast.id.symbol.offset = current + 3
    retval = current + 1
    return retval


def _Stmt(ast: asts.Stmt, current: int) -> int:
    retval: int = 0
    match ast:
        case asts.AssignStmt():
            retval = _AssignStmt(ast, current)
        case asts.CallStmt():
            retval = _CallStmt(ast, current)
        case asts.CompoundStmt():
            retval = _CompoundStmt(ast, current)
        case asts.IfStmt():
            retval = _IfStmt(ast, current)
        case asts.PrintStmt():
            retval = _PrintStmt(ast, current)
        case asts.ReturnStmt():
            retval = _ReturnStmt(ast, current)
        case asts.WhileStmt():
            retval = _WhileStmt(ast, current)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")
    return retval


def _AssignStmt(ast: asts.AssignStmt, current: int) -> int:
    retval: int = 0
    return retval


def _CallStmt(ast: asts.CallStmt, current: int) -> int:
    retval: int = 0
    return retval


def _CompoundStmt(ast: asts.CompoundStmt, current: int) -> int:
    retval: int = current
    for decl in ast.decls:
        current = _VarDecl(decl, current)
    retval = current
    for stmt in ast.stmts:
        temp = _Stmt(stmt, current)
        if temp > retval:
            retval = temp
    return retval


def _IfStmt(ast: asts.IfStmt, current: int) -> int:
    retval: int = 0
    _CompoundStmt(ast.thenStmt, current)
    if ast.elseStmt:
        _CompoundStmt(ast.elseStmt, current)
    return retval


def _PrintStmt(ast: asts.PrintStmt, current: int) -> int:
    retval: int = 0
    return retval


def _ReturnStmt(ast: asts.ReturnStmt, current: int) -> int:
    retval: int = 0
    return retval


def _WhileStmt(ast: asts.WhileStmt, current: int) -> int:
    retval: int = 0
    _CompoundStmt(ast.stmt, current)
    return retval
