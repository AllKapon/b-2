"""No comment"""

import sys
import Lexer


class Parser:
    """la classe Parser sert à  détailler les commandes à partir d'un fichier"""

    def __init__(self, file):
        self.lexer = Lexer.Lexer(file)
        self.command = self._read()

    def next(self):
        """retourne la commande et lit la suivante"""
        res = self.command
        self.command = self._read()
        return res

    def look(self):
        """ retourne la commande """
        return self.command

    def hasNext(self):
        """vérifie si il y a une commande suivante"""
        return self.command is not None

    def __iter__(self):
        return self

    def __next__(self):
        if self.hasNext():
            return self.next()
        else:
            raise StopIteration

    def _read(self):
        # lit la prochaine commande à partir du lexer
        command = self.lexer.look()
        if command is None:
            return None
        else:
            type = command['type']
            match type:
                case 'pushpop':
                    return self._commandpushpop()
                case 'branching':
                    return self._commandbranching()
                case 'arithmetic':
                    return self._commandarithmetic()
                case 'function':
                    return self._commandfunction()
                case 'return':
                    return self._commandreturn()
                case _:
                    print(f'SyntaxError : {command}')
                    exit()

    def _commandarithmetic(self):
        # traite une commande arithmérique
        command = self.lexer.next()
        return {'line': command['line'], 'col': command['col'], 'type': command['token']}

    def _commandpushpop(self):
        # traite une commande push ou pop
        command = self.lexer.next()
        segment = self.lexer.next()
        parameter = self.lexer.next()
        if segment is None or parameter is None or segment['type'] != 'segment' or parameter['type'] != 'int':
            print(f"SyntaxError (line={command['line']}, col={command['col']}): {command['token']}")
            exit()

        return {'line': command['line'], 'col': command['col'], 'type': command['token']
            , 'segment': segment['token'], 'parameter': parameter['token']}

    def _commandbranching(self):
        # traite une commande de branchement
        command = self.lexer.next()
        label = self.lexer.next()
        if label is None or label['type'] != 'string':
            print(f"SyntaxError (line={command['line']}, col={command['col']}): {command['token']}")
            exit()

        return {'line': command['line'], 'col': command['col'], 'type': command['token']
            , 'label': label['token']}

    def _commandfunction(self):
        # traite une commande de fonction
        command = self.lexer.next()
        name = self.lexer.next()
        parameter = self.lexer.next()
        if name is None or parameter is None or name['type'] != 'string' or parameter['type'] != 'int':
            print(f"SyntaxError (line={command['line']}, col={command['col']}): {command['token']}")
            exit()

        return {'line': command['line'], 'col': command['col'], 'type': command['token']
            , 'function': name['token'], 'parameter': parameter['token']}

    def _commandreturn(self):
        # traite une commande de retour
        command = self.lexer.next()
        return {'line': command['line'], 'col': command['col'], 'type': command['token']}


if __name__ == "__main__":
    file = sys.argv[1]
    print('-----debut')
    parser = Parser(file)
    for command in parser:
        print(command)
    print('-----fin')
