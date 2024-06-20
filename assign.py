# pyright: reportUnboundVariable=none, reportUnusedFunction=none
# REMEMBER TO REMOVE THE pyright DIRECTIVE ABOVE!!!!!!

from tau import asts


class Context:
    register_pool: list[str]

    def __init__(self) -> None:
        self.curr_register = 1


def process(ast: asts.Program) -> None:
    _Program(ast)


def _Program(ast: asts.Program) -> None:
    # ast.register_pool : list[str]
    ctx = Context()  # <--- fix this!!
    for decl in ast.decls:
        ctx.register_pool = []
        _FuncDecl(decl, ctx)
        ctx.curr_register = 1


def _Decl(ast: asts.Decl, ctx: Context) -> None:
    match ast:
        case asts.FuncDecl():
            _FuncDecl(ast, ctx)
        case asts.ParamDecl():
            _ParamDecl(ast, ctx)
        case asts.VarDecl():
            _VarDecl(ast, ctx)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _FuncDecl(ast: asts.FuncDecl, ctx: Context) -> None:
    # ast.id : Id
    # ast.ret_type_ast : TypeAST
    # ast.register_pool : list[str]
    for param in ast.params:
        _ParamDecl(param, ctx)
    _CompoundStmt(ast.body, ctx)


def _ParamDecl(ast: asts.ParamDecl, ctx: Context) -> None:
    # ast.id : Id
    # ast.type_ast : TypeAST
    pass


def _VarDecl(ast: asts.VarDecl, ctx: Context) -> None:
    # ast.id : Id
    # ast.type_ast : TypeAST
    pass


def _Stmt(ast: asts.Stmt, ctx: Context) -> None:
    match ast:
        case asts.AssignStmt():
            _AssignStmt(ast, ctx)
        case asts.CallStmt():
            _CallStmt(ast, ctx)
        case asts.CompoundStmt():
            _CompoundStmt(ast, ctx)
        case asts.IfStmt():
            _IfStmt(ast, ctx)
        case asts.PrintStmt():
            _PrintStmt(ast, ctx)
        case asts.ReturnStmt():
            _ReturnStmt(ast, ctx)
        case asts.WhileStmt():
            _WhileStmt(ast, ctx)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _AssignStmt(ast: asts.AssignStmt, ctx: Context) -> None:
    _Expr(ast.lhs, ctx)
    _Expr(ast.rhs, ctx)


def _CallStmt(ast: asts.CallStmt, ctx: Context) -> None:
    _CallExpr(ast.call, ctx)


def _CompoundStmt(ast: asts.CompoundStmt, ctx: Context) -> None:
    for decl in ast.decls:
        _VarDecl(decl, ctx)
    for stmt in ast.stmts:
        ctx.curr_register = 1
        _Stmt(stmt, ctx)


def _IfStmt(ast: asts.IfStmt, ctx: Context) -> None:
    _Expr(ast.expr, ctx)
    _CompoundStmt(ast.thenStmt, ctx)
    if ast.elseStmt:
        _CompoundStmt(ast.elseStmt, ctx)


def _PrintStmt(ast: asts.PrintStmt, ctx: Context) -> None:
    _Expr(ast.expr, ctx)


def _ReturnStmt(ast: asts.ReturnStmt, ctx: Context) -> None:
    if ast.expr:
        _Expr(ast.expr, ctx)


def _WhileStmt(ast: asts.WhileStmt, ctx: Context) -> None:
    _Expr(ast.expr, ctx)
    _CompoundStmt(ast.stmt, ctx)


def _Expr(ast: asts.Expr, ctx: Context) -> None:
    match ast:
        case asts.ArrayCell():
            _ArrayCell(ast, ctx)
        case asts.BinaryOp():
            _BinaryOp(ast, ctx)
        case asts.BoolLiteral():
            _BoolLiteral(ast, ctx)
        case asts.CallExpr():
            _CallExpr(ast, ctx)
        case asts.IdExpr():
            _IdExpr(ast, ctx)
        case asts.IntLiteral():
            _IntLiteral(ast, ctx)
        case asts.UnaryOp():
            _UnaryOp(ast, ctx)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _ArrayCell(ast: asts.ArrayCell, ctx: Context) -> None:
    # ast.register : str <--- set this!!
    ast.register = "r" + str(ctx.curr_register)
    _Expr(ast.arr, ctx)
    _Expr(ast.idx, ctx)


def _BinaryOp(ast: asts.BinaryOp, ctx: Context) -> None:
    # ast.register : str <--- set this!!
    ast.register = "r" + str(ctx.curr_register)
    _Expr(ast.left, ctx)
    _Expr(ast.right, ctx)
    ctx.curr_register -= 1


def _BoolLiteral(ast: asts.BoolLiteral, ctx: Context) -> None:
    # ast.register : str <--- set this!!
    ast.register = "r" + str(ctx.curr_register)
    ctx.curr_register += 1


def _CallExpr(ast: asts.CallExpr, ctx: Context) -> None:
    # ast.register : str <--- set this!!
    ast.register = "r" + str(ctx.curr_register)
    _Expr(ast.fn, ctx)
    for arg in ast.args:
        _Argument(arg, ctx)
        ctx.curr_register -= 1


def _IdExpr(ast: asts.IdExpr, ctx: Context) -> None:
    # ast.register : str <--- set this!!
    # ast.id : Id
    ast.register = "r" + str(ctx.curr_register)
    ctx.curr_register += 1


def _IntLiteral(ast: asts.IntLiteral, ctx: Context) -> None:
    # ast.register : str <--- set this!!
    ast.register = "r" + str(ctx.curr_register)
    ctx.curr_register += 1


def _UnaryOp(ast: asts.UnaryOp, ctx: Context) -> None:
    # ast.register : str <--- set this!!
    ast.register = "r" + str(ctx.curr_register)
    _Expr(ast.expr, ctx)


def _Argument(ast: asts.Argument, ctx: Context) -> None:
    _Expr(ast.expr, ctx)
