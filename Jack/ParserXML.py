import sys
import re
import Lexer




class ParserXML:
    """No comment"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.xml = open(file[0:-5] + ".xml", "w")
        self.xml.write('<?xml version="1.0" encoding="UTF-8"?>')

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.xml.write(f"""<class>\n""")
        self.process('class')
        self.className()
        self.process('{')
        while self.lexer.look()['token'] in ['static', 'field']:
            self.classVarDec()
        while self.lexer.look()['token'] in ['constructor', 'function', 'method']:
            self.subroutineDec()
        self.process('}')
        self.process('}')
        self.xml.write(f"""</class>\n""")

    def classVarDec(self):
        """
        classVarDec: ('static'| 'field') type varName (',' varName)* ';'
        """
        self.xml.write(f"""<classVarDec>\n""")
        self.process(self.lexer.next()['token'])  # 'static' or 'field'
        self.type()
        self.varName()
        while self.lexer.look()['token'] == ',':
            self.process(',')
            self.varName()
        self.process(';')
        self.xml.write(f"""</classVarDec>\n""")

    def type(self):
        """
        type: 'int'|'char'|'boolean'|className
        """
        self.xml.write(f"""<type>\n""")
        token = self.lexer.look()['token']
        if token in ['int', 'char', 'boolean'] or self.isIdentifier(token):
            self.process(token)
        else:
            self.error(None)
        self.xml.write(f"""</type>\n""")

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'| 'function'|'method') ('void'|type)
        subroutineName '(' parameterList ')' subroutineBody
        """
        self.xml.write(f"""<subroutineDec>\n""")
        self.process(self.lexer.next()['token'])  # 'constructor', 'function', or 'method'
        token = self.lexer.look()['token']
        if token == 'void' or token in ['int', 'char', 'boolean'] or self.isIdentifier(token):
            self.process(token)
        self.subroutineName()
        self.process('(')
        self.parameterList()
        self.process(')')
        self.subroutineBody()
        self.xml.write(f"""</subroutineDec>\n""")

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        self.xml.write(f"""<parameterList>\n""")
        if self.lexer.look()['token'] in ['int', 'char', 'boolean'] or self.isIdentifier(self.lexer.look()['token']):
            self.type()
            self.varName()
            while self.lexer.look()['token'] == ',':
                self.process(',')
                self.type()
                self.varName()
        self.xml.write(f"""</parameterList>\n""")

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        self.xml.write(f"""<subroutineBody>\n""")
        self.process('{')
        while self.lexer.look()['token'] == 'var':
            self.varDec()
        self.statements()
        self.process('}')
        self.xml.write(f"""</subroutineBody>\n""")

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.xml.write(f"""<varDec>\n""")
        self.process('var')
        self.type()
        self.varName()
        while self.lexer.look()['token'] == ',':
            self.process(',')
            self.varName()
        self.process(';')
        self.xml.write(f"""</varDec>\n""")

    def className(self):
        """
        className: identifier
        """
        self.xml.write(f"""<className>""")
        token = self.lexer.look()['token']
        if self.isIdentifier(token):
            self.process(token)  # This will process and write the class name to XML
        else:
            self.error(None)
        self.xml.write(f"""</className>""")

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        self.xml.write(f"""<subroutineName>""")
        token = self.lexer.look()['token']
        if self.isIdentifier(token):
            self.process(token)  # This will process and write the subroutine name to XML
        else:
            self.error(None)
        self.xml.write(f"""</subroutineName>""")

    def varName(self):
        """
        varName: identifier
        """
        self.xml.write(f"""<varName>""")
        token = self.lexer.look()['token']
        if self.isIdentifier(token):
            self.process(token)  # This will process and write the variable name to XML
        else:
            self.error(None)
        self.xml.write(f"""</varName>""")

    def statements(self):
        """
        statements : statements*
        """
        self.xml.write("<statements>\n")
        while self.lexer.look()['token'] in ['let', 'if', 'while', 'do', 'return']:
            if self.lexer.look()['token'] == 'let':
                self.letStatement()
            elif self.lexer.look()['token'] == 'if':
                self.ifStatement()
            elif self.lexer.look()['token'] == 'while':
                self.whileStatement()
            elif self.lexer.look()['token'] == 'do':
                self.doStatement()
            elif self.lexer.look()['token'] == 'return':
                self.returnStatement()
        self.xml.write("</statements>\n")


    def letStatement(self):
        """
        letStatement : 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.xml.write("<letStatement>\n")
        self.process('let')
        self.varName()
        if self.lexer.look()['token'] == '[':
            self.process('[')
            self.expression()
            self.process(']')
        self.process('=')
        self.expression()
        self.process(';')
        self.xml.write("</letStatement>\n")

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self.xml.write("<ifStatement>\n")
        self.process('if')
        self.process('(')
        self.expression()
        self.process(')')
        self.process('{')
        self.statements()
        self.process('}')
        if self.lexer.look()['token'] == 'else':
            self.process('else')
            self.process('{')
            self.statements()
            self.process('}')
        self.xml.write("</ifStatement>\n")

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        self.xml.write("<whileStatement>\n")
        self.process('while')
        self.process('(')
        self.expression()
        self.process(')')
        self.process('{')
        self.statements()
        self.process('}')
        self.xml.write("</whileStatement>\n")

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        self.xml.write("<doStatement>\n")
        self.process('do')
        self.subroutineCall()
        self.process(';')
        self.xml.write("</doStatement>\n")

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        self.xml.write("<returnStatement>\n")
        self.process('return')
        if self.lexer.look()['token'] != ';':
            self.expression()
        self.process(';')
        self.xml.write("</returnStatement>\n")

    def isIdentifier(self, token):
        """Check if a token is a valid identifier."""
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token) is not None

    def expression(self):
        """
        expression : term (op term)*
        """
        self.xml.write("<expression>\n")
        self.term()
        while self.lexer.look()['token'] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.op()
            self.term()
        self.xml.write("</expression>\n")

    def term(self):
        """
        term : integerConstant|stringConstant|keywordConstant
                |varName|varName '[' expression ']'|subroutineCall
                | '(' expression ')' | unaryOp term
        """
        self.xml.write("<term>\n")
        token = self.lexer.look()
        if token['type'] == 'identifier':
            self.process(token['token'])
            if self.lexer.look()['token'] == '[':
                self.process('[')
                self.expression()
                self.process(']')
            elif self.lexer.look()['token'] == '(':
                self.process('(')
                self.expressionList()
                self.process(')')
            elif self.lexer.look()['token'] == '.':
                self.process('.')
                self.subroutineName()
                self.process('(')
                self.expressionList()
                self.process(')')
        elif token['type'] in ['IntegerConstant', 'StringConstant', 'keyword']:
            self.process(token['token'])
        elif token['token'] == '(':
            self.process('(')
            self.expression()
            self.process(')')
        elif token['token'] in ['-', '~']:
            self.process(token['token'])
            self.term()
        else:
            self.error(token)
        self.xml.write("</term>\n")

    def subroutineCall(self):
        """
        subroutineCall : subroutineName '(' expressionList ')'
                | (className|varName) '.' subroutineName '(' expressionList ')'
        Attention : l'analyse syntaxique ne peut pas distingué className et varName.
            Nous utiliserons la balise <classvarName> pour (className|varName)
        """
        self.xml.write(f"""<subroutineCall>\n""")
        token = self.lexer.look()
        if self.lexer.look2()['token'] == '.':
            self.process(token['token'])
            self.process('.')
            self.subroutineName()
        else:
            self.subroutineName()
        self.process('(')
        self.expressionList()
        self.process(')')
        self.xml.write(f"""</subroutineCall>\n""")

    def expressionList(self):
        """
        expressionList : (expression (',' expression)*)?
        """
        self.xml.write("<expressionList>\n")
        if self.lexer.look()['token'] != ')':
            self.expression()
            while self.lexer.look()['token'] == ',':
                self.process(',')
                self.expression()
        self.xml.write("</expressionList>\n")

    def op(self):
        """
        op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """
        self.xml.write(f"""<op>""")
        token = self.lexer.look()['token']
        if token in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.process(token)  # This will process and write the operator to XML
        else:
            self.error(None)
        self.xml.write(f"""</op>""")

    def unaryOp(self):
        """
        unaryop : '-'|'~'
        """
        self.xml.write(f"""<unaryop>""")
        token = self.lexer.look()['token']
        if token in ['-', '~']:
            self.process(token)  # This will process and write the unary operator to XML
        else:
            self.error(None)
        self.xml.write(f"""</unaryop>""")

    def KeywordConstant(self):
        """
        KeyWordConstant : 'true'|'false'|'null'|'this'
        """
        self.xml.write(f"""<KeywordConstant>""")
        token = self.lexer.look()['token']
        if token in ['true', 'false', 'null', 'this']:
            self.process(token)  # This will process and write the keyword constant to XML
        else:
            self.error(None)
        self.xml.write(f"""</KeywordConstant>""")

    def process(self, str):
        token = self.lexer.next()
        if (token is not None and token['token'] == str):
            self.xml.write(f"""<{token['type']}>{token['token']}</{token['type']}>\n""")
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
