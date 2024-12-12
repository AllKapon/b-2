"""No comment"""
import os
import glob
import sys

import Generator


class Translator:
    """No comment"""

    def __init__(self, files, asm):
        self.asm = open(asm, "w")
        self.files = files

    def translate(self):
        """No comment"""
        self.asm.write(self._bootstrap())
        # os.listdir("/home/olivier")
        if os.path.isfile(self.files):
            self._translateonefile(self.files)
        else:
            if os.path.isdir(self.files):
                for file in glob.glob(f'{self.files}/*.vm'):
                    self._translateonefile(file)

    def _translateonefile(self, file):
        """No comment"""
        self.asm.write(f"""\n//code de {file}\n""")
        generator = Generator.Generator(file)
        for command in generator:
            self.asm.write(command)

    def _bootstrap(self):
        """No comment"""
        init = Generator.Generator()._commandcall({'type': 'Call', 'function': 'Sys.init', 'parameter': '0'})

        return f"""// Bootstrap
    @256
    D=A
    @SP
    M=D
{init}
"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: Translotor.py <vm file| dir> <asm file>")
    else:
        vmfiles=sys.argv[1]
        asmfile=sys.argv[2]
        translator = Translator(vmfiles,asmfile)
        translator.translate()
