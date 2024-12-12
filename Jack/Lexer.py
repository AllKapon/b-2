import re
import sys

import Reader

'''No comment'''


class Lexer:
    """No comment"""

    def __init__(self, file):
        self.reader = Reader.Reader(file)
        self.tokens = [self._read(),self._read()]

    def _comment(self):
        # No comment
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        else:
            return None
        match t['char']:
            case '/':
                while t is not None and t['char'] != '\n':
                    t = self.reader.next()
                return None
            case '*':
                while True:
                    while t is not None and t['char'] != '*':
                        t = self.reader.next()
                    t = self.reader.next()
                    if t is None or t['char'] == '/':
                        return
            case _:
                return '/'

    def _skip(self):
        # No comment
        self.reader.next()
        return

    def _toke(self):
        # No comment
        res = ''
        t = self.reader.look()
        while t is not None and re.fullmatch(r'[a-zA-Z0-9_]', t['char']):
            t = self.reader.next()
            res += t['char']
            t = self.reader.look()
        return res

    def _stringConstant(self):
        res = '"'
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        else:
            return '""'
        while t is not None and t['char'] != '\"':
            res += t['char']
            t = self.reader.next()
        return res + '"'

    def next(self):
        """No comment"""
        res = self.tokens[0]
        self.tokens[0]=self.tokens[1]
        self.tokens[1] = self._read()
        return res

    def _read(self):
        # No comment
        token = None
        while self.reader.hasNext() and token is None:
            self.line = self.reader._line
            self.col = self.reader._col
            t = self.reader.look()
            char = t['char']
            match char:
                case '/':
                    if self._comment() is not None:
                        token = "/"
                case '(' | ')' | '[' | ']' | '{' | '}' | ',' | ';' | '=' | '.' | '+' | '-' | '*' | '&' | '/|' | '~' | '<' | '>':
                    token = char
                    self._skip()
                case ' ' | '\t' | '\n':
                    self._skip()
                case char if re.fullmatch(r'[a-zA-Z0-9_]', char):
                    token = self._toke()
                case '"':
                    token = self._stringConstant()
                case _:
                    print(f'SyntaxError : line={self.line}, col={self.col}')
                    exit()

        if token is None:
            return None
        else:
            pattern = self._pattern()
            group = pattern.fullmatch(token)
            if group is None:
                print(f'SyntaxError (line={self.line}, col={self.col}): {token}')
                exit()
            else:
                return {'line': self.line, 'col': self.col, 'type': group.lastgroup, 'token': token}

    def hasNext(self):
        """ No comment """
        return self.tokens[0] is not None

    def hasNext2(self):
        """ No comment """
        return self.tokens[1] is not None

    def look(self):
        """ No comment """
        return self.tokens[0]

    def look2(self):
        """ No comment """
        return self.tokens[1]

    def _pattern(self):
        # No comment
        return re.compile(r"""
            (?P<symbol>[()[\]{},;=.+\-*/&|~<>])|
            (?P<keyword>class|constructor|method|function|int|boolean|char|void|var|static|field|let|do|if|else|while|return|true|false|null|this) |
            (?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*) | # identifiant
            (?P<StringConstant>\"[^\n]*\") | # chaine de caracteres sans retour a la ligne
            (?P<IntegerConstant>[0-9]+) | # des entiers  
        """, re.X)

    def __iter__(self):
        return self

    def __next__(self):
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    lexer = Lexer(file)
    for token in lexer:
        print(token)
    print('-----fin')
