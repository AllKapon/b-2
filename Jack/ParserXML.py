import sys
import Lexer


class ParserXML:
    """Parser for Jack programming language to produce an XML representation"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.xml = open(file[0:-5] + ".xml", "w")
        self.xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.token = None  # For storing the current token from the lexer
        self.advance()  # Initialize the first token

    def advance(self):
        """Advances to the next token."""
        self.token = self.lexer.next()

    def jackclass(self):
        self.xml.write(f"<class>\n")
        self.process('class')  # 'class'
        self.className()  # className
        self.process('{')  # '{'

        while self.token and self.token['token'] in ['static', 'field']:
            self.classVarDec()  # classVarDec*

        while self.token and self.token['token'] in ['constructor', 'function', 'method']:
            self.subroutineDec()  # subroutineDec*

        self.process('}')  # '}'
        self.xml.write(f"</class>\n")

    def classVarDec(self):
        self.xml.write(f"<classVarDec>\n")
        kind = self.token['token']  # 'static' or 'field'
        self.process(kind)
        self.type()  # type
        self.varName()  # varName

        while self.token and self.token['token'] == ',':
            self.process(',')
            self.varName()  # varName

        self.process(';')  # ';'
        self.xml.write(f"</classVarDec>\n")

    def type(self):
        """ Handles types in Jack"""
        self.xml.write(f"<type>\n")
        if self.token['token'] in ['int', 'char', 'boolean']:
            self.process(self.token['token'])  # 'int', 'char', 'boolean'
        else:
            self.className()  # className
        self.xml.write(f"</type>\n")

    def subroutineDec(self):
        self.xml.write(f"<subroutineDec>\n")
        kind = self.token['token']  # 'constructor', 'function', 'method'
        self.process(kind)
        if self.token['token'] in ['void']:
            self.process('void')  # 'void'
        else:
            self.type()  # type

        self.subroutineName()  # subroutineName
        self.process('(')  # '('
        self.parameterList()  # parameterList
        self.process(')')  # ')'
        self.subroutineBody()  # subroutineBody
        self.xml.write(f"</subroutineDec>\n")

    def parameterList(self):
        self.xml.write(f"<parameterList>\n")
        if self.token and self.token['token'] in ['int', 'char', 'boolean']:
            self.type()  # type
            self.varName()  # varName
            while self.token and self.token['token'] == ',':
                self.process(',')
                self.type()  # type
                self.varName()  # varName
        self.xml.write(f"</parameterList>\n")

    def subroutineBody(self):
        self.xml.write(f"<subroutineBody>\n")
        self.process('{')  # '{'
        while self.token and self.token['token'] == 'var':
            self.varDec()  # varDec*
        self.statements()  # statements
        self.process('}')  # '}'
        self.xml.write(f"</subroutineBody>\n")

    def varDec(self):
        self.xml.write(f"<varDec>\n")
        self.process('var')  # 'var'
        self.type()  # type
        self.varName()  # varName

        while self.token and self.token['token'] == ',':
            self.process(',')
            self.varName()  # varName
        self.process(';')  # ';'
        self.xml.write(f"</varDec>\n")

    def className(self):
        self.xml.write(f"<className>")
        self.process(self.token['token'])  # identifier
        self.xml.write(f"</className>\n")

    def subroutineName(self):
        self.xml.write(f"<subroutineName>")
        self.process(self.token['token'])  # identifier
        self.xml.write(f"</subroutineName>\n")

    def varName(self):
        self.xml.write(f"<varName>")
        self.process(self.token['token'])  # identifier
        self.xml.write(f"</varName>\n")

    def statements(self):
        self.xml.write(f"<statements>\n")
        while self.token and self.token['token'] in ['let', 'if', 'while', 'do', 'return']:
            self.statement()  # statement*
        self.xml.write(f"</statements>\n")

    def statement(self):
        self.xml.write(f"<statement>\n")
        if self.token['token'] == 'let':
            self.letStatement()  # letStatement
        elif self.token['token'] == 'if':
            self.ifStatement()  # ifStatement
        elif self.token['token'] == 'while':
            self.whileStatement()  # whileStatement
        elif self.token['token'] == 'do':
            self.doStatement()  # doStatement
        elif self.token['token'] == 'return':
            self.returnStatement()  # returnStatement
        self.xml.write(f"</statement>\n")

    def letStatement(self):
        self.xml.write(f"<letStatement>\n")
        self.process('let')  # 'let'
        self.varName()  # varName

        if self.token and self.token['token'] == '[':
            self.process('[')  # '['
            self.expression()  # expression
            self.process(']')  # ']'

        self.process('=')  # '='
        self.expression()  # expression
        self.process(';')  # ';'
        self.xml.write(f"</letStatement>\n")

    def ifStatement(self):
        self.xml.write(f"<ifStatement>\n")
        self.process('if')  # 'if'
        self.process('(')  # '('
        self.expression()  # expression
        self.process(')')  # ')'
        self.process('{')  # '{'
        self.statements()  # statements
        self.process('}')  # '}'

        if self.token and self.token['token'] == 'else':
            self.process('else')  # 'else'
            self.process('{')  # '{'
            self.statements()  # statements
            self.process('}')  # '}'

        self.xml.write(f"</ifStatement>\n")

    def whileStatement(self):
        self.xml.write(f"<whileStatement>\n")
        self.process('while')  # 'while'
        self.process('(')  # '('
        self.expression()  # expression
        self.process(')')  # ')'
        self.process('{')  # '{'
        self.statements()  # statements
        self.process('}')  # '}'
        self.xml.write(f"</whileStatement>\n")

    def doStatement(self):
        self.xml.write(f"<doStatement>\n")
        self.process('do')  # 'do'
        self.subroutineCall()  # subroutineCall
        self.process(';')  # ';'
        self.xml.write(f"</doStatement>\n")

    def returnStatement(self):
        self.xml.write(f"<returnStatement>\n")
        self.process('return')  # 'return'
        if self.token and self.token['token'] != ';':
            self.expression()  # expression
        self.process(';')  # ';'
        self.xml.write(f"</returnStatement>\n")

    def expression(self):
        self.xml.write(f"<expression>\n")
        self.term()  # term
        while self.token and self.token['token'] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.op()  # op
            self.term()  # term
        self.xml.write(f"</expression>\n")

    def term(self):
        self.xml.write(f"<term>\n")
        if self.token['type'] == 'IntegerConstant':
            self.process(self.token['token'])  # integerConstant
        elif self.token['type'] == 'StringConstant':
            self.process(self.token['token'])  # stringConstant
        elif self.token['token'] in ['true', 'false', 'null', 'this']:
            self.KeywordConstant()  # keywordConstant
        elif self.token['type'] == 'identifier':
            self.varName()  # varName
            if self.token and self.token['token'] == '[':
                self.process('[')
                self.expression()  # expression
                self.process(']')
            elif self.token and self.token['token'] == '.':
                self.subroutineCall()  # subroutineCall
        elif self.token and self.token['token'] == '(':
            self.process('(')
            self.expression()  # expression
            self.process(')')
        elif self.token['token'] in ['-', '~']:
            self.unaryOp()  # unaryOp
            self.term()  # term
        self.xml.write(f"</term>\n")

    def subroutineCall(self):
        self.xml.write(f"<subroutineCall>\n")

        self.process(self.token['token'])  # objectName or subroutineName
        if self.token and self.token['token'] == '.':
            self.process('.')  # Consume the '.'
            if self.token and self.token['type'] == 'identifier':  # This ensures a method name exists
                self.process(self.token['token'])  # Read subroutineName
            else:
                self.error(self.token)  # This ensures we display the error if no method is detected
        self.process('(')  # Consume '('
        self.expressionList()  # Process the arguments
        self.process(')')  # Consume ')'

        self.xml.write(f"</subroutineCall>\n")

    def expressionList(self):
        self.xml.write(f"<expressionList>\n")
        if self.token and self.token['type'] in ['IntegerConstant', 'StringConstant', 'identifier', 'keyword']:
            self.expression()  # expression
            while self.token and self.token['token'] == ',':
                self.process(',')
                self.expression()  # expression
        self.xml.write(f"</expressionList>\n")

    def op(self):
        self.xml.write(f"<op>\n")
        self.process(self.token['token'])  # op
        self.xml.write(f"</op>\n")

    def unaryOp(self):
        self.xml.write(f"<unaryOp>\n")
        self.process(self.token['token'])  # unaryOp
        self.xml.write(f"</unaryOp>\n")

    def KeywordConstant(self):
        self.xml.write(f"<keyWordConstant>\n")
        self.process(self.token['token'])  # keyword constant (true | false | null | this)
        self.xml.write(f"</keyWordConstant>\n")

    def process(self, str):
        token = self.token
        print(f"Processing token: {token}")  # Ajoutez cette ligne pour déboguer
        if token is not None and token['token'] == str:
            self.xml.write(f"<{token['type']}>{token['token']}</{token['type']}>\n")
            self.advance()  # Move to the next token
        else:
            self.error(token)

    def error(self, token):
        if token is None:
            print("Syntax error: end of file")
        else:
            print(f"SyntaxError (line={token['line']}, col={token['col']}): {token['token']}")
        exit()


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    parser = ParserXML(file)
    parser.jackclass()
    print('-----fin')