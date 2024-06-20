# pyright: reportUnboundVariable=none, reportUnusedFunction=none
# REMEMBER TO REMOVE THE pyright DIRECTIVE ABOVE!!!!!!

from tau import asts, symbols


def process(ast: asts.Program) -> None:
    _Program(ast)


def _Program(ast: asts.Program) -> None:
    # ast.span : Span <--- set this
    temp = symbols.GlobalScope(ast.span)
    for decl in ast.decls:
        temp.symtab[decl.id.token.value] = symbols.Symbol(decl.id.token.value, temp)
        _FuncDecl(decl, temp)


def _Argument(ast: asts.Argument, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Expr(ast.expr, scope)


def _Id(ast: asts.Id, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.token : Token
    # ast.symbol : Symbol <--- set this!!
    if isinstance(scope, symbols.LocalScope) and ast.token.value in scope.symtab:
        raise Exception(f"duplicate identifier")
    ast.symbol = symbols.Symbol(ast.token.value, scope)
    scope.symtab[ast.token.value] = ast.symbol


def _Decl(ast: asts.Decl, scope: symbols.Scope) -> None:
    match ast:
        case asts.FuncDecl():
            _FuncDecl(ast, scope)
        case asts.ParamDecl():
            _ParamDecl(ast, scope)
        case asts.VarDecl():
            _VarDecl(ast, scope)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _FuncDecl(ast: asts.FuncDecl, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.func_scope : Scope <--- set this!!
    _Id(ast.id, scope)
    ast.func_scope = symbols.FuncScope(span=ast.span, parent=scope)
    for param in ast.params:
        _ParamDecl(param, ast.func_scope)
    _TypeAST(ast.ret_type_ast, ast.func_scope)
    _CompoundStmt(ast.body, ast.func_scope)


def _ParamDecl(ast: asts.ParamDecl, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Id(ast.id, scope)
    _TypeAST(ast.type_ast, scope)


def _VarDecl(ast: asts.VarDecl, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Id(ast.id, scope)
    _TypeAST(ast.type_ast, scope)


def _Expr(ast: asts.Expr, scope: symbols.Scope) -> None:
    match ast:
        case asts.ArrayCell():
            _ArrayCell(ast, scope)
        case asts.BinaryOp():
            _BinaryOp(ast, scope)
        case asts.BoolLiteral():
            _BoolLiteral(ast, scope)
        case asts.CallExpr():
            _CallExpr(ast, scope)
        case asts.IdExpr():
            _IdExpr(ast, scope)
        case asts.IntLiteral():
            _IntLiteral(ast, scope)
        case asts.UnaryOp():
            _UnaryOp(ast, scope)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _ArrayCell(ast: asts.ArrayCell, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Expr(ast.arr, scope)
    _Expr(ast.idx, scope)


def _BinaryOp(ast: asts.BinaryOp, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.op : Token
    _Expr(ast.left, scope)
    _Expr(ast.right, scope)


def _BoolLiteral(ast: asts.BoolLiteral, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.token : Token
    # ast.value : bool
    pass


def _CallExpr(ast: asts.CallExpr, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Expr(ast.fn, scope)
    for arg in ast.args:
        _Argument(arg, scope)


def _IdExpr(ast: asts.IdExpr, scope: symbols.Scope) -> None:
    # ast.span : Span <--- set this!!
    if scope.lookup(ast.id.token.value) is None:
        raise NameError(f"undefined symbol {ast.span}")
    else:
        ast.id.symbol = scope.lookup(ast.id.token.value)


def _IntLiteral(ast: asts.IntLiteral, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.token : Token
    pass


def _UnaryOp(ast: asts.UnaryOp, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.op : Token
    _Expr(ast.expr, scope)


def _Stmt(ast: asts.Stmt, scope: symbols.Scope) -> None:
    match ast:
        case asts.AssignStmt():
            _AssignStmt(ast, scope)
        case asts.CallStmt():
            _CallStmt(ast, scope)
        case asts.CompoundStmt():
            _CompoundStmt(ast, scope)
        case asts.IfStmt():
            _IfStmt(ast, scope)
        case asts.PrintStmt():
            _PrintStmt(ast, scope)
        case asts.ReturnStmt():
            _ReturnStmt(ast, scope)
        case asts.WhileStmt():
            _WhileStmt(ast, scope)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _AssignStmt(ast: asts.AssignStmt, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Expr(ast.lhs, scope)
    _Expr(ast.rhs, scope)


def _CallStmt(ast: asts.CallStmt, scope: symbols.Scope) -> None:
    # ast.span : Span
    _CallExpr(ast.call, scope)


def _CompoundStmt(ast: asts.CompoundStmt, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.local_scope : Scope <--- set this!!
    ast.local_scope = symbols.LocalScope(span=ast.span, parent=scope)
    for decl in ast.decls:
        _VarDecl(decl, ast.local_scope)
    for stmt in ast.stmts:
        _Stmt(stmt, ast.local_scope)


def _IfStmt(ast: asts.IfStmt, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Expr(ast.expr, scope)
    _CompoundStmt(ast.thenStmt, scope)
    if ast.elseStmt:
        _CompoundStmt(ast.elseStmt, scope)


def _PrintStmt(ast: asts.PrintStmt, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Expr(ast.expr, scope)


def _ReturnStmt(ast: asts.ReturnStmt, scope: symbols.Scope) -> None:
    # ast.span : Span
    if ast.expr:
        _Expr(ast.expr, scope)


def _WhileStmt(ast: asts.WhileStmt, scope: symbols.Scope) -> None:
    # ast.span : Span
    _Expr(ast.expr, scope)
    _CompoundStmt(ast.stmt, scope)


def _TypeAST(ast: asts.TypeAST, scope: symbols.Scope) -> None:
    match ast:
        case asts.ArrayType():
            _ArrayType(ast, scope)
        case asts.BoolType():
            _BoolType(ast, scope)
        case asts.IntType():
            _IntType(ast, scope)
        case asts.VoidType():
            _VoidType(ast, scope)
        case _:
            raise NotImplementedError(f"Unknown type {ast}")


def _ArrayType(ast: asts.ArrayType, scope: symbols.Scope) -> None:
    # ast.span : Span
    _TypeAST(ast.element_type_ast, scope)


def _BoolType(ast: asts.BoolType, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.token : Token
    pass


def _IntType(ast: asts.IntType, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.token : Token
    pass


def _VoidType(ast: asts.VoidType, scope: symbols.Scope) -> None:
    # ast.span : Span
    # ast.token : Token
    pass
