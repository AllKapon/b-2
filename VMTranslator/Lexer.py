import re
import sys

import Reader

'''No comment'''


class Lexer:
    """No comment"""

    def __init__(self, file):
        self.reader = Reader.Reader(file)
        self.token = self._read()

    def _comment(self):
        # No comment
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        else:
            return
        if t['char'] == '/':
            while t is not None and t['char'] != '\n':
                t = self.reader.next()
            return
        else:
            while True:
                while t is not None and t['char'] != '*':
                    t = self.reader.next()
                t = self.reader.next()
                if t is None or t['char'] == '/':
                    return

    def _skip(self):
        # No comment
        self.reader.next()
        return

    def _toke(self):
        # No comment
        res = ''
        t = self.reader.next()
        while t is not None and re.fullmatch(r'[a-zA-Z0-9\-]', t['char']):
            res += t['char']
            t = self.reader.next()
        return res

    def next(self):
        """No comment"""
        res = self.token
        self.token = self._read()
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
                    self._comment()
                case ' ' | '\t' | '\n':
                    self._skip()
                case char if re.fullmatch(r'[a-zA-Z0-9]', char):
                    token = self._toke()
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
        return self.token is not None

    def look(self):
        """ No comment """
        return self.token

    def _pattern(self):
        # No comment
        return re.compile(r"""
            (?P<pushpop>push|pop) |
            (?P<segment>local|argument|static|constant|this|that|pointer|temp) |
            (?P<branching>label|goto|if-goto) |
            (?P<arithmetic>add|sub|neg|eq|gt|lt|and|or|not) |
            (?P<function>Function|Call) |
            (?P<return>return) |
            (?P<string>[a-zA-Z][a-zA-Z0-9]*) | # label et nom de fonction
            (?P<int>[0-9]+) # des entiers 
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
