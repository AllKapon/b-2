import sys
import Lexer
import todot

class Parser:
    """A parser for the Jack programming language."""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.current_token = None
        self.advance()  # Load the first token

    def advance(self):
        """Advance to the next token."""
        self.current_token = self.lexer.next()

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.process('class')
        class_name = self.className()
        self.process('{')
        class_var_decs = []
        while self.current_token and self.current_token['token'] in ['static', 'field']:
            class_var_decs.append(self.classVarDec())
        subroutine_decs = []
        while self.current_token and self.current_token['token'] in ['constructor', 'function', 'method']:
            subroutine_decs.append(self.subroutineDec())
        self.process('}')
        return {
            'type': 'class',
            'className': class_name,
            'classVarDecs': class_var_decs,
            'subroutineDecs': subroutine_decs
        }

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        kind = self.current_token['token']
        self.advance()  # Move to the type
        var_type = self.type()
        var_names = [self.varName()]
        while self.current_token and self.current_token['token'] == ',':
            self.process(',')
            var_names.append(self.varName())
        self.process(';')
        return {
            'type': 'classVarDec',
            'kind': kind,
            'varType': var_type,
            'varNames': var_names
        }

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        if self.current_token['token'] in ['int', 'char', 'boolean']:
            type_name = self.current_token['token']
            self.advance()
            return type_name
        else:
            return self.className()

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        subroutine_kind = self.current_token['token']
        self.advance()  # Move to return type
        return_type = self.type() if self.current_token['token'] != 'void' else 'void'
        self.advance()  # Move to subroutine name
        subroutine_name = self.subroutineName()
        self.process('(')
        parameters = self.parameterList()
        self.process(')')
        body = self.subroutineBody()
        return {
            'type': 'subroutineDec',
            'subroutineKind': subroutine_kind,
            'returnType': return_type,
            'subroutineName': subroutine_name,
            'parameters': parameters,
            'body': body
        }

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        parameters = []
        if self.current_token and self.current_token['token'] != ')':
            while True:
                param_type = self.type()
                param_name = self.varName()
                parameters.append({'type': param_type, 'name': param_name})
                if self.current_token['token'] != ',':
                    break
                self.process(',')
        return parameters

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.process('{')
        var_decs = []
        while self.current_token and self.current_token['token'] == 'var':
            var_decs.append(self.varDec())
        statements = self.statements()
        self.process('}')
        return {
            'type': 'subroutineBody',
            'varDecs': var_decs,
            'statements': statements
        }

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.process('var')
        var_type = self.type()
        var_names = [self.varName()]
        while self.current_token and self.current_token['token'] == ',':
            self.process(',')
            var_names.append(self.varName())
        self.process(';')
        return {
            'type': 'varDec',
            'varType': var_type,
            'varNames': var_names
        }

    def className(self):
        """
        className: identifier
        """
        name = self.varName()
        return name

    def subroutineName(self):
        if self.current_token['type'] == 'identifier':
            name = self.current_token
            self.advance()  # Move to the next token
            return name
        raise SyntaxError("Expected a subroutine name")

    def varName(self):
        """
        varName: identifier
        """
        token = self.current_token
        self.process(token['token'])  # Consume the varName token
        return token['token']

    def statements(self):
        """
        statements : statement*
        """
        statement_list = []
        while self.current_token and self.current_token['token'] in ['let', 'if', 'while', 'do', 'return']:
            statement_list.append(self.statement())
        return statement_list

    def statement(self):
        """
        statement : letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        if self.current_token['token'] == 'let':
            return self.letStatement()
        elif self.current_token['token'] == 'if':
            return self.ifStatement()
        elif self.current_token['token'] == 'while':
            return self.whileStatement()
        elif self.current_token['token'] == 'do':
            return self.doStatement()
        elif self.current_token['token'] == 'return':
            return self.returnStatement()
        else:
            self.error(self.current_token)

    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.process('let')
        var_name = self.varName()
        expr = None
        if self.current_token['token'] == '[':
            self.process('[')
            expr = self.expression()
            self.process(']')
        self.process('=')
        value_expr = self.expression()
        self.process(';')
        return {
            'type': 'letStatement',
            'varName': var_name,
            'indexExpr': expr,
            'valueExpr': value_expr
        }

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.process('if')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        then_statements = self.statements()
        self.process('}')
        else_statements = None
        if self.current_token and self.current_token['token'] == 'else':
            self.process('else')
            self.process('{')
            else_statements = self.statements()
            self.process('}')
        return {
            'type': 'ifStatement',
            'condition': condition,
            'thenStatements': then_statements,
            'elseStatements': else_statements
        }

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        self.process('while')
        self.process('(')
        condition = self.expression()
        self.process(')')
        self.process('{')
        body_statements = self.statements()
        self.process('}')
        return {
            'type': 'whileStatement',
            'condition': condition,
            'bodyStatements': body_statements
        }

    def doStatement(self):
        # Process 'do' keyword
        self.process('do')  # Consume 'do'

        # Process the identifier (class or object name)
        if self.current_token['type'] != 'identifier':
            raise SyntaxError(f"Expected identifier after 'do', found {self.current_token['token']}")
        identifier = self.current_token['token']  # Store the identifier (e.g., 'Output')
        self.advance()  # Move to the next token

        # Process '.' symbol
        if self.current_token['token'] != '.':
            raise SyntaxError(f"Expected '.' after identifier, found {self.current_token['token']}")
        self.advance()  # Consume '.'

        # Process the method name (another identifier)
        if self.current_token['type'] != 'identifier':
            raise SyntaxError(f"Expected method name after '.', found {self.current_token['token']}")
        method_name = self.current_token['token']  # Store the method name (e.g., 'printString')
        self.advance()  # Move to the next token

        # Process '(' symbol
        if self.current_token['token'] != '(':
            raise SyntaxError(f"Expected '(' after method name, found {self.current_token['token']}")
        self.advance()  # Consume '('

        # Process the argument list (or none)
        args = self.expressionList()  # Parse the argument list

        # Process ')' symbol
        if self.current_token['token'] != ')':
            raise SyntaxError(f"Expected ')' after arguments, found {self.current_token['token']}")
        self.advance()  # Consume ')'

        # Process ';' symbol
        if self.current_token['token'] != ';':
            raise SyntaxError(f"Expected ';' at the end of 'do' statement, found {self.current_token['token']}")
        self.advance()  # Consume ';'

        print(f"Current token: {self.current_token}, Expected: identifier")

        # Return the parsed 'do' statement as a dictionary or AST node
        return {
            'type': 'doStatement',
            'object': identifier,
            'method': method_name,
            'arguments': args
        }

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.process('return')
        expr = None
        if self.current_token and self.current_token['token'] != ';':
            expr = self.expression()
        self.process(';')
        return {
            'type': 'returnStatement',
            'expression': expr
        }

    def expression(self):
        """
        expression : term (op term)*
        """
        terms = [self.term()]
        while True:
            print(f"Current token in expression: {self.current_token}")  # Debugging output
            operator = self.op()  # Get the operator
            if operator is None:
                break  # Exit loop if no valid operator found
            print(f"Operator found: {operator}")  # Debugging output
            terms.append({'op': operator, 'term': self.term()})
        return {
            'type': 'expression',
            'terms': terms
        }

    def term(self):
        """
        term : integerConstant | stringConstant | keywordConstant
              | varName | varName '[' expression ']' | subroutineCall
              | '(' expression ')' | unaryOp term
        """
        token = self.current_token
        if token['type'] == 'IntegerConstant':
            self.advance()
            return {'type': 'integerConstant', 'value': token['token']}
        elif token['type'] == 'StringConstant':
            self.advance()
            return {'type': 'stringConstant', 'value': token['token']}
        elif token['token'] in ['true', 'false', 'null', 'this']:
            self.advance()
            return {'type': 'keywordConstant', 'value': token['token']}
        elif token['type'] == 'identifier':
            var_name = self.varName()
            if self.current_token and self.current_token['token'] == '[':
                self.process('[')
                index_expr = self.expression()
                self.process(']')
                return {
                    'type': 'arrayAccess',
                    'varName': var_name,
                    'indexExpr': index_expr
                }
            elif self.current_token and self.current_token['token'] == '(':
                return self.subroutineCall()  # Handle subroutine call.
            return {'type': 'varName', 'name': var_name}
        elif token['token'] == '(':
            self.process('(')
            expr = self.expression()
            self.process(')')
            return expr
        elif token['token'] in ['-', '~']:
            unary_operator = self.current_token['token']
            self.advance()
            return {
                'type': 'unaryExpression',
                'op': unary_operator,
                'term': self.term()
            }
        else:
            self.error(token)

    def subroutineCall(self):
        """
        subroutineCall : subroutineName '(' expressionList ')'
                       | (className | varName) '.' subroutineName '(' expressionList ')'
        """
        if self.current_token['type'] == 'identifier':
            subroutine_name = self.subroutineName()
            self.process('(')
            expression_list = self.expressionList()
            self.process(')')
            return {'type': 'subroutineCall', 'name': subroutine_name, 'args': expression_list}
        elif self.current_token['token'] in ['varName', 'className']:
            class_or_var = self.className()  # Using varName or className
            self.process('.')
            subroutine_name = self.subroutineName()
            self.process('(')
            expression_list = self.expressionList()
            self.process(')')
            return {'type': 'subroutineCall', 'classOrVar': class_or_var, 'name': subroutine_name,
                    'args': expression_list}
        else:
            self.error(self.current_token)

    def expressionList(self):
        args = []

        # Check if there are any arguments (if the next token is not ')')
        if self.current_token['token'] != ')':
            args.append(self.expression())  # Parse the first expression

            # Parse additional arguments (comma-separated)
            while self.current_token['token'] == ',':
                self.advance()  # Consume ','
                args.append(self.expression())  # Parse the next expression

        return args

    def op(self):
        """
        op : '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
        """
        valid_operators = {
            '+': 'plus',
            '-': 'minus',
            '*': 'star',
            '/': 'slash',
            '&': 'ampersand',
            '|': 'pipe',
            '<': 'lt',
            '>': 'gt',
            '=': 'eq'
        }
        token_value = self.current_token['token']
        if token_value in valid_operators:
            self.advance()  # Consume the token
            return valid_operators[token_value]
        return None

    def unaryOp(self):
        """
        unaryOp : '-' | '~'
        """
        return self.current_token['token']

    def KeywordConstant(self):
        """
        KeyWordConstant : 'true' | 'false' | 'null' | 'this'
        """
        if self.current_token['token'] in ['true', 'false', 'null', 'this']:
            value = self.current_token['token']
            self.advance()
            return value
        else:
            self.error(self.current_token)

    def process(self, expected_token):
        """Check for the expected token and advance. Raise an error if not found."""
        if self.current_token['token'] == expected_token:
            self.advance()
        else:
            self.error(self.current_token)

    def error(self, token):
        """Handle parsing errors."""
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
