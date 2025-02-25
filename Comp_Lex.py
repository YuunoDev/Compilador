import re

# Expresiones regulares para identificar tokens
rules_lex = [
    (r"[a-zA-Z_][a-zA-Z0-9_]*", 'ID'),  # Identificadores
    (r'\d*\.\d+|\d+\.\d*', 'FLOAT'),  # Números flotantes
    (r'\d+', 'INT'),  # Números enteros
    (r'\'[^\']*\'', 'STRING'),  # Cadenas de texto
    (r'"[^"]*"', 'STRING'),  # Cadenas de texto
]

rules_color = [
    (r"[a-zA-Z_][a-zA-Z0-9_]*", 'ID'),  # Identificadores
    (r'\d*\.\d+|\d+\.\d*', 'FLOAT'),  # Números flotantes
    (r'\d+', 'INT'),  # Números enteros
    (r'"[^"]*"', 'STRING'),  # Cadenas con comillas dobles
    (r'\'[^\']*\'', 'STRING'),  # Cadenas con comillas simples
    (r'#.*', 'COMMENT'),  # Comentarios con #
    (r'//.*', 'COMMENT'),  # Comentarios con //
    (r'/\*[\s\S]*?\*/', 'COMMENT'),  # Comentarios multilínea
]

coment_rules = [
    (r'#.*', 'COMMENT'),  # Comentarios
    (r'//.*', 'COMMENT'),
    (r'/\*[\s\S]*?\*/', 'COMMENT')  # Comentarios multilínea
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

# Lista para errores
errors = []

def lexer(input_text):
    tokens = []
    position = 0
    line = 1
    column = 0

    while position < len(input_text):
        match = None

        # Manejo de espacios y saltos de línea
        if re.match(r'\n', input_text[position]):
            position += 1
            line += 1
            column = 0
            continue
        elif re.match(r'\s', input_text[position]):
            position += 1
            column += 1
            continue

        # Saltar comentarios
        for pattern, token_type in coment_rules:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                position = match.end()
                column = 0
                break

        # Verificar reglas léxicas
        for pattern, token_type in rules_lex:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                value = match.group()
                if token_type == 'ID' and value in reserved:
                    token_type = reserved[value]
                tokens.append((token_type, value, line, column))
                position = match.end()
                column += len(value)
                break

        # Verificar operadores
        for op, op_type in sorted(operators.items(), key=lambda x: -len(x[0])):  # Ordenar para coincidir los más largos primero
            if input_text.startswith(op, position):
                tokens.append((op_type, op, line, column))
                position += len(op)
                column += len(op)
                match = True
                break

        if match:
            continue

        # Manejo de errores léxicos
        if not match:
            errors.append((line, column, f"Error de sintaxis: {input_text[position]}"))
            position += 1
            column += 1

    return tokens, errors

# Función para colorear el texto
def lexer_color(input_text):
    tokens = []
    position = 0

    while position < len(input_text):
        match = None

        # Ignorar espacios en blanco
        if re.match(r'\s', input_text[position]):
            position += 1
            continue

        
        # verificar comentarios para marcarlos de color
        for pattern, token_type in coment_rules:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                value = match.group()
                tokens.append((token_type, value, 'COMMENT'))
                position = match.end()
                break



        # Verificar operadores
        for op, op_type in sorted(operators.items(), key=lambda x: -len(x[0])):  # Prioriza los más largos
            if input_text.startswith(op, position):
                tokens.append((op_type, op, 'OPERATOR'))
                position += len(op)
                match = True
                break

        if match:
            continue

        # Verificar palabras clave y otros tokens
        for pattern, token_type in rules_color:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                value = match.group()

                # Verificar si es palabra reservada
                if token_type == 'ID' and value in reserved:
                    token_type = reserved[value]

                # Categoría de color
                color_category = 'KEYWORD' if token_type in reserved.values() else 'STRING' if token_type == 'STRING' else 'COMMENT' if token_type == 'COMMENT' else 'NUMBER' if token_type in ['INT', 'FLOAT'] else 'IDENTIFIER'

                tokens.append((token_type, value, color_category))
                position = match.end()
                break

        if not match:
            tokens.append(('ERROR', input_text[position], 'ERROR'))
            position += 1  # Avanza para evitar bucles infinitos

    return tokens



# Leer archivo y probar el lexer
# with open("TestIDE.txt", "r", encoding="utf-8", errors="ignore") as file:
#     code = file.read()

# tokens, errores = lexer(code)

# print("Tokens reconocidos:")
# for token in tokens:
#     print(token)

# print("\nErrores encontrados:")
# for error in errores:
#     print(f"Línea {error[0]}, Columna {error[1]}: {error[2]}")

