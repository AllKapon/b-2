"""No comment"""
import os
import glob
import sys
import Generator


class Translator:
    """No comment"""

    def __init__(self, files):
        self.files = files

    def translate(self):
        """No comment"""

        if os.path.isfile(self.files):
            self._translateonefile(self.files)
        else:
            if os.path.isdir(self.files):
                for file in glob.glob(f'{self.files}/*.jack'):
                    self._translateonefile(file)

    def _translateonefile(self, file):
        """No comment"""
        generator = Generator.Generator(file)
        generator.jackclass()


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: Translator.py <jack file| dir>")
    else:
        jackfiles = sys.argv[1]
        translator = Translator(jackfiles)
        translator.translate()
