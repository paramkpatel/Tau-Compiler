# pyright: reportUnboundVariable=none, reportUnusedFunction=none
# REMEMBER TO REMOVE THE pyright DIRECTIVE ABOVE!!!!!!

from tau import asts, symbols


# Context is placeholder class for your use.
# You can add whatever you want to it.
class Context:
    return_type: asts.FuncDecl = None


def process(ast: asts.Program) -> None:
    _Program(ast)


def _Program(ast: asts.Program) -> None:
    ctx = Context()  # <--- fix this!!!
    func_bank = set()
    for decl in ast.decls:
        if isinstance(decl, asts.FuncDecl):
            if decl.id.token.value in func_bank:
                raise NameError(f"Redefinition of symbol, {decl.span}")
            func_bank.add(decl.id.token.value)
        ctx.return_type = decl
        _FuncDecl(decl, ctx)


def _Argument(ast: asts.Argument, ctx: Context) -> None:
    _Expr(ast.expr, ctx)
    ast.semantic_type = ast.expr.semantic_type


def _Id(ast: asts.Id, ctx: Context) -> None:
    # ast.token : Token
    # ast.symbol : Symbol
    ast.semantic_type = ast.symbol.get_type()


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
    _Id(ast.id, ctx)
    param_array = []
    for param in ast.params:
        _ParamDecl(param, ctx)
        param_array.append(param.semantic_type)
    _TypeAST(ast.ret_type_ast, ctx)
    ast.semantic_type = symbols.FuncType(param_array, ast.ret_type_ast.semantic_type)
    ast.id.semantic_type = ast.semantic_type
    ast.id.symbol.set_type(ast.semantic_type)
    _CompoundStmt(ast.body, ctx)


def _ParamDecl(ast: asts.ParamDecl, ctx: Context) -> None:
    _Id(ast.id, ctx)
    _TypeAST(ast.type_ast, ctx)
    ast.id.semantic_type = ast.type_ast.semantic_type
    ast.semantic_type = ast.type_ast.semantic_type
    ast.id.symbol.set_type(ast.semantic_type)


def _VarDecl(ast: asts.VarDecl, ctx: Context) -> None:
    _Id(ast.id, ctx)
    _TypeAST(ast.type_ast, ctx)
    ast.id.semantic_type = ast.type_ast.semantic_type
    ast.semantic_type = ast.type_ast.semantic_type
    ast.id.symbol.set_type(ast.semantic_type)


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
    _Expr(ast.arr, ctx)
    _Expr(ast.idx, ctx)


def _BinaryOp(ast: asts.BinaryOp, ctx: Context) -> None:
    _Expr(ast.left, ctx)
    _Expr(ast.right, ctx)
    if ast.op.value in {"+", "-", "*", "/"}:
        if not isinstance(ast.left.semantic_type, symbols.IntType) or not isinstance(
            ast.right.semantic_type, symbols.IntType
        ):
            raise TypeError("TypeError")
        ast.semantic_type = symbols.IntType()
    elif ast.op.value in {"<", ">", "<=", ">=", "==", "!=", "and", "or"}:
        if type(ast.left.semantic_type) is not type(ast.right.semantic_type):
            raise TypeError(f"{ast.op.value} needs to be same type", ast.span)
        if ast.op.value in {"and", "or"} and not isinstance(
            ast.left.semantic_type, symbols.BoolType
        ):
            raise TypeError("TypeError")
        ast.semantic_type = symbols.BoolType()


def _BoolLiteral(ast: asts.BoolLiteral, ctx: Context) -> None:
    # ast.token : Token
    # ast.value : bool
    ast.semantic_type = symbols.BoolType()


def _CallExpr(ast: asts.CallExpr, ctx: Context) -> None:
    _Expr(ast.fn, ctx)
    for arg in ast.args:
        _Argument(arg, ctx)
    temp = ast.fn.semantic_type
    assert isinstance(temp, symbols.FuncType)
    ast.semantic_type = temp.ret
    if len(ast.args) != len(temp.params):
        raise TypeError("incorrect number of args")


def _IdExpr(ast: asts.IdExpr, ctx: Context) -> None:
    _Id(ast.id, ctx)
    ast.semantic_type = ast.id.semantic_type


def _IntLiteral(ast: asts.IntLiteral, ctx: Context) -> None:
    # ast.token : Token
    ast.semantic_type = symbols.IntType()


def _UnaryOp(ast: asts.UnaryOp, ctx: Context) -> None:
    # ast.op : Token
    _Expr(ast.expr, ctx)
    if ast.op.value == "-":
        if not isinstance(ast.expr.semantic_type, symbols.IntType):
            raise TypeError(f"TypeError", ast.span)
        ast.semantic_type = symbols.IntType()
    elif ast.op.value == "not":
        if not isinstance(ast.expr.semantic_type, symbols.BoolType):
            raise TypeError(f"TypeError", ast.span)
        ast.semantic_type = symbols.BoolType()
    else:
        raise TypeError(f"Invalid: {ast.op.value}", ast.span)


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
    if type(ast.lhs.semantic_type) is not type(ast.rhs.semantic_type):
        raise TypeError(f"Not same type")


def _CallStmt(ast: asts.CallStmt, ctx: Context) -> None:
    _CallExpr(ast.call, ctx)


def _CompoundStmt(ast: asts.CompoundStmt, ctx: Context) -> None:
    for decl in ast.decls:
        _VarDecl(decl, ctx)
    for stmt in ast.stmts:
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
    ast.enclosing_function = ctx.return_type
    if not isinstance(
        ast.expr.semantic_type, type(ctx.return_type.ret_type_ast.semantic_type)
    ):
        raise TypeError("invalid return type")


def _WhileStmt(ast: asts.WhileStmt, ctx: Context) -> None:
    _Expr(ast.expr, ctx)
    _CompoundStmt(ast.stmt, ctx)


def _TypeAST(ast: asts.TypeAST, ctx: Context) -> None:
    match ast:
        case asts.ArrayType():
            _ArrayType(ast, ctx)
        case asts.BoolType():
            _BoolType(ast, ctx)
        case asts.IntType():
            _IntType(ast, ctx)
        case asts.VoidType():
            _VoidType(ast, ctx)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _ArrayType(ast: asts.ArrayType, ctx: Context) -> None:
    _TypeAST(ast.element_type_ast, ctx)


def _BoolType(ast: asts.BoolType, ctx: Context) -> None:
    # ast.token : Token
    ast.semantic_type = symbols.BoolType()


def _IntType(ast: asts.IntType, ctx: Context) -> None:
    # ast.token : Token
    ast.semantic_type = symbols.IntType()


def _VoidType(ast: asts.VoidType, ctx: Context) -> None:
    # ast.token : Token
    ast.semantic_type = symbols.VoidType()
