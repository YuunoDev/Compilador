class NumberRecognizerDFA:
    def __init__(self):
        self.state = 0

    def reset(self):
        self.state = 0

    def process(self, input_string):
        self.reset()
        for char in input_string:
            if self.state == 0:
                if char in "+-":
                    self.state = 1
                elif char.isdigit():
                    self.state = 2
                else:
                    return False
            elif self.state == 1:
                if char.isdigit():
                    self.state = 2
                else:
                    return False
            elif self.state == 2:
                if char.isdigit():
                    self.state = 2
                elif char == '.':
                    self.state = 3
                else:
                    return False
            elif self.state == 3:
                if char.isdigit():
                    self.state = 4
                else:
                    return False
            elif self.state == 4:
                if char.isdigit():
                    self.state = 4
                else:
                    return False
        # Estados finales válidos: 2 (entero) o 4 (real)
        return self.state in (2, 4)

# Ejemplo de uso
dfa = NumberRecognizerDFA()
test_cases = ["123", "-45", "+3.14", "0.0", "-.5", "12.", "++4", "abc"]

for case in test_cases:
    result = dfa.process(case)
    print(f"'{case}': {'válido' if result else 'inválido'}")
