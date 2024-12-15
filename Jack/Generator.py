"""No comment"""
import sys
import Parser




class Generator:
    """No comment"""

    def __init__(self, file=None):
        if file is not None:
            self.parser = Parser.Parser(file)
            self.arbre = self.parser.jackclass()
            print("Arbre syntaxique:", self.arbre)
            self.vmfile = open(self.arbre['name'] + '.vm', "w")
            self.symbolClassTable = []
            self.symbolRoutineTable = []
            self.output = []

    def jackclass(self):
        """
        Gère la classe Jack, incluant les déclarations de variables et sous-programmes.
        """
        class_name = self.arbre['name']
        print(f"Processing class: {class_name}")

        # Vérifie et traite les variables de classe
        for var in self.arbre.get('varDec', []):
            self.variable(var)

        self.vmfile.write(f"// Class {self.arbre['name']}\n")
        for subroutine in self.arbre['subroutineDec']:
            self.subroutineDec(subroutine)

    def variable(self, var):
        """
        Ajoute une variable à la table des symboles.
        """
        if var['kind'] in ['static', 'field']:
            self.symbolClassTable.append(var)
        elif var['kind'] in ['argument', 'local']:
            self.symbolRoutineTable.append(var)
        else:
            self.error(f"Type de variable inconnu: {var['kind']}")

    def subroutineDec(self, routine):
        """
        Gère les déclarations de sous-programmes.
        """
        # Type de sous-programme (function, constructor, method)
        subroutine_type = routine['type']
        subroutine_name = routine['name']

        # Nombre de variables locales
        num_locals = len(routine['body']['vars'])  # Corrigé pour accéder à la clé correcte

        # Déclare la fonction dans le fichier VM
        self.write_vm(f"function {self.arbre['name']}.{subroutine_name} {num_locals}")

        # Initialisation spécifique pour les méthodes et constructeurs
        if subroutine_type == 'method':
            # Initialisation pour les méthodes : définir `this` sur l'objet passé en argument
            self.write_vm("push argument 0")
            self.write_vm("pop pointer 0")
        elif subroutine_type == 'constructor':
            # Initialisation pour les constructeurs : allouer de la mémoire pour les champs
            num_fields = sum(1 for var in self.symbolClassTable if var['kind'] == 'field')
            self.write_vm(f"push constant {num_fields}")
            self.write_vm("call Memory.alloc 1")
            self.write_vm("pop pointer 0")

        # Traiter les instructions du# Example snippet to handle the "." symbol in your tokenizer/parser.

 # Consume the identifier

        for instruction in routine['body']['statements']:  # Corrigé pour accéder à 'statements'
            self.statement(instruction)

    def statement(self, instruction):
        """
        Gère une instruction spécifique (do, let, if, while, return).
        """
        instruction_type = instruction['type']

        if instruction_type == 'doStatement':
            self.doStatement(instruction)  # Appel de la méthode doStatement
        elif instruction_type == 'letStatement':
            self.letStatement(instruction)
        elif instruction_type == 'ifStatement':
            self.ifStatement(instruction)
        elif instruction_type == 'whileStatement':
            self.whileStatement(instruction)
        elif instruction_type == 'returnStatement':
            self.returnStatement(instruction)
        else:
            raise SyntaxError(f"Instruction inconnue: {instruction_type}")

    def letStatement(self, inst):
        """
        {'line': line, 'col': col, 'type': 'let',
         'name': varName, 'indice': expression, 'valeur': expression}
        """
        print(f"Processing let statement: {inst}")  # Debugging line
        var_name = inst.get('name')  # Get the variable name (e.g., 'sum') instead of 'variable'
        if not var_name:
            print(f"Error: Missing 'name' key in instruction: {inst}")
            return

        value = inst.get('valeur')  # Get the value to assign to the variable (e.g., 'a + b')
        if not value:
            print(f"Error: Missing 'valeur' key in instruction: {inst}")
            return

        # Generate code for the value (right-hand side of the assignment)
        self.expression(value)  # This should push the result of 'a + b' onto the stack

        # Debugging line to check the stack before the assignment
        print(f"Stack after evaluating {value}:")  # Debugging line
        self.write_vm("debug stack")  # This is a placeholder for your method to print the stack

        # Check if it's an array assignment
        if 'indice' in inst and inst['indice']:
            # Evaluate the array index (for array assignments like arr[i] = value)
            self.expression(inst['indice'])
            # Push base address of the array
            self.write_vm(f"push {self.get_segment(var_name)} {self.get_index(var_name)}")
            # Add the index to the base address
            self.write_vm("add")
            # Store the value in the address pointed by the computed address
            self.write_vm("pop temp 0")
            self.write_vm("pop pointer 1")
            self.write_vm("push temp 0")
            self.write_vm("pop that 0")
        else:
            # Simple assignment (for scalar variables like 'sum = 5')
            # Pop the evaluated value and assign it to the variable
            self.write_vm(f"pop {self.get_segment(var_name)} {self.get_index(var_name)}")
            print(f"Assigned {value} to {var_name}")  # Debugging line

    def ifStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'if', 'condition': expression, 'true': [instruction],
        'false': [instruction]}
        """
        label_true = self.new_label()
        label_false = self.new_label()

        self.expression(inst['condition'])
        self.write_vm(f"if-goto {label_true}")
        for instr in inst['false']:
            self.statement(instr)
        self.write_vm(f"goto {label_false}")
        self.write_vm(f"label {label_true}")
        for instr in inst['true']:
            self.statement(instr)
        self.write_vm(f"label {label_false}")

    def whileStatement(self, inst):
        """
        {'line':line, 'col': col,
        'type': 'while', 'condition': expression,
        'instructions': [instruction]}
        """
        label_start = self.new_label()
        label_end = self.new_label()

        self.write_vm(f"label {label_start}")
        self.expression(inst['condition'])
        self.write_vm(f"not")
        self.write_vm(f"if-goto {label_end}")
        for instr in inst['instructions']:
            self.statement(instr)
        self.write_vm(f"goto {label_start}")
        self.write_vm(f"label {label_end}")

    def doStatement(self, instruction):
        """
        Gère une instruction `do`, qui correspond à un appel de sous-routine.
        """
        subroutine_call = instruction['call']  # Extraire l'appel de sous-routine
        self.subroutineCall(subroutine_call)  # Traiter l'appel de sous-routine

        # Ignore la valeur de retour de l'appel de sous-routine
        self.write_vm("pop temp 0")

    def returnStatement(self, inst):
        """
        {'line':line, 'col': col, 'type': 'return', 'valeur': expression}
        """
        if 'valeur' in inst and inst['valeur'] is not None:
            self.expression(inst['valeur'])
        else:
            self.write_vm("push constant 0")
        self.write_vm("return")

    def expression(self, exp):
        """
        [term op ...]
        avec op : '+'|'-'|'*'|'/'|'&'|'|'<'|'>'|'='
        """
        print(f"Processing expression: {exp}")

        # Traiter le terme gauche (left)
        if 'left' in exp:
            print(f"Left term: {exp['left']}")
            self.term(exp['left'])

        # Vérifier si un opérateur est présent et traiter le terme droit (right)
        if 'op' in exp:
            print(f"Operator: {exp['op']}")

            # Traiter le terme droit (right)
            if 'right' in exp:
                print(f"Right term: {exp['right']}")
                self.term(exp['right'])

            # Générer le code VM pour l'opérateur
            if exp['op'] == '+':
                print("VM Code: add")
                self.write_add()  # Ajoute l'instruction VM pour l'addition
            elif exp['op'] == '-':
                print("VM Code: sub")
                self.write_sub()  # Ajoute l'instruction VM pour la soustraction
            elif exp['op'] == '*':
                print("VM Code: call Math.multiply 2")
                self.write_call("Math.multiply", 2)  # Appelle la multiplication
            elif exp['op'] == '/':
                print("VM Code: call Math.divide 2")
                self.write_call("Math.divide", 2)  # Appelle la division
            elif exp['op'] == '&':
                print("VM Code: and")
                self.write_and()  # Effectue une opération AND
            elif exp['op'] == '|':
                print("VM Code: or")
                self.write_or()  # Effectue une opération OR
            elif exp['op'] == '<':
                print("VM Code: lt")
                self.write_lt()  # Effectue une comparaison inférieure
            elif exp['op'] == '>':
                print("VM Code: gt")
                self.write_gt()  # Effectue une comparaison supérieure
            elif exp['op'] == '=':
                print("VM Code: eq")
                self.write_eq()  # Effectue une comparaison d'égalité

    def term(self, t):
        """
        {'line':line, 'col': col,
        'type': 'int'| 'string'| 'constant'| 'varName'|'call'| 'expression'|'-'|'~',
         'indice':expression, 'subroutineCall': subroutineCall}
        """
        if t['type'] == 'int':
            self.write_vm(f"push constant {t['value']}")
        elif t['type'] == 'string':
            self.handle_string(t['value'])
        elif t['type'] == 'varName':
            self.write_vm(f"push {self.get_segment(t['name'])} {self.get_index(t['name'])}")
        elif t['type'] == 'call':
            self.subroutineCall(t['subroutineCall'])
        elif t['type'] == 'expression':
            self.expression(t['value'])

    def subroutineCall(self, call):
        """
        {'line':line, 'col': col, 'classvar': className ou varName,
        'name': subroutineName, 'argument': [expression]}
        """
        object_name = call.get('object')  # Objet ou classe
        subroutine_name = call['name']  # Nom de la méthode
        args = call['args']  # Arguments de la méthode

        if object_name:
            full_name = f"{object_name}.{subroutine_name}"
        else:
            full_name = subroutine_name
        # Traiter les arguments
        num_args = 0
        for arg in args:
            self.expression(arg)  # Génère le code pour chaque argument
            num_args += 1
        self.write_vm(f"call {full_name} {num_args}")

    def handle_string(self, value):
        """
        Gère une chaîne de caractères.
        """
        self.write_vm(f"push constant {len(value)}")
        self.write_vm("call String.new 1")
        for char in value:
            self.write_vm(f"push constant {ord(char)}")
            self.write_vm("call String.appendChar 2")

    def get_segment(self, var_name):
        """
        Récupère le segment de mémoire pour une variable.
        """
        for var in self.symbolClassTable + self.symbolRoutineTable:
            if var['name'] == var_name:
                return {'static': 'static', 'field': 'this', 'argument': 'argument', 'local': 'local'}[var['kind']]
        self.error(f"Variable inconnue: {var_name}")

    def get_index(self, var_name):
        """
        Récupère l'index d'une variable dans son segment.
        """
        for i, var in enumerate(self.symbolClassTable + self.symbolRoutineTable):
            if var['name'] == var_name:
                return i
        self.error(f"Variable inconnue: {var_name}")

    def new_label(self):
        """
        Génère un nouveau label unique.
        """
        if not hasattr(self, '_label_count'):
            self._label_count = 0
        label = f"L{self._label_count}"
        self._label_count += 1
        return label

    def write_vm(self, command):
        """Writes VM command to the file and also prints it for debugging."""
        print(command)  # Debugging line
        self.vmfile.write(command + '\n')

    def error(self, message=''):
        print(f"SyntaxError: {message}")
        exit()


    def write_push(self, segment, index):
        """Génère une instruction VM pour un 'push'."""
        self.output.append(f"push {segment} {index}")

    def write_pop(self, segment, index):
        """Génère une instruction VM pour un 'pop'."""
        self.output.append(f"pop {segment} {index}")

    def write_add(self):
        """Génère une instruction VM pour l'addition."""
        self.output.append("add")

    def write_sub(self):
        """Génère une instruction VM pour la soustraction."""
        self.output.append("sub")

    def write_neg(self):
        """Génère une instruction VM pour la négation."""
        self.output.append("neg")

    def write_eq(self):
        """Génère une instruction VM pour la comparaison d'égalité."""
        self.output.append("eq")

    def write_gt(self):
        """Génère une instruction VM pour la comparaison 'greater than'."""
        self.output.append("gt")

    def write_lt(self):
        """Génère une instruction VM pour la comparaison 'less than'."""
        self.output.append("lt")

    def write_and(self):
        """Génère une instruction VM pour l'opération logique AND."""
        self.output.append("and")

    def write_or(self):
        """Génère une instruction VM pour l'opération logique OR."""
        self.output.append("or")

    def write_not(self):
        """Génère une instruction VM pour l'opération logique NOT."""
        self.output.append("not")

    def write_call(self, name, num_args):
        """Génère une instruction VM pour appeler une fonction."""
        self.output.append(f"call {name} {num_args}")

    def write_return(self):
        """Génère une instruction VM pour retourner d'une fonction."""
        self.output.append("return")

    def write_function(self, name, num_locals):
        """Génère une instruction VM pour définir une fonction."""
        self.output.append(f"function {name} {num_locals}")

    def write_label(self, label):
        """Génère une instruction VM pour un label."""
        self.output.append(f"label {label}")

    def write_goto(self, label):
        """Génère une instruction VM pour un saut inconditionnel."""
        self.output.append(f"goto {label}")

    def write_if(self, label):
        """Génère une instruction VM pour un saut conditionnel."""
        self.output.append(f"if-goto {label}")

    def get_vm_output(self):
        return self.get_output()

    def get_output(self):
        """Retourne le code VM généré sous forme de chaîne."""
        return "\n".join(self.output)

if __name__ == '__main__':
    file = sys.argv[1]
    print('-----debut')
    generator = Generator(file)
    generator.jackclass()
    print('-----fin')