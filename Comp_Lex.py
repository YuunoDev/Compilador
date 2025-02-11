import re

# Expresiones regulares para identificar tokens
rules_color = [
    (r"[a-zA-Z_][a-zA-Z0-9_]*", 'ID'),  # Identificadores
    (r'\d*\.\d+|\d+\.\d*', 'FLOAT'),  # Números flotantes
    (r'\d+', 'INT'),  # Números enteros
    (r'"[^"]*"', 'STRING'),  # Cadenas de texto
    (r'#.*', 'COMMENT'),  # Comentarios
]

rules_lex = [
    (r"[a-zA-Z_][a-zA-Z0-9_]*", 'ID'),  # Identificadores
    (r'\d*\.\d+|\d+\.\d*', 'FLOAT'),  # Números flotantes
    (r'\d+', 'INT'),  # Números enteros
    (r'\'[^\']*\'', 'STRING'),  # Cadenas de texto
    (r'"[^"]*"', 'STRING'),  # Cadenas de texto
]

coment_rules = [
    (r'#.*', 'COMMENT'),  # Comentarios
    (r'//.*', 'COMMENT'),  # Comentarios
]

# Operadores y símbolos especiales
operators = {
    '+': 'PLUS', '-': 'MINUS', '*': 'MULT', '/': 'DIV', '%': 'MOD',
    '==': 'EQUALS', '!=': 'DIFF', '<': 'LESS', '<=': 'LESSEQ',
    '>': 'GREATER', '>=': 'GREATEREQ', '=': 'ASSIGN',
    '(': 'LPAREN', ')': 'RPAREN',
    '{': 'LBRACE', '}': 'RBRACE',
    '[': 'LBRACKET', ']': 'RBRACKET',
    ',': 'COMMA', ':': 'COLON', ';': 'TERM',
    '++': 'INCREMENT', '--': 'DECREMENT',
    '&&': 'AND', '||': 'OR', '!': 'NOT'
}

# Palabras reservadas
reserved = {
    'if': 'IF', 'else': 'ELSE', 'while': 'WHILE',
    'for': 'FOR', 'in': 'IN', 'range': 'RANGE',
    'def': 'DEF', 'return': 'RETURN', 'int': 'TYPE',
    'float': 'TYPE', 'str': 'TYPE', 'bool': 'TYPE',
    'True': 'BOOL', 'False': 'BOOL', 'None': 'NONE',
    'print': 'PRINT', 'input': 'INPUT', 'len': 'LEN',
    'string': 'TYPE'
}

# Lexer simple
def lexer(input_text):
    tokens = []
    position = 0
    #posicion de la linea
    line = 1
    #posicion de la columna
    column = 0

    while position < len(input_text):
        match = None

        # Ignorar espacios saltos de linea y tabulaciones
        if re.match(r'\n', input_text[position]) or re.match(r'\r', input_text[position]):
            position += 1
            line += 1 
            column = 0
            continue
        elif re.match(r' ', input_text[position]):
            position += 1
            column += 1
            continue

        # saltar comentarios
        for pattern, token_type in coment_rules:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                position = match.end()
                line += 1
                column = 0
                break

        # Verificar operadores
        for op, op_type in operators.items():
            if input_text.startswith(op, position):
                tokens.append((op_type, op, line, column))
                position += len(op)
                column += len(op)
                match = True
                break

        if match:
            continue

        # Verificar reglas
        for pattern, token_type in rules_lex:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                value = match.group()
                # Verificar si es palabra reservada
                if token_type == 'ID' and value in reserved:
                    token_type = reserved[value]
                tokens.append((token_type, value, line, column))
                position = match.end()
                column += len(value)
                break

        if not match:
            raise Exception(f"Error de sintaxis en: {input_text[position:]}")
        
    return tokens


def lexer_color(input_text):
    tokens = []
    position = 0

    while position < len(input_text):
        match = None

        # Ignorar espacios en blanco
        if re.match(r'\s', input_text[position]):
            position += 1
            continue

        # Verificar operadores
        for op, op_type in operators.items():
            if input_text.startswith(op, position):
                tokens.append((op_type, op))
                position += len(op)
                match = True
                break

        if match:
            continue

        # Verificar reglas
        for pattern, token_type in rules_color:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                value = match.group()
                # Verificar si es palabra reservada
                if token_type == 'ID' and value in reserved:
                    token_type = reserved[value]
                tokens.append((token_type, value))
                position = match.end()
                break

        if not match:
            raise Exception(f"Error de sintaxis en: {input_text[position:]}")
        
    return tokens