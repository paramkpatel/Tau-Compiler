from tau.tokens import Span, Token
from tau import asts

from typing import NoReturn, Iterable, Iterator


class ParseErrorException(Exception):
    msg: str
    token: Token
    expected: set[str]

    def __init__(self, msg: str, current: Token, expected: set[str]):
        self.msg = msg
        self.current = current
        self.expected = expected

    def __str__(self) -> str:
        return f"Parse error {self.msg} at {self.current}:  Expected {self.expected}"


class Parser:
    scanner: Iterator[Token]
    _current: Token

    def __init__(
        self,
        scanner: Iterable[Token],
    ):
        self.scanner: Iterator[Token] = iter(scanner)
        self._current = next(self.scanner)

    def error(self, msg: str, expected: set[str]) -> NoReturn:
        raise ParseErrorException(msg, self._current, expected)

    def match(self, kind: str) -> Token:
        if self.current() == kind:
            prev: Token = self._current
            try:
                self._current = next(self.scanner)
            except StopIteration:
                pass
            return prev
        else:
            self.error("", {kind})

    def current(self) -> str:
        return self._current.kind

    def parse(self) -> asts.Program:
        v = self._grammar()
        self.match("EOF")
        return v

    def _grammar(self) -> asts.Program:
        # grammar -> function { function }
        func_array = []
        func_array.append(self._function())
        while self.current() in {"func"}:
            func_array.append(self._function())
        return asts.Program(
            decls=func_array,
            span=Span(func_array[0].span.start, func_array[-1].span.end),
        )

    def _function(self) -> asts.FuncDecl:
        # function -> "func" ID "(" [ parameter { "," parameter } ] ")" ":" type compound_statement
        fun = self.match("func")
        token_ID = self.match("ID")
        node_ID = asts.Id(token=token_ID, span=token_ID.span)
        self.match("(")
        param_array = []
        if self.current() in {"ID"}:
            param_array.append(self._parameter())
            while self.current() in {","}:
                self.match(",")
                param_array.append(self._parameter())
        self.match(")")
        self.match(":")
        token_ret = self._type()
        ret_node = self._compound_statement()
        return asts.FuncDecl(
            id=node_ID,
            params=param_array,
            ret_type_ast=token_ret,
            body=ret_node,
            span=Span(fun.span.start, ret_node.span.end),
        )

    def _parameter(self) -> asts.ParamDecl:
        # parameter -> ID [ ":" type ]
        param_id = self.match("ID")
        param_node = asts.Id(token=param_id, span=param_id.span)
        typ_node = None
        if self.current() in {":"}:
            self.match(":")
            typ_node = self._type()
        return asts.ParamDecl(
            id=param_node,
            type_ast=typ_node,
            span=Span(param_id.span.start, typ_node.span.end),
        )

    def _compound_statement(self) -> asts.CompoundStmt:
        # compound_statement -> "{" { variable_declaration | statement } [ return_statement ] "}"
        curly = self.match("{")
        var_dec = []
        stat_array = []
        while self.current() in {"call", "if", "print", "var", "while", "{", "ID"}:
            if self.current() in {"var"}:
                var_dec.append(self._variable_declaration())
            elif self.current() in {"call", "if", "print", "while", "{", "ID"}:
                stat_array.append(self._statement())
            else:
                self.error(
                    "syntax error", {"call", "if", "print", "var", "while", "{", "ID"}
                )
        if self.current() in {"return"}:
            stat_array.append(self._return_statement())
        end_curly = self.match("}")
        return asts.CompoundStmt(
            decls=var_dec,
            stmts=stat_array,
            span=Span(curly.span.start, end_curly.span.end),
        )

    def _variable_declaration(self) -> asts.VarDecl:
        # variable_declaration -> "var" ID ":" type
        var_start = self.match("var")
        token_ID = self.match("ID")
        node = asts.Id(token=token_ID, span=token_ID.span)
        self.match(":")
        typ_node = self._type()
        return asts.VarDecl(
            id=node,
            type_ast=typ_node,
            span=Span(var_start.span.start, typ_node.span.end),
        )

    def _statement(self) -> asts.Stmt:
        # statement -> if_statement | while_statement | print_statement | call_statement | assignment_statement | compound_statement
        if self.current() in {"if"}:
            return self._if_statement()
        elif self.current() in {"while"}:
            return self._while_statement()
        elif self.current() in {"print"}:
            return self._print_statement()
        elif self.current() in {"call"}:
            return self._call_statement()
        elif self.current() in {"ID"}:
            return self._assignment_statement()
        elif self.current() in {"{"}:
            return self._compound_statement()
        else:
            self.error("syntax error", {"call", "if", "print", "while", "{", "ID"})

    def _if_statement(self) -> asts.IfStmt:
        # if_statement -> "if" expression compound_statement [ "else" compound_statement ]
        if_start = self.match("if")
        exp = self._expression()
        comp = self._compound_statement()
        else_comp = None
        if self.current() in {"else"}:
            self.match("else")
            else_comp = self._compound_statement()
        end_span = else_comp.span.end if else_comp else comp.span.end
        return asts.IfStmt(
            expr=exp,
            thenStmt=comp,
            elseStmt=else_comp,
            span=Span(if_start.span.start, end_span),
        )

    def _while_statement(self) -> asts.WhileStmt:
        # while_statement -> "while" expression compound_statement
        start = self.match("while")
        exp_node = self._expression()
        stat_node = self._compound_statement()
        end = stat_node
        return asts.WhileStmt(
            expr=exp_node, stmt=stat_node, span=Span(start.span.start, end.span.end)
        )

    def _print_statement(self) -> asts.PrintStmt:
        # print_statement -> "print" expression
        start = self.match("print")
        pr_exp = self._expression()
        return asts.PrintStmt(expr=pr_exp, span=Span(start.span.start, pr_exp.span.end))

    def _call_statement(self) -> asts.CallStmt:
        # call_statement -> "call" ID function_call
        call_start = self.match("call")
        match_id = self.match("ID")
        param = asts.IdExpr(match_id.span, asts.Id(match_id.span, match_id))
        temp = self._function_call(param)

        return asts.CallStmt(call=temp, span=Span(call_start.span.start, temp.span.end))

    def _assignment_statement(self) -> asts.AssignStmt:
        # assignment_statement -> ID [ array_index ] "=" expression
        id_token = self.match("ID")
        node = asts.IdExpr(
            id=asts.Id(token=id_token, span=id_token.span), span=id_token.span
        )
        temp: asts.Expr = node
        if self.current() in {"["}:
            temp = self._array_index(node)
        self.match("=")
        temp2 = self._expression()
        return asts.AssignStmt(
            lhs=temp, rhs=temp2, span=Span(id_token.span.start, temp2.span.end)
        )

    def _return_statement(self) -> asts.ReturnStmt:
        # return_statement -> "return" [ expression ]
        start_ret = self.match("return")
        end = start_ret.span.end
        node = None
        if self.current() in {"(", "-", "false", "not", "true", "ID", "INT"}:
            node = self._expression()
            end = node.span.end
        return asts.ReturnStmt(expr=node, span=Span(start_ret.span.start, end))

    def _expression(self) -> asts.Expr:
        # expression -> logical_or_expression
        return self._logical_or_expression()

    def _logical_or_expression(self) -> asts.Expr:
        # logical_or_expression -> logical_and_expression { "or" logical_and_expression }
        l_exp = self._logical_and_expression()
        while self.current() in {"or"}:
            or_token = self.match("or")
            r_exp = self._logical_and_expression()
            l_exp = asts.BinaryOp(
                op=or_token,
                left=l_exp,
                right=r_exp,
                span=Span(l_exp.span.start, r_exp.span.end),
            )
        return l_exp

    def _logical_and_expression(self) -> asts.Expr:
        # logical_and_expression -> comparison_expression { "and" comparison_expression }
        comp = self._comparison_expression()
        while self.current() in {"and"}:
            and_token = self.match("and")
            comp2 = self._comparison_expression()
            comp = asts.BinaryOp(
                op=and_token,
                left=comp,
                right=comp2,
                span=Span(comp.span.start, comp2.span.end),
            )
        return comp

    def _comparison_expression(self) -> asts.Expr:
        # comparison_expression -> addition_expression { comparison_operator addition_expression }
        left_expr = self._addition_expression()
        while self.current() in {"!=", "<", "<=", "==", ">", ">="}:
            op_token = self.match(self.current())
            right_expr = self._addition_expression()
            left_expr = asts.BinaryOp(
                op=op_token,
                left=left_expr,
                right=right_expr,
                span=Span(start=left_expr.span.start, end=right_expr.span.end),
            )
        return left_expr

    def _addition_expression(self) -> asts.Expr:
        # addition_expression -> multiplication_expression { plus_min multiplication_expression }
        mul = self._multiplication_expression()
        while self.current() in {"+", "-"}:
            op_token = self._plus_min()
            mul2 = self._multiplication_expression()
            mul = asts.BinaryOp(
                op=op_token,
                left=mul,
                right=mul2,
                span=Span(mul.span.start, mul2.span.end),
            )
        return mul

    def _multiplication_expression(self) -> asts.Expr:
        # multiplication_expression -> not_expression { multi_div not_expression }
        not_exp = self._not_expression()
        while self.current() in {"*", "/"}:
            op_token = self._multi_div()
            not_exp2 = self._not_expression()
            not_exp = asts.BinaryOp(
                op=op_token,
                left=not_exp,
                right=not_exp2,
                span=Span(not_exp.span.start, not_exp2.span.end),
            )
        return not_exp

    def _not_expression(self) -> asts.Expr:
        # not_expression -> { "not" | "-" } primary_expression
        not_array = []
        while self.current() in {"-", "not"}:
            if self.current() in {"not"}:
                not_array.append(self.match("not"))
            elif self.current() in {"-"}:
                not_array.append(self.match("-"))
            else:
                self.error("syntax error", {"-", "not"})
        first = self._primary_expression()
        for tok in reversed(not_array):
            first = asts.UnaryOp(
                op=tok, expr=first, span=Span(tok.span.start, first.span.end)
            )
        return first

    def _primary_expression(self) -> asts.Expr:
        # primary_expression -> INT | boolean | ID [ function_call | array_index ] | "(" expression ")"
        if self.current() in {"INT"}:
            int_token = self.match("INT")
            return asts.IntLiteral(token=int_token, span=int_token.span)
        elif self.current() in {"false", "true"}:
            return self._boolean()
        elif self.current() in {"ID"}:
            token = self.match("ID")
            base = asts.IdExpr(
                span=token.span, id=asts.Id(token=token, span=token.span)
            )
            if self.current() in {"(", "["}:
                if self.current() == "(":
                    return self._function_call(base)
                elif self.current() == "[":
                    return self._array_index(base)
                else:
                    self.error("syntax error", {"(", "["})
            return base
        elif self.current() in {"("}:
            self.match("(")
            expr_node = self._expression()
            self.match(")")
            return expr_node
        else:
            self.error("syntax error", {"(", "false", "true", "ID", "INT"})

    def _function_call(self, name: asts.IdExpr) -> asts.CallExpr:
        # function_call -> "(" [ expression { "," expression } ] ")"
        self.match("(")
        func_args = []
        if self.current() in {"(", "-", "false", "not", "true", "ID", "INT"}:
            exp = self._expression()
            func_args.append(asts.Argument(expr=exp, span=exp.span))
            while self.current() in {","}:
                self.match(",")
                exp = self._expression()
                func_args.append(asts.Argument(expr=exp, span=exp.span))
        end = self.match(")")
        return asts.CallExpr(
            span=Span(start=name.span.start, end=end.span.end),
            fn=name,
            args=func_args,
        )

    def _array_index(self, name: asts.IdExpr) -> asts.ArrayCell:
        if self.current() in {"["}:
            start = self.match("[")
            index = self._expression()
            end = self.match("]")
        return asts.ArrayCell(
            idx=index, arr=name, span=Span(name.span.start, end.span.end)
        )

    def _type(self) -> asts.TypeAST:
        # type -> "void" | "int" | "bool" | array_type
        if self.current() in {"void"}:
            void_match = self.match("void")
            return asts.VoidType(void_match.span, void_match)
        elif self.current() in {"int"}:
            int_match = self.match("int")
            return asts.IntType(int_match.span, int_match)
        elif self.current() in {"bool"}:
            bool_match = self.match("bool")
            return asts.BoolType(bool_match.span, bool_match)
        elif self.current() in {"["}:
            bracket_match = self._array_type()
            return asts.ArrayType(
                span=bracket_match.span,
                size=bracket_match.size,
                element_type_ast=bracket_match.element_type_ast,
            )
        else:
            self.error("syntax error", {"[", "bool", "int", "void"})

    def _array_type(self) -> asts.ArrayType:
        # array_type -> "[" [ INT ] "]" "int"
        array_start = self.match("[")
        tkn_size = None
        if self.current() in {"INT"}:
            tkn_size = self.match("INT")
        self.match("]")
        int_match = self.match("int")
        param = asts.IntType(int_match.span, int_match)
        span = Span(array_start.span.start, param.span.end)
        return asts.ArrayType(size=tkn_size, element_type_ast=param, span=span)

    def _boolean(self) -> asts.BoolLiteral:
        # boolean -> "true" | "false"
        if self.current() in {"true"}:
            true_start = self.match("true")
            return asts.BoolLiteral(true_start.span, true_start, True)
        elif self.current() in {"false"}:
            false_start = self.match("false")
            return asts.BoolLiteral(false_start.span, false_start, False)
        else:
            self.error("syntax error", {"false", "true"})

    def _comparison_operator(self) -> Token:
        # comparison_operator -> "<" | "<=" | "==" | "!=" | ">" | ">="
        if self.current() in {"<"}:
            return self.match("<")
        elif self.current() in {"<="}:
            return self.match("<=")
        elif self.current() in {"=="}:
            return self.match("==")
        elif self.current() in {"!="}:
            return self.match("!=")
        elif self.current() in {">"}:
            return self.match(">")
        elif self.current() in {">="}:
            return self.match(">=")
        else:
            self.error("syntax error", {"!=", "<", "<=", "==", ">", ">="})

    def _plus_min(self) -> Token:
        # plus_min -> "+" | "-"
        if self.current() in {"+"}:
            return self.match("+")
        elif self.current() in {"-"}:
            return self.match("-")
        else:
            self.error("syntax error", {"+", "-"})

    def _multi_div(self) -> Token:
        # multi_div -> "*" | "/"
        if self.current() in {"*"}:
            return self.match("*")
        elif self.current() in {"/"}:
            return self.match("/")
        else:
            self.error("syntax error", {"*", "/"})
