"""No comment"""
import sys
import Parser


class Generator:
    """No comment"""

    def __init__(self, file=None):
        if file is not None:
            self.parser = Parser.Parser(file)
            self.arbre = self.parser.jackclass()
            self.vmfile = open(self.arbre['name'] + '.vm', "w")
            self.symbolClassTable = []
            self.symbolRoutineTable = []

    def jackclass(self, arbre):
        """
            {'line': line, 'col': col, 'type': 'class', 'name': className,
            'varDec': [variable], 'subrout ine':[subroutine]}
        """

    def variable(self, var):
        """
        {'line': line, 'col': col, 'name': varName, 'kind': kind, 'type': type}
        """

    def subroutineDec(self, routine):
        """
        {'line':line, 'col': col,'type': 'constructor'|'function'|'method',
            'return' : 'void| 'int'|'char'|'boolean'|className',
            'name': subroutineName, 'argument': [variable],'local': [variable],
            'instructions' : [instruction]
        """

    def statement(self, inst):
        """
        statement : letStatements|ifStatement|whileStatement|doStatement|returnStatement
        """

    def letStatement(self, inst):
        """
        {'line':line, 'col': col,'type': 'let',
        'variable': varName, 'indice': expression, 'valeur': expression
        """

    def ifStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'if', 'condition': expression, 'true': [instruction],
        'false': [instruction]}
        """

    def whileStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'while', 'condition': expression,
        'instructions': [instruction]}
        """

    def doStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'do', 'classvar': className ou varName,
        'name': subroutineName, 'argument': [expression]}
        """

    def returnStatement(self, inst):
        """
        {'line':line, 'col': col, 'type': 'return', 'valeur': expression}
        """

    def expression(self, exp):
        """
        [term op ...]
            avec op : '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        """

    def term(self, t):
        """
        {'line':line, 'col': col,
        'type': 'int'| 'string'| 'constant'| 'varName'|'call'| 'expression'|'-'|'~',
         'indice':expression, 'subroutineCall': subroutineCall}
        """

    def subroutineCall(self, call):
        """
        {'line':line, 'col': col, 'classvar': className ou varName,
        'name': subroutineName, 'argument': [expression]}
        """

    def error(self, message=''):
        print(f"SyntaxError: {message}")
        exit()


if __name__ == '__main__':
    file = sys.argv[1]
    print('-----debut')
    generator = Generator(file)
    generator.jackclass()
    print('-----fin')
