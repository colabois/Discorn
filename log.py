class Logger:
    _name = 'Unknown'
    levels = {'debug': '\033[96m',
              'Info': '\033[92m',
              'Warning': '\033[93m',
              'ERROR': '\033[91m'}

    def __init__(self, name):
        self._name = name

    def debug(self, *args, **kwargs):
        level = 'debug'
        print(f'[{self._name}] - {self.levels[level]}[{level}]\033[0m :', *args, **kwargs)

    def info(self, *args, **kwargs):
        level = 'Info'
        print(f'[{self._name}] - {self.levels[level]}[{level}]\033[0m :', *args, **kwargs)

    def warning(self, *args, **kwargs):
        level = 'Warning'
        print(f'[{self._name}] - {self.levels[level]}[{level}]\033[0m :', *args, **kwargs)

    def error(self, *args, **kwargs):
        level = 'ERROR'
        print(f'[{self._name}] - {self.levels[level]}[{level}]\033[0m :', *args, **kwargs)

    def log(self, *args, **kwargs):
        return self.info(*args, **kwargs)
