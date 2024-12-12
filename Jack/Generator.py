"""No comment"""
import sys
import Parser

class Generator:
    """
    Générateur pour produire le code VM à partir de l'arbre syntaxique d'un programme Jack.
    """

    def __init__(self, file=None):
        if file is not None:
            self.parser = Parser.Parser(file)
            self.arbre = self.parser.jackclass()
            self.vmfile = open(self.arbre['name'] + '.vm', "w")
            self.symbolClassTable = {}
            self.symbolRoutineTable = {}

    def write(self, command):
        """Écrit une commande dans le fichier VM."""
        self.vmfile.write(command + '\n')

    def jackclass(self):
        """
        Traite la structure de la classe Jack et génère le code VM correspondant.
        """
        class_name = self.arbre['name']
        var_declarations = self.arbre['varDec']
        subroutines = self.arbre['subroutine']

        # Traiter les déclarations de variables
        for var in var_declarations:
            self.variable(var)

        # Traiter les sous-routines
        for subroutine in subroutines:
            self.subroutineDec(subroutine)

        self.vmfile.close()

    def variable(self, var):
        """
        Ajoute une variable à la table des symboles et traite ses attributs.
        """
        kind = var['kind']
        name = var['name']
        var_type = var['type']

        if kind in ('static', 'field'):
            self.symbolClassTable[name] = (var_type, kind)
        else:
            self.symbolRoutineTable[name] = (var_type, kind)

    def subroutineDec(self, routine):
        """
        Gère une déclaration de sous-routine.
        """
        subroutine_type = routine['type']
        subroutine_name = routine['name']
        arguments = routine['argument']
        locals_ = routine['local']
        instructions = routine['instructions']

        # Ajouter arguments et variables locales à la table des symboles
        for arg in arguments:
            self.variable(arg)

        for local_var in locals_:
            self.variable(local_var)

        # Écrire le header de la fonction
        self.write(f"function {self.arbre['name']}.{subroutine_name} {len(locals_)}")

        # Instructions spécifiques au constructeur, méthode, ou fonction
        if subroutine_type == 'constructor':
            num_fields = sum(1 for v in self.symbolClassTable.values() if v[1] == 'field')
            self.write(f"push constant {num_fields}")
            self.write("call Memory.alloc 1")
            self.write("pop pointer 0")
        elif subroutine_type == 'method':
            self.write("push argument 0")
            self.write("pop pointer 0")

        # Écrire les instructions
        for instruction in instructions:
            self.statement(instruction)

    def statement(self, inst):
        """
        Route vers le bon type d'instruction.
        """
        inst_type = inst['type']
        if inst_type == 'let':
            self.letStatement(inst)
        elif inst_type == 'if':
            self.ifStatement(inst)
        elif inst_type == 'while':
            self.whileStatement(inst)
        elif inst_type == 'do':
            self.doStatement(inst)
        elif inst_type == 'return':
            self.returnStatement(inst)

    def letStatement(self, inst):
        """Génère le code VM pour une instruction let."""
        variable = inst['variable']
        value = inst['valeur']

        self.expression(value)
        self.write(f"pop {self._get_segment(variable)} {self._get_index(variable)}")

    def ifStatement(self, inst):
        """Génère le code VM pour une instruction if."""
        condition = inst['condition']
        true_label = self._new_label("IF_TRUE")
        false_label = self._new_label("IF_FALSE")

        self.expression(condition)
        self.write("not")
        self.write(f"if-goto {false_label}")

        for true_inst in inst['true']:
            self.statement(true_inst)

        self.write(f"goto {true_label}")
        self.write(f"label {false_label}")

        for false_inst in inst.get('false', []):
            self.statement(false_inst)

        self.write(f"label {true_label}")

    def whileStatement(self, inst):
        """Génère le code VM pour une instruction while."""
        start_label = self._new_label("WHILE_START")
        end_label = self._new_label("WHILE_END")

        self.write(f"label {start_label}")
        self.expression(inst['condition'])
        self.write("not")
        self.write(f"if-goto {end_label}")

        for instruction in inst['instructions']:
            self.statement(instruction)

        self.write(f"goto {start_label}")
        self.write(f"label {end_label}")

    def doStatement(self, inst):
        """Génère le code VM pour une instruction do."""
        self.subroutineCall(inst)
        self.write("pop temp 0")  # Ignorer la valeur de retour

    def returnStatement(self, inst):
        """Génère le code VM pour une instruction return."""
        if 'valeur' in inst:
            self.expression(inst['valeur'])
        else:
            self.write("push constant 0")
        self.write("return")

    def expression(self, exp):
        """Génère le code VM pour une expression."""
        for term in exp:
            self.term(term)

    def term(self, t):
        """Génère le code VM pour un terme."""
        term_type = t['type']
        if term_type == 'int':
            self.write(f"push constant {t['value']}")
        elif term_type == 'varName':
            self.write(f"push {self._get_segment(t['name'])} {self._get_index(t['name'])}")

    def subroutineCall(self, call):
        """Génère le code VM pour un appel de sous-routine."""
        for arg in call['argument']:
            self.expression(arg)
        self.write(f"call {call['classvar']}.{call['name']} {len(call['argument'])}")

    def _get_segment(self, var_name):
        """Renvoie le segment de mémoire correspondant à une variable."""
        if var_name in self.symbolRoutineTable:
            kind = self.symbolRoutineTable[var_name][1]
        else:
            kind = self.symbolClassTable[var_name][1]
        return {'static': 'static', 'field': 'this', 'arg': 'argument', 'var': 'local'}.get(kind)

    def _get_index(self, var_name):
        """Renvoie l'index de la variable."""
        # Non implémenté : Ajouter une méthode de suivi des indices
        return 0

    def _new_label(self, base):
        """Génère un nouveau label unique."""
        from uuid import uuid4
        return f"{base}_{uuid4().hex[:8]}"

    def error(self, message=''):
        print(f"SyntaxError: {message}")
        exit()

if __name__ == '__main__':
    file = sys.argv[1]
    generator = Generator(file)
    generator.jackclass()
    print('-----fin')
