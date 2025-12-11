class ASTNode:
    def __init__(self, tipo, valor=None, linea=None, columna=None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
        self.hijos = []
        self.es_error = False
        self.tipo_dato = None
        self.scope = None
        self.use = False
    
    def agregar_hijo(self, hijo):
        if hijo:
            self.hijos.append(hijo)

    def setvalor(self, valor):
        self.valor = valor
    
    def marcar_error(self):
        self.es_error = True

    def marcar_warning(self):
        self.es_warning = True

    def set_tipo(self, tipo):
        self.tipo = tipo
    
    def __repr__(self):
        return f"ASTNode({self.tipo}, {self.valor})"


class ThreeAddressCode:
    """Representa una instrucción de código de tres direcciones"""
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op          # operación
        self.arg1 = arg1      # primer argumento
        self.arg2 = arg2      # segundo argumento
        self.result = result  # resultado
    
    def __str__(self):
        if self.op in ['=', 'ASSIGN']:
            return f"{self.result} = {self.arg1}"
        elif self.op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', 'AND', 'OR', '&&', '||']:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op == 'UNARY_MINUS':
            return f"{self.result} = -{self.arg1}"
        elif self.op == 'NOT':
            return f"{self.result} = !{self.arg1}"
        elif self.op == 'GOTO':
            return f"goto {self.result}"
        elif self.op == 'IF_FALSE':
            return f"if !{self.arg1} goto {self.result}"
        elif self.op == 'IF_TRUE':
            return f"if {self.arg1} goto {self.result}"
        elif self.op == 'LABEL':
            return f"{self.result}:"
        elif self.op == 'PARAM':
            return f"param {self.arg1}"
        elif self.op == 'CALL':
            if self.result:
                return f"{self.result} = call {self.arg1}, {self.arg2}"
            return f"call {self.arg1}, {self.arg2}"
        elif self.op == 'RETURN':
            if self.arg1:
                return f"return {self.arg1}"
            return "return"
        elif self.op == 'ARRAY_ACCESS':
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        elif self.op == 'ARRAY_ASSIGN':
            return f"{self.result}[{self.arg1}] = {self.arg2}"
        elif self.op == 'PRINT':
            return f"print {self.arg1}"
        elif self.op == 'READ':
            return f"read {self.result}"
        else:
            return f"{self.op} {self.arg1 or ''} {self.arg2 or ''} {self.result or ''}".strip()


class IntermediateCodeGenerator:
    """Generador de código intermedio de tres direcciones"""
    
    def __init__(self):
        self.code = []                  # lista de instrucciones TAC
        self.temp_count = 0             # contador de temporales
        self.label_count = 0            # contador de etiquetas
        self.current_function = None    # función actual
        
    def new_temp(self):
        """Genera un nuevo temporal"""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def new_label(self):
        """Genera una nueva etiqueta"""
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def emit(self, op, arg1=None, arg2=None, result=None):
        """Emite una instrucción de tres direcciones"""
        instruction = ThreeAddressCode(op, arg1, arg2, result)
        self.code.append(instruction)
        return instruction
    
    def generate(self, node):
        """
        Punto de entrada principal para generar código
        Retorna el temporal o variable que contiene el resultado (para expresiones)
        """
        if not node or node.es_error:
            return None
        
        # Mapeo de tipos de nodos a métodos generadores
        handlers = {
            # Expresiones
            'NUMERO': self._gen_literal,
            'ENTERO': self._gen_literal,
            'DECIMAL': self._gen_literal,
            'CADENA': self._gen_literal,
            'BOOLEANO': self._gen_literal,
            'IDENTIFICADOR': self._gen_identifier,
            'OPERACION_BINARIA': self._gen_binary_op,
            'OPERACION_UNARIA': self._gen_unary_op,
            'LLAMADA_FUNCION': self._gen_function_call,
            'ACCESO_ARREGLO': self._gen_array_access,
            
            # Sentencias
            'ASIGNACION': self._gen_assignment,
            'DECLARACION': self._gen_declaration,
            'SI': self._gen_if,
            'MIENTRAS': self._gen_while,
            'PARA': self._gen_for,
            'HACER_MIENTRAS': self._gen_do_while,
            'RETORNO': self._gen_return,
            'FUNCION': self._gen_function,
            'PROGRAMA': self._gen_program,
            'BLOQUE': self._gen_block,
            'IMPRIMIR': self._gen_print,
            'LEER': self._gen_read,
            'BREAK': self._gen_break,
            'CONTINUE': self._gen_continue,
        }
        
        handler = handlers.get(node.tipo)
        if handler:
            return handler(node)
        else:
            print(f"Advertencia: Tipo de nodo no soportado: {node.tipo}")
            return None
    
    def _gen_literal(self, node):
        """Genera código para un literal"""
        return node.valor
    
    def _gen_identifier(self, node):
        """Genera código para un identificador"""
        return node.valor
    
    def _gen_binary_op(self, node):
        """Genera código para una operación binaria"""
        if len(node.hijos) < 2:
            return None
        
        left = self.generate(node.hijos[0])
        right = self.generate(node.hijos[1])
        temp = self.new_temp()
        
        self.emit(node.valor, left, right, temp)
        return temp
    
    def _gen_unary_op(self, node):
        """Genera código para una operación unaria"""
        if len(node.hijos) < 1:
            return None
        
        operand = self.generate(node.hijos[0])
        temp = self.new_temp()
        
        if node.valor == '-':
            self.emit('UNARY_MINUS', operand, None, temp)
        elif node.valor in ['!', 'NOT']:
            self.emit('NOT', operand, None, temp)
        else:
            self.emit(node.valor, operand, None, temp)
        
        return temp
    
    def _gen_assignment(self, node):
        """Genera código para una asignación"""
        if len(node.hijos) < 2:
            return None
        
        # El primer hijo es el lado izquierdo (variable o acceso a arreglo)
        lhs = node.hijos[0]
        # El segundo hijo es la expresión del lado derecho
        rhs_value = self.generate(node.hijos[1])
        
        if lhs.tipo == 'ACCESO_ARREGLO':
            # Asignación a un elemento de arreglo
            array_name = lhs.hijos[0].valor
            index = self.generate(lhs.hijos[1])
            self.emit('ARRAY_ASSIGN', index, rhs_value, array_name)
        else:
            # Asignación simple
            var_name = lhs.valor
            self.emit('=', rhs_value, None, var_name)
        
        return rhs_value
    
    def _gen_declaration(self, node):
        """Genera código para una declaración (con o sin inicialización)"""
        if not node.hijos:
            return None
        
        var_name = node.hijos[0].valor
        
        # Si hay inicialización
        if len(node.hijos) > 1:
            init_value = self.generate(node.hijos[1])
            self.emit('=', init_value, None, var_name)
        
        return None
    
    def _gen_if(self, node):
        """Genera código para una sentencia if"""
        if len(node.hijos) < 2:
            return None
        
        condition = self.generate(node.hijos[0])
        label_else = self.new_label()
        label_end = self.new_label()
        
        # Si la condición es falsa, saltar a else (o fin)
        self.emit('IF_FALSE', condition, None, label_else)
        
        # Código del bloque then
        self.generate(node.hijos[1])
        
        # Si hay bloque else
        if len(node.hijos) > 2:
            self.emit('GOTO', None, None, label_end)
            self.emit('LABEL', None, None, label_else)
            self.generate(node.hijos[2])
            self.emit('LABEL', None, None, label_end)
        else:
            self.emit('LABEL', None, None, label_else)
        
        return None
    
    def _gen_while(self, node):
        """Genera código para un ciclo while"""
        if len(node.hijos) < 2:
            return None
        
        label_start = self.new_label()
        label_end = self.new_label()
        
        # Guardar etiquetas para break y continue
        old_break = getattr(self, 'break_label', None)
        old_continue = getattr(self, 'continue_label', None)
        self.break_label = label_end
        self.continue_label = label_start
        
        # Etiqueta de inicio del ciclo
        self.emit('LABEL', None, None, label_start)
        
        # Evaluar condición
        condition = self.generate(node.hijos[0])
        self.emit('IF_FALSE', condition, None, label_end)
        
        # Cuerpo del ciclo
        self.generate(node.hijos[1])
        
        # Saltar al inicio
        self.emit('GOTO', None, None, label_start)
        
        # Etiqueta de fin
        self.emit('LABEL', None, None, label_end)
        
        # Restaurar etiquetas
        self.break_label = old_break
        self.continue_label = old_continue
        
        return None
    
    def _gen_do_while(self, node):
        """Genera código para un ciclo do-while"""
        if len(node.hijos) < 2:
            return None
        
        label_start = self.new_label()
        label_end = self.new_label()
        
        old_break = getattr(self, 'break_label', None)
        old_continue = getattr(self, 'continue_label', None)
        self.break_label = label_end
        self.continue_label = label_start
        
        # Etiqueta de inicio
        self.emit('LABEL', None, None, label_start)
        
        # Cuerpo del ciclo (se ejecuta primero)
        self.generate(node.hijos[0])
        
        # Evaluar condición
        condition = self.generate(node.hijos[1])
        self.emit('IF_TRUE', condition, None, label_start)
        
        # Etiqueta de fin
        self.emit('LABEL', None, None, label_end)
        
        self.break_label = old_break
        self.continue_label = old_continue
        
        return None
    
    def _gen_for(self, node):
        """Genera código para un ciclo for"""
        if len(node.hijos) < 4:
            return None
        
        # Inicialización
        self.generate(node.hijos[0])
        
        label_start = self.new_label()
        label_end = self.new_label()
        label_increment = self.new_label()
        
        old_break = getattr(self, 'break_label', None)
        old_continue = getattr(self, 'continue_label', None)
        self.break_label = label_end
        self.continue_label = label_increment
        
        # Etiqueta de inicio
        self.emit('LABEL', None, None, label_start)
        
        # Condición
        condition = self.generate(node.hijos[1])
        self.emit('IF_FALSE', condition, None, label_end)
        
        # Cuerpo del ciclo
        self.generate(node.hijos[3])
        
        # Etiqueta de incremento
        self.emit('LABEL', None, None, label_increment)
        
        # Incremento
        self.generate(node.hijos[2])
        
        # Saltar al inicio
        self.emit('GOTO', None, None, label_start)
        
        # Etiqueta de fin
        self.emit('LABEL', None, None, label_end)
        
        self.break_label = old_break
        self.continue_label = old_continue
        
        return None
    
    def _gen_break(self, node):
        """Genera código para break"""
        if hasattr(self, 'break_label'):
            self.emit('GOTO', None, None, self.break_label)
        return None
    
    def _gen_continue(self, node):
        """Genera código para continue"""
        if hasattr(self, 'continue_label'):
            self.emit('GOTO', None, None, self.continue_label)
        return None
    
    def _gen_return(self, node):
        """Genera código para return"""
        if node.hijos:
            value = self.generate(node.hijos[0])
            self.emit('RETURN', value)
        else:
            self.emit('RETURN')
        return None
    
    def _gen_function_call(self, node):
        """Genera código para una llamada a función"""
        func_name = node.valor
        
        # Generar código para los argumentos
        if node.hijos:
            for arg in node.hijos:
                arg_temp = self.generate(arg)
                self.emit('PARAM', arg_temp)
        
        # Llamada a función
        temp = self.new_temp()
        num_params = len(node.hijos) if node.hijos else 0
        self.emit('CALL', func_name, num_params, temp)
        return temp
    
    def _gen_array_access(self, node):
        """Genera código para acceso a arreglo"""
        if len(node.hijos) < 2:
            return None
        
        array_name = node.hijos[0].valor
        index = self.generate(node.hijos[1])
        temp = self.new_temp()
        self.emit('ARRAY_ACCESS', array_name, index, temp)
        return temp
    
    def _gen_function(self, node):
        """Genera código para una función"""
        if not node.hijos:
            return None
        
        func_name = node.valor
        self.current_function = func_name
        
        # Etiqueta de inicio de función
        func_label = f"FUNC_{func_name}"
        self.emit('LABEL', None, None, func_label)
        
        # Generar código para el cuerpo de la función
        # Asumiendo que el cuerpo es el último hijo
        body = node.hijos[-1]
        self.generate(body)
        
        # Si no hay return explícito, agregar uno
        if not self.code or self.code[-1].op != 'RETURN':
            self.emit('RETURN')
        
        self.current_function = None
        return None
    
    def _gen_block(self, node):
        """Genera código para un bloque de sentencias"""
        for hijo in node.hijos:
            self.generate(hijo)
        return None
    
    def _gen_program(self, node):
        """Genera código para todo el programa"""
        for hijo in node.hijos:
            self.generate(hijo)
        return None
    
    def _gen_print(self, node):
        """Genera código para una sentencia de impresión"""
        if node.hijos:
            value = self.generate(node.hijos[0])
            self.emit('PRINT', value)
        return None
    
    def _gen_read(self, node):
        """Genera código para una sentencia de lectura"""
        if node.hijos:
            var_name = node.hijos[0].valor
            self.emit('READ', None, None, var_name)
        return None
    
    def print_code(self):
        """Imprime el código generado"""
        print("\n" + "="*50)
        print("CÓDIGO INTERMEDIO DE TRES DIRECCIONES")
        print("="*50 + "\n")
        for i, instr in enumerate(self.code):
            print(f"{i:4d}: {instr}")
        print("\n" + "="*50 + "\n")
    
    def get_code(self):
        """Retorna el código generado"""
        return self.code
    
    def save_to_file(self, filename):
        """Guarda el código generado en un archivo"""
        with open(filename, 'w', encoding='utf-8') as f:
            for i, instr in enumerate(self.code):
                f.write(f"{i:d}: {instr}\n")


# Ejemplo de uso
if __name__ == "__main__":
    # Crear un AST de ejemplo
    # Programa: x = 5 + 3; y = x * 2; if (y > 10) { result = 1; } else { result = 0; }
    
    programa = ASTNode('PROGRAMA')
    
    # x = 5 + 3
    asig1 = ASTNode('ASIGNACION')
    asig1.agregar_hijo(ASTNode('IDENTIFICADOR', 'x'))
    suma = ASTNode('OPERACION_BINARIA', '+')
    suma.agregar_hijo(ASTNode('NUMERO', 5))
    suma.agregar_hijo(ASTNode('NUMERO', 3))
    asig1.agregar_hijo(suma)
    programa.agregar_hijo(asig1)
    
    # y = x * 2
    asig2 = ASTNode('ASIGNACION')
    asig2.agregar_hijo(ASTNode('IDENTIFICADOR', 'y'))
    mult = ASTNode('OPERACION_BINARIA', '*')
    mult.agregar_hijo(ASTNode('IDENTIFICADOR', 'x'))
    mult.agregar_hijo(ASTNode('NUMERO', 2))
    asig2.agregar_hijo(mult)
    programa.agregar_hijo(asig2)
    
    # if (y > 10) { result = 1; } else { result = 0; }
    if_node = ASTNode('SI')
    condicion = ASTNode('OPERACION_BINARIA', '>')
    condicion.agregar_hijo(ASTNode('IDENTIFICADOR', 'y'))
    condicion.agregar_hijo(ASTNode('NUMERO', 10))
    if_node.agregar_hijo(condicion)
    
    # Bloque then
    then_block = ASTNode('BLOQUE')
    asig_then = ASTNode('ASIGNACION')
    asig_then.agregar_hijo(ASTNode('IDENTIFICADOR', 'result'))
    asig_then.agregar_hijo(ASTNode('NUMERO', 1))
    then_block.agregar_hijo(asig_then)
    if_node.agregar_hijo(then_block)
    
    # Bloque else
    else_block = ASTNode('BLOQUE')
    asig_else = ASTNode('ASIGNACION')
    asig_else.agregar_hijo(ASTNode('IDENTIFICADOR', 'result'))
    asig_else.agregar_hijo(ASTNode('NUMERO', 0))
    else_block.agregar_hijo(asig_else)
    if_node.agregar_hijo(else_block)
    
    programa.agregar_hijo(if_node)
    
    # Generar código intermedio
    generator = IntermediateCodeGenerator()
    generator.generate(programa)
    generator.print_code()
    
    # Opcionalmente, guardar en archivo
    generator.save_to_file('codigo_intermedio.txt')