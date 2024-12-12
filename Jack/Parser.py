import sys
import re
import Lexer


class Parser:
    """Classe pour parser un programme Jack et générer un arbre syntaxique simplifié"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)  # Utilise le Lexer pour analyser le programme Jack

    def jackclass(self):
        """
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        tree = {"type": "class", "children": []}  # Arbre principal représentant la classe

        # Analyse de la déclaration de classe
        self.process('class')
        tree['className'] = self.className()
        self.process('{')

        # Ajoute les variables de classe (field, static)
        while self.lexer.look()['token'] in ['static', 'field']:
            tree['children'].append(self.classVarDec())

        # Ajoute les sous-routines (constructor, function, method)
        while self.lexer.look()['token'] in ['constructor', 'function', 'method']:
            tree['children'].append(self.subroutineDec())

        self.process('}')
        return tree

    def classVarDec(self):
        """
        classVarDec: ('static'|'field') type varName (',' varName)* ';'
        """
        var_dec = {"type": "classVarDec", "children": []}

        # Analyse 'static' ou 'field'
        var_dec['modifier'] = self.process(self.lexer.next()['token'])

        # Analyse du type
        var_dec['type'] = self.type()

        # Analyse du nom de variable
        var_dec['varName'] = self.varName()

        # Ajoute d'autres variables si nécessaire
        while self.lexer.look()['token'] == ',':
            self.process(',')
            var_dec['children'].append(self.varName())

        self.process(';')
        return var_dec

    def subroutineDec(self):
        """
        subroutineDec: ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody
        """
        subroutine = {"type": "subroutineDec", "children": []}

        # Analyse du type de sous-routine (constructor, function, method)
        subroutine['modifier'] = self.process(self.lexer.next()['token'])

        # Type de retour
        subroutine['returnType'] = self.process(self.lexer.look()['token'])

        # Nom de la sous-routine
        subroutine['subroutineName'] = self.subroutineName()

        # Paramètres de la sous-routine
        self.process('(')
        subroutine['parameters'] = self.parameterList()
        self.process(')')

        # Corps de la sous-routine
        subroutine['body'] = self.subroutineBody()

        return subroutine

    # Méthodes supplémentaires pour analyser d'autres éléments de la syntaxe du langage Jack
    def type(self):
        """
        type: 'int' | 'char' | 'boolean' | className
        """
        token = self.lexer.look()['token']
        if token in ['int', 'char', 'boolean'] or self.isIdentifier(token):
            return token
        else:
            self.error(None)

    def varName(self):
        """
        varName: identifier
        """
        token = self.lexer.look()['token']
        if self.isIdentifier(token):
            return token
        else:
            self.error(None)

    def subroutineName(self):
        """
        subroutineName: identifier
        """
        token = self.lexer.look()['token']
        if self.isIdentifier(token):
            return token
        else:
            self.error(None)

    def className(self):
        """
        className: identifier
        """
        token = self.lexer.look()['token']
        if self.isIdentifier(token):
            return token
        else:
            self.error(None)

    def parameterList(self):
        """
        parameterList: ((type varName) (',' type varName)*)?
        """
        parameters = []
        while self.lexer.look()['token'] in ['int', 'char', 'boolean'] or self.isIdentifier(self.lexer.look()['token']):
            param_type = self.type()
            param_name = self.varName()
            parameters.append({"type": param_type, "name": param_name})
            if self.lexer.look()['token'] == ',':
                self.process(',')
        return parameters

    def subroutineBody(self):
        """
        subroutineBody: '{' varDec* statements '}'
        """
        body = {"type": "subroutineBody", "children": []}
        self.process('{')

        while self.lexer.look()['token'] == 'var':
            body['children'].append(self.varDec())

        body['children'].extend(self.statements())
        self.process('}')
        return body

    def varDec(self):
        """
        varDec: 'var' type varName (',' varName)* ';'
        """
        var_dec = {"type": "varDec", "children": []}

        # Le mot-clé 'var'
        self.process('var')

        # Le type de la variable
        var_dec['type'] = self.type()

        # Le nom de la première variable
        var_dec['varName'] = self.varName()

        # Ajouter d'autres variables séparées par des virgules, si nécessaire
        while self.lexer.look()['token'] == ',':
            self.process(',')
            var_dec['children'].append(self.varName())

        # Le point-virgule final
        self.process(';')

        return var_dec

    def statements(self):
        """
        statements: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        statements = []
        while self.lexer.look()['token'] in ['let', 'if', 'while', 'do', 'return']:
            if self.lexer.look()['token'] == 'let':
                statements.append(self.letStatement())
            elif self.lexer.look()['token'] == 'if':
                statements.append(self.ifStatement())
            elif self.lexer.look()['token'] == 'while':
                statements.append(self.whileStatement())
            elif self.lexer.look()['token'] == 'do':
                statements.append(self.doStatement())
            elif self.lexer.look()['token'] == 'return':
                statements.append(self.returnStatement())
        return statements

    def letStatement(self):
        """
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        let_stmt = {"type": "letStatement", "children": []}
        self.process('let')
        let_stmt['varName'] = self.varName()
        if self.lexer.look()['token'] == '[':
            self.process('[')
            let_stmt['expression'] = self.expression()
            self.process(']')
        self.process('=')
        let_stmt['value'] = self.expression()
        self.process(';')
        return let_stmt

    def ifStatement(self):
        """
        ifStatement : 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        if_statement = {"type": "ifStatement", "children": []}

        # 'if'
        self.process('if')

        # '('
        self.process('(')

        # Expression dans la condition
        if_statement['condition'] = self.expression()

        # ')'
        self.process(')')

        # '{' et les instructions à exécuter si la condition est vraie
        self.process('{')
        if_statement['trueStatements'] = self.statements()
        self.process('}')

        # Si 'else' est présent, traiter l'autre bloc d'instructions
        if self.lexer.look()['token'] == 'else':
            self.process('else')
            self.process('{')
            if_statement['falseStatements'] = self.statements()
            self.process('}')

        return if_statement

    def whileStatement(self):
        """
        whileStatement : 'while' '(' expression ')' '{' statements '}'
        """
        while_statement = {"type": "whileStatement", "children": []}

        # 'while'
        self.process('while')

        # '('
        self.process('(')

        # Expression de la condition
        while_statement['condition'] = self.expression()

        # ')'
        self.process(')')

        # '{' et les instructions à exécuter tant que la condition est vraie
        self.process('{')
        while_statement['statements'] = self.statements()
        self.process('}')

        return while_statement

    def doStatement(self):
        """
        doStatement : 'do' subroutineCall ';'
        """
        do_statement = {"type": "doStatement", "children": []}

        # 'do'
        self.process('do')

        # Appel de la sous-routine
        do_statement['subroutineCall'] = self.subroutineCall()

        # ';'
        self.process(';')

        return do_statement

    def returnStatement(self):
        """
        returnStatement : 'return' expression? ';'
        """
        return_statement = {"type": "returnStatement", "children": []}

        # 'return'
        self.process('return')

        # Expression à retourner (si présente)
        if self.lexer.look()['token'] != ';':
            return_statement['expression'] = self.expression()

        # ';'
        self.process(';')

        return return_statement

    def expression(self):
        """
        expression: term (op term)*
        """
        expr = {"type": "expression", "children": []}
        expr['term'] = self.term()
        while self.lexer.look()['token'] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            expr['children'].append(self.op())
            expr['children'].append(self.term())
        return expr

    def term(self):
        """
        term : integerConstant | stringConstant | keywordConstant
              | varName | varName '[' expression ']' | subroutineCall
              | '(' expression ')' | unaryOp term
        """
        term_node = {"type": "term", "children": []}
        token = self.lexer.look()

        # Identifier (nom de variable)
        if token['type'] == 'identifier':
            term_node["children"].append(self.process(token['token']))  # Traiter le nom de la variable

            # Gestion du tableau (varName '[' expression ']')
            if self.lexer.look()['token'] == '[':
                self.process('[')
                term_node["children"].append(
                    {"type": "expression", "children": [self.expression()]})  # Expression entre []
                self.process(']')

            # Gestion de l'appel de sous-routine (varName '(' expressionList ')')
            elif self.lexer.look()['token'] == '(':
                self.process('(')
                term_node["children"].append({"type": "expressionList", "children": [self.expressionList()]})
                self.process(')')

            # Gestion de l'appel de méthode (varName '.' subroutineName '(' expressionList ')')
            elif self.lexer.look()['token'] == '.':
                self.process('.')
                term_node["children"].append({"type": "subroutineName", "children": [self.subroutineName()]})
                self.process('(')
                term_node["children"].append({"type": "expressionList", "children": [self.expressionList()]})
                self.process(')')

        # Constantes (integerConstant, stringConstant, keywordConstant)
        elif token['type'] == 'IntegerConstant':
            term_node["children"].append(self.process(token['token']))

        elif token['type'] == 'StringConstant':
            term_node["children"].append(self.process(token['token']))

        elif token['type'] == 'keyword':
            term_node["children"].append(self.process(token['token']))

        # Expression entre parenthèses
        elif token['token'] == '(':
            self.process('(')
            term_node["children"].append({"type": "expression", "children": [self.expression()]})
            self.process(')')

        # Opération unaire
        elif token['token'] in ['-', '~']:
            term_node["children"].append(self.process(token['token']))
            term_node["children"].append({"type": "term", "children": [self.term()]})

        else:
            self.error(token)

        return term_node

    #def term(self):
    #    """
    #    term: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall
    #    """
    #    term = {"type": "term", "children": []}
    #    token = self.lexer.look()
    #    if token['type'] == 'identifier':
    #        term['value'] = token['token']
    #    # Ajoutez des cas supplémentaires pour gérer les autres types de termes
    #    return term

    def process(self, expected_token):
        token = self.lexer.next()
        if token and token['token'] == expected_token:
            return token['token']
        else:
            self.error(token)

    def error(self, token):
        if token is None:
            print("Syntax error: unexpected end of file")
        else:
            print(f"SyntaxError (line={token['line']}, col={token['col']}): {token['token']}")
        exit()

    def isIdentifier(self, token):
        """Vérifie si un token est un identifiant valide"""
        return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token) is not None


if __name__ == "__main__":
    file = sys.argv[1]
    parser = Parser(file)
    ast = parser.jackclass()  # Analyse la classe principale
    print(ast)  # Affiche l'arbre syntaxique simplifié
