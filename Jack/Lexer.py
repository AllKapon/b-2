import re
import sys
import Reader

class Lexer:
    """A simple lexer for the Jack language"""

    def __init__(self, file):
        self.reader = Reader.Reader(file)
        self.tokens = [self._read(), self._read()]

    def _comment(self):
        # Handles comments
        t = self.reader.next()
        if self.reader.hasNext():
            t = self.reader.next()
        if t['char'] == '/':  # Single-line comment
            while self.reader.hasNext() and t['char'] != '\n':
                t = self.reader.next()
            return
        elif t['char'] == '*':  # Multi-line comment
            while True:
                while self.reader.hasNext() and t['char'] != '*':
                    t = self.reader.next()
                t = self.reader.next()
                if t and t['char'] == '/':
                    return
                if not t:  # End of file
                    return

    def _skip(self):
        self.reader.next()  # Just skip the current character

    def _toke(self):
        res = ''
        t = self.reader.look()
        while t is not None and re.fullmatch(r'[a-zA-Z0-9_]', t['char']):
            res += t['char']
            t = self.reader.next()
            if self.reader.hasNext():
                t = self.reader.look()
        return res

    def _stringConstant(self):
        res = '"'
        t = self.reader.next()  # Move past the opening "
        while t is not None and t['char'] != '"':
            res += t['char']
            t = self.reader.next()
        res += '"'  # Append closing "
        return res

    def next(self):
        """Get the next token."""
        res = self.tokens[0]
        self.tokens[0] = self.tokens[1]
        self.tokens[1] = self._read()
        print(f"Token generated: {res}")  # Ajoutez cette ligne

        return res

    def _read(self):
        token = None
        while self.reader.hasNext() and token is None:
            self.line = self.reader._line
            self.col = self.reader._col
            t = self.reader.look()
            char = t['char']
            match char:
                case '/':
                    if self._comment() is not None:
                        token = '/'
                case '(' | ')' | '[' | ']' | '{' | '}' | ',' | ';' | '=' | '.' | '+' | '-' | '*' | '&' | '|' | '~' | '<' | '>':
                    token = char
                    self._skip()
                case ' ' | '\t' | '\n':
                    self._skip()
                case char if re.fullmatch(r'[a-zA-Z0-9_]', char):
                    token = self._toke()
                case '"':
                    token = self._stringConstant()
                case _:
                    print(f'SyntaxError (line={self.line}, col={self.col}): Unexpected character {char}')
                    exit()

        if token is None:
            return None
        else:
            pattern = self._pattern()
            group = pattern.fullmatch(token)
            if group is None:
                print(f'SyntaxError (line={self.line}, col={self.col}): Invalid token {token}')
                exit()
            else:
                return {'line': self.line, 'col': self.col, 'type': group.lastgroup, 'token': token}

    def hasNext(self):
        """Check if there's a next token."""
        return self.tokens[0] is not None

    def look(self):
        """Peek at the next token."""
        return self.tokens[0]

    def _pattern(self):
        """Regex pattern for different token types."""
        return re.compile(r"""  
            (?P<symbol>[()[\]{},;=.+\-*/&|~<>])|  
            (?P<keyword>class|constructor|method|function|int|boolean|char|void|var|static|field|let|do|if|else|while|return|true|false|null|this) |  
            (?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*) |   
            (?P<StringConstant>\"[^\n]*\") |   
            (?P<IntegerConstant>[0-9]+)   
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
    print('----- Start Parsing -----')
    lexer = Lexer(file)
    for token in lexer:
        print(token)
    print('----- End Parsing -----')