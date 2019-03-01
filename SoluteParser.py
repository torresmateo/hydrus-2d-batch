class SoluteParser(object):

    def __init__(self, filename):
        self.file = open(filename)
        self.lineno = 0

    def __iter__(self):
        for line in self.file:
            self.lineno += 1
            if self.lineno <= 5:
                continue
            if not line.startswith('end'):
                parts = line.strip().split()
                yield parts[0], parts[2]
