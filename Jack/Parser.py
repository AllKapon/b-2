import sys
import Lexer
import todot


class Parser:
    """A parser for the Jack programming language."""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)


    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.process('class')
        class_name = self.className()
        self.process('{')
        class_vars = []
        while self.lookahead('static', 'field'):
            class_vars.append(self.classVarDec())
        subroutines = []
        while self.lookahead('constructor', 'function', 'method'):
            subroutines.append(self.subroutineDec())
        self.process('}')
        return {'type': 'class', 'name': class_name, 'classVarDec': class_vars, 'subroutineDec': subroutines}

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        var_kind = self.lexer.next()['token']
        var_type = self.type()
        vars = [self.varName()]
        while self.lookahead(','):
            self.process(',')
            vars.append(self.varName())
        self.process(';')
        return {'type': 'classVarDec', 'kind': var_kind, 'varType': var_type, 'vars': vars}

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        if self.lookahead('int', 'char', 'boolean'):
            return self.lexer.next()['token']
        return self.className()

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        subroutine_type = self.lexer.next()['token']
        return_type = self.lexer.next()['token'] if self.lookahead('void') else self.type()
        name = self.subroutineName()
        self.process('(')
        params = self.parameterList()
        self.process(')')
        body = self.subroutineBody()
        return {'type': 'subroutineDec', 'subroutineType': subroutine_type, 'returnType': return_type, 'name': name, 'parameters': params, 'body': body}

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        params = []
        if not self.lookahead(')'):
            param_type = self.type()
            param_name = self.varName()
            params.append({'type': param_type, 'name': param_name})
            while self.lookahead(','):
                self.process(',')
                param_type = self.type()
                param_name = self.varName()
                params.append({'type': param_type, 'name': param_name})
        return params

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.process('{')
        vars = []
        while self.lookahead('var'):
            vars.append(self.varDec())
        statements = self.statements()
        self.process('}')
        return {'type': 'subroutineBody', 'vars': vars, 'statements': statements}

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.process('var')
        var_type = self.type()
        vars = [self.varName()]
        while self.lookahead(','):
            self.process(',')
            vars.append(self.varName())
        self.process(';')
        return {'type': 'varDec', 'varType': var_type, 'vars': vars}


    def className(self):
        """
        className: identifier
        """
        return self.processIdentifier()

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        return self.processIdentifier()

    def varName(self):
        """
        varName: identifier
        """
        return self.processIdentifier()

    def statements(self):
        """
        statements : statement*
        """
        stmts = []
        while self.lookahead('let', 'if', 'while', 'do', 'return'):
            stmts.append(self.statement())
        return stmts

    def statement(self):
        """
        statement : letStatement|ifStatement|whileStatement|doStatement|returnStatement
        """
        if self.lookahead('let'):
            return self.letStatement()
        elif self.lookahead('if'):
            return self.ifStatement()
        elif self.lookahead('while'):
            return self.whileStatement()
        elif self.lookahead('do'):
            return self.doStatement()
        elif self.lookahead('return'):
            return self.returnStatement()
        else:
            self.error(self.lexer.look())

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.process('let')
        name = self.varName()
        print(f"Parsed variable name: {name}")  # Debugging line
        index = None
        if self.lookahead('['):
            self.process('[')
            index = self.expression()
            self.process(']')
        self.process('=')
        value = self.expression()
        print(f"Parsed expression value: {value}")  # Debugging line
        self.process(';')
        return {'type': 'letStatement', 'name': name, 'index': index, 'value': value}

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.process('if')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        if_statements = self.statements()
        self.process('}')
        else_statements = None
        if self.lookahead('else'):
            self.process('else')
            self.process('{')
            else_statements = self.statements()
            self.process('}')
        return {'type': 'ifStatement', 'condition': condition, 'ifStatements': if_statements,
                'elseStatements': else_statements}

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        self.process('while')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        body = self.statements()
        self.process('}')
        return {'type': 'whileStatement', 'condition': condition, 'body': body}

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        self.process('do')
        print(f"Expecting subroutine call after 'do'")
        call = self.subroutineCall()
        self.process(';')
        return {'type': 'doStatement', 'call': call}

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.process('return')
        expr = None
        if not self.lookahead(';'):
            expr = self.expression()
        self.process(';')
        return {'type': 'returnStatement', 'expression': expr}

    def expression(self):
        """
        Parses an expression.
        expression: term (op term)*
        """
        expr = {'type': 'expression', 'terms': []}

        # Parse the first term
        expr['terms'].append(self.term())

        # Parse (op term)* - handle additional terms
        while self.lookahead('+', '-', '*', '/', '&', '|', '<', '>', '='):  # Check for operator
            op = self.processOperator()
            term = self.term()  # Parse the next term
            expr['terms'].append({'op': op})
            expr['terms'].append(term)

        return expr

    def term(self):
        """
        term : integerConstant|stringConstant|keywordConstant
              |varName|varName '[' expression ']'|subroutineCall
              | '(' expression ')' | unaryOp term
        """
        token = self.lexer.look()

        if token['type'] == 'IntegerConstant':
            return {'type': 'term', 'subType': 'integerConstant', 'value': self.lexer.next()['token']}
        elif self.lookahead('('):  # Handle grouped expressions
            self.process('(')
            expr = self.expression()  # Parse the inner expression
            self.process(')')  # Consume closing parenthesis
            return {'type': 'term', 'subType': 'expression', 'value': expr}
        elif self.lookahead('-', '~'):  # Unary operation
            op = self.unaryOp()
            term = self.term()
            return {'type': 'term', 'subType': 'unaryOp', 'op': op, 'term': term}
        elif self.lookahead('true', 'false', 'null', 'this'):  # Keyword constants
            return {'type': 'term', 'subType': 'keywordConstant', 'value': self.KeywordConstant()}
        elif token['type'] == 'identifier':  # Check for identifiers
            var_name = self.processIdentifier()  # Consume the identifier
            if self.lookahead('['):  # Array access: varName[expression]
                self.process('[')
                index = self.expression()
                self.process(']')
                return {'type': 'term', 'subType': 'arrayAccess', 'name': var_name, 'index': index}
            elif self.lookahead('(') or self.lookahead('.'):  # Subroutine call
                return self.subroutineCall()
            else:  # Standalone variable
                return {'type': 'term', 'subType': 'varName', 'name': var_name}
        elif self.lookahead('\"'):  # String constants
            return {'type': 'term', 'subType': 'stringConstant', 'value': self.lexer.next()['token']}
        else:
            self.error(token)

    def subroutineCall(self):
        """
        Handles a subroutine call, which can be in the form:
        1. subroutineName(expressionList)
        2. objectName.subroutineName(expressionList)
        """
        identifier = self.processIdentifier()  # Process the first identifier (object or subroutine name)

        if self.lookahead() and self.lookahead()['type'] == 'symbol' and self.lookahead()['token'] == '.':
            # Method or object call (e.g., Keyboard.readInt())
            self.process('.')  # Consume the '.'

            if self.lookahead()['type'] != 'identifier':
                raise SyntaxError(f"Expected method name after '.', but got {self.lookahead()}")

            subroutine_name = self.processIdentifier()  # Handle the method name
            self.process('(')  # Process the opening '('
            args = self.expressionList()  # Parse the expression list (arguments)
            self.process(')')  # Process the closing ')'

            return {
                'type': 'subroutineCall',
                'object': identifier,  # The object or class (e.g., 'Keyboard')
                'name': subroutine_name,  # The method name (e.g., 'readInt')
                'args': args,  # Parsed argument list
            }

        elif self.lookahead() and self.lookahead()['type'] == 'symbol' and self.lookahead()['token'] == '(':
            # Subroutine call without an object (e.g., doSomething())
            self.process('(')  # Process the opening '('
            args = self.expressionList()  # Parse the expression list (arguments)
            self.process(')')  # Process the closing ')'

            return {
                'type': 'subroutineCall',
                'name': identifier,  # Subroutine name (e.g., 'main')
                'args': args,  # Parsed argument list
            }

        else:
            raise SyntaxError(f"Invalid subroutine call syntax: {identifier}")

    def lookahead_identifier(self):
        """
        Checks if the next token is an identifier.
        Returns:
            bool: True if the next token's type is 'identifier', otherwise False.
        """
        next_token = self.lookahead()  # Peek at the next token without consuming it
        return next_token and next_token.get('type') == 'identifier'

    def lookahead_keyword(self, expected_keyword):
        """
        Checks if the next token is a specific keyword.
        Args:
            expected_keyword (str): The keyword to check for.
        Returns:
            bool: True if the next token matches the keyword, otherwise False.
        """
        next_token = self.lookahead()
        return next_token and next_token.get('type') == 'keyword' and next_token.get('token') == expected_keyword

    def lookahead_symbol(self, expected_symbol):
        """
        Checks if the next token is a specific symbol.
        Args:
            expected_symbol (str): The symbol to check for (e.g., '(' or ')').
        Returns:
            bool: True if the next token matches the symbol, otherwise False.
        """
        next_token = self.lookahead()
        return next_token and next_token.get('type') == 'symbol' and next_token.get('token') == expected_symbol

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        expressions = []
        if not self.lookahead(')'):
            expressions.append(self.expression())
            while self.lookahead(','):
                self.process(',')
                expressions.append(self.expression())
        return expressions


    def op(self):
        """
        op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """
        return self.process(self.lexer.next()['token'])

    def unaryOp(self):
        """
        unaryop : '-'|'~'
        """
        return self.process(self.lexer.next()['token'])

    def KeywordConstant(self):
        """
        KeyWordConstant : 'true'|'false'|'null'|'this'
        """
        return self.process(self.lexer.next()['token'])

    def process(self, expected):
        token = self.lexer.next()
        if token is not None and token['token'] == expected:
            return token['token']
        else:
            self.error(token)

    def processOperator(self):
        """
        Consumes an operator token and returns its value.
        Valid operators: +, -, *, /, &, |, <, >, =
        """
        token = self.lexer.look()  # Peek at the current token
        if token['token'] in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
            return self.lexer.next()['token']  # Consume and return the operator
        else:
            self.error(f"Unexpected token: {token}, expected an operator.")

    def processIdentifier(self):
        token = self.lexer.next()
        if token is not None and token['type'] == 'identifier':
            return token['token']
        else:
            self.error(token)

    def lookahead(self, *expected):
        """
        Checks if the next token matches one of the expected tokens.
        Supports both token and type matching.
        Expected can include:
        - Strings (token values)
        - Tuples (type, token value)
        """
        token = self.lexer.look()
        if token is None:
            print(f"Lookahead failed: No token available, expected {expected}")
            return False

        for exp in expected:
            if isinstance(exp, tuple):  # Match (type, value)
                if token['type'] == exp[0] and token['token'] == exp[1]:
                    print(f"Lookahead matched: {token} (expected {exp})")
                    return True
            elif token['token'] == exp:  # Match token value
                print(f"Lookahead matched: {token['token']} (expected {exp})")
                return True

        print(f"Lookahead failed: {token} not in {expected}")
        return False

    def error(self, token):
        if token is None:
            print("Syntax error: end of file")
        else:
            print(f"SyntaxError (line={token['line']}, col={token['col']}): {token['token']}")
        exit()


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    parser = Parser(file)
    arbre = parser.jackclass()
    todot = todot.Todot(file)
    todot.todot(arbre)
    print('-----fin')
