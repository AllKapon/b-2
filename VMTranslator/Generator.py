"""No comment"""

import sys
import Parser


class Generator:
    """No comment"""

    def __init__(self, file=None):
        """No comment"""
        if file is not None:
            self.parser = Parser.Parser(file)

    def __iter__(self):
        return self

    def __next__(self):
        if self.parser is not None and self.parser.hasNext():
            return self._next()
        else:
            raise StopIteration

    def _next(self):
        # No comment
        command = self.parser.next()
        if command is None:
            return None
        else:
            type = command['type']
            # type = push|pop|
            #        add|sub|neg|eq|gt|lt|and|or|not) |
            #        label|goto|if-goto|
            #        Function|Call|return

            match type:
                # Faire une fonction par type de commande
                case 'push':
                    return self._commandpush(command)
                case 'pop':
                    return self._commandpop(command)
                case 'add' | 'sub' | 'neg' | 'eq' | 'gt' | 'lt' | 'and' | 'or' | 'not':
                    return self._commandarith(command)
                case 'Call':
                    return self.commandcall(command)
                case _:
                    print(f'SyntaxError : {command}')
                    exit()

    def _commandpush(self, command):
        """No comment"""
        segment = command['segment']
        # segment=local|argument|static|constant|this|that|pointer
        match segment:
            # Faire une fonction par type de segment
            case 'constant':
                return self._commandpushconstant(command)
            case 'local' | 'argument' | 'this' | 'that':
                return self._commandpushsegment(command)
            case _:
                print(f'SyntaxError : {command}')
                exit()

    def _commandpop(self, command):
        """No comment"""
        segment = command['segment']
        match segment:
            case 'local' | 'argument' | 'this' | 'that':
                return self._commandpopsegment(command)
            case _:
                print(f'SyntaxError : {command}')
                exit()

    def _commandpushconstant(self, command):
        """Push constant value onto the stack"""
        parameter = command['parameter']
        return f"""\t// push constant {parameter}
    @ {parameter}
    D=A
    @SP
    A=M
    M=D
    @SP
    M=M+1\n"""

    def _commandpushsegment(self, command):
        """Push value from local/argument/this/that segment"""
        segment_map = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }
        segment = command['segment']
        index = command['parameter']
        asm_segment = segment_map[segment]
        return f"""\t// push {segment} {index}
    @{asm_segment}
    D=M
    @{index}
    A=D+A
    D=M
    @SP
    A=M
    M=D
    @SP
    M=M+1\n"""

    def _commandpopsegment(self, command):
        """Pop value from the stack into local/argument/this/that segment"""
        segment_map = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }
        segment = command['segment']
        index = command['parameter']
        asm_segment = segment_map[segment]
        return f"""\t// pop {segment} {index}
    @{asm_segment}
    D=M
    @{index}
    D=D+A
    @R13
    M=D
    @SP
    AM=M-1
    D=M
    @R13
    A=M
    M=D\n"""

    def _commandarith(self, command):
        """Handle arithmetic and logical commands"""
        operation = command['type']
        if operation == 'add':
            return self._commandadd()
        elif operation == 'sub':
            return self._commandsub()
        elif operation == 'neg':
            return self._commandneg()
        elif operation == 'eq':
            return self._commandeq()
        elif operation == 'gt':
            return self._commandgt()
        elif operation == 'lt':
            return self._commandlt()
        elif operation == 'and':
            return self._commandand()
        elif operation == 'or':
            return self._commandor()
        elif operation == 'not':
            return self._commandnot()

    def _commandadd(self):
        """Add the top two elements of the stack"""
        return """\t// add
    @SP
    AM=M-1
    D=M
    A=A-1
    M=M+D\n"""

    def _commandsub(self):
        """Subtract the top two elements of the stack"""
        return """\t// sub
    @SP
    AM=M-1
    D=M
    A=A-1
    M=M-D\n"""

    def _commandneg(self):
        """Negate the top element of the stack"""
        return """\t// neg
    @SP
    A=M-1
    M=-M\n"""

    def _commandand(self):
        """Perform bitwise AND on the top two elements of the stack"""
        return """\t// and
    @SP
    AM=M-1
    D=M
    A=A-1
    M=M&D\n"""

    def _commandor(self):
        """Perform bitwise OR on the top two elements of the stack"""
        return """\t// or
    @SP
    AM=M-1
    D=M
    A=A-1
    M=M|D\n"""

    def _commandnot(self):
        """Perform bitwise NOT on the top element of the stack"""
        return """\t// not
    @SP
    A=M-1
    M=!M\n"""

    def _commandeq(self):
        """Check equality of the top two elements of the stack"""
        return self._comparison_template("JEQ")

    def _commandgt(self):
        """Check if the second-to-top element is greater than the top"""
        return self._comparison_template("JGT")

    def _commandlt(self):
        """Check if the second-to-top element is less than the top"""
        return self._comparison_template("JLT")

    def _comparison_template(self, jump):
        """Template for equality and comparison (eq, gt, lt)"""
        return f"""\t// {jump.lower()}
    @SP
    AM=M-1
    D=M
    A=A-1
    D=M-D
    @TRUE_{jump}
    D;{jump}
    @SP
    A=M-1
    M=0
    @END_{jump}
    0;JMP
(TRUE_{jump})
    @SP
    A=M-1
    M=-1
(END_{jump})\n"""

    def _commandcall(self, command):
        """No comment"""
        return f"""\t//{command['type']} {command['function']} {command['parameter']}
    Code assembleur de {command}\n"""


if __name__ == '__main__':
    file = sys.argv[1]
    print('-----debut')
    generator = Generator(file)
    for command in generator:
        print(command)
    print('-----fin')
