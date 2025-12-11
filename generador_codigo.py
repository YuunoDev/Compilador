from AnSem import ASTNode, DataType

class IntermediateCodeGenerator:
    def __init__(self):
        self.code = []          # Lista de instrucciones generadas
        self.temp_counter = 0   # Contador para variables temporales (t1, t2...)
        self.label_counter = 0  # Contador para etiquetas (L1, L2...)

    def generate(self, node):
        """Genera código intermedio a partir del AST"""
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
        if node:
            self.visit(node)
        return self.code

    def new_temp(self):
        """Genera una nueva variable temporal."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        """Genera una nueva etiqueta."""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, instruction):
        """Agrega una instrucción a la lista."""
        self.code.append(instruction)

    def visit(self, node):
        """Visita un nodo del AST y llama al método correspondiente"""
        if not isinstance(node, ASTNode):
            return None

        # Normalizar y obtener tanto tipo como posible lexema/valor
        raw_tipo = str(node.tipo) if hasattr(node, 'tipo') and node.tipo is not None else ""
        raw_valor = str(node.valor) if hasattr(node, 'valor') and node.valor is not None else ""

        node_type = raw_tipo.lower().strip().replace(" ", "")
        node_val = raw_valor.strip()

        """quitar de las operaciones el (x), ejemplo +(x) -> +"""
        if node_type.endswith(")") and "(" in node_type:
            node_type = node_type[:node_type.index("(")]
        if node_val.endswith(")") and "(" in node_val:
            node_val = node_val[:node_val.index("(")]
        #print("Cleaned node_type:", node_type, "node_val:", node_val)

        # Detectar operadores por símbolo ya sea en tipo o en valor
        if node_type in ["+","-","*","/","%"] or node_val in ["+","-","*","/","%"]:
            method_name = 'visit_operacion'
        elif node_type in [">","<",">=","<=","==","!="] or node_val in [">","<",">=","<=","==","!="]:
            method_name = 'visit_operacioncomparacion'
        elif node_type in ["&&","||"] or node_val in ["&&","||"]:
            method_name = 'visit_operacionlogica'
        else:
            # Normal fallback: construir nombre de método a partir del tipo
            method_name = f'visit_{node_type}'

        # Debug temporal (borra o comenta cuando ya funcione)
        # print(f"DEBUG visit: tipo='{raw_tipo}' valor='{raw_valor}' -> método {method_name}")

        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)


    def generic_visit(self, node):
        """Visita genérica para nodos sin método específico"""
        for child in node.hijos:
            self.visit(child)
        return None

    # --- PROGRAMA Y BLOQUES ---
    def visit_programa(self, node):
        """Visita el nodo raíz del programa"""
        self.emit("START")
        for child in node.hijos:
            self.visit(child)
        self.emit("END")

    def visit_raiz(self, node):
        """Visita el nodo raíz (alternativo)"""
        self.emit("START")
        for child in node.hijos:
            self.visit(child)
        self.emit("END")

    # --- DECLARACIONES ---
    def visit_declaracion(self, node):
        """Genera código para declaración de variables solo si tiene una asignación"""
        #print("Declaracion node con menos de 2 hijos:", node.hijos)

        if len(node.hijos) <= 2:
            return
        
        # Obtener identificador y expresión
        id_node = node.hijos[1]
        expr_node = node.hijos[2]
        
        # El identificador puede ser un nodo con id o valor
        identificador = id_node.id if hasattr(id_node, 'id') and id_node.id else id_node.valor
        #print("Identificador declarado:", identificador)
        # Calcular el valor de la expresión
        expr_temp = self.visit(expr_node)
        
        # Generar la declaración con asignación
        if expr_temp:
            self.emit(f"{identificador} = {expr_temp}")
        else:
            # Si la expresión no retorna temporal, obtener el valor del nodo
            valor = self._get_node_value(expr_node)
            if valor:
                self.emit(f"{identificador} = {valor}")

    # --- ASIGNACIÓN ---
    def visit_asignacion(self, node):
        """Genera código para asignación: id = expresion"""

        if len(node.hijos) < 2:
            return
        
        # Obtener identificador y expresión
        id_node = node.hijos[0]
        expr_node = node.hijos[1]
        
        # El identificador puede ser un nodo con id o valor
        identificador = id_node.id if hasattr(id_node, 'id') and id_node.id else id_node.valor
        
        # Calcular el valor de la expresión
        expr_temp = self.visit(expr_node)
        
        # Generar la asignación
        if expr_temp:
            self.emit(f"{identificador} = {expr_temp}")
        else:
            # Si la expresión no retorna temporal, obtener el valor del nodo
            valor = self._get_node_value(expr_node)
            if valor:
                self.emit(f"{identificador} = {valor}")

    # --- ENTRADA / SALIDA ---
    def visit_cin(self, node):
        """Genera código para entrada: cin >> id con mensaje opcional"""
        if not node.hijos:
            return
        
        # Procesar múltiples argumentos (pueden ser identificadores o cadenas)
        mensaje_partes = []
        id_nodo = None
        
        for hijo in node.hijos:
            if hasattr(hijo, 'tipo') and hijo.tipo == "cadena":
                # Es una cadena de mensaje
                valor = hijo.valor if hasattr(hijo, 'valor') else hijo.id
                valor_str = str(valor)
                if not (valor_str.startswith('"') and valor_str.endswith('"')):
                    valor_str = f'"{valor_str}"'
                mensaje_partes.append(valor_str)
            else:
                # Es el identificador (puede ser tipo "ID(...)" o "identificador")
                id_nodo = hijo
        
        if id_nodo:
            # Obtener el identificador del nodo
            identificador = None
            
            # Primero intentar con el atributo 'id'
            if hasattr(id_nodo, 'id') and id_nodo.id:
                identificador = id_nodo.id
            # Luego intentar con 'valor'
            elif hasattr(id_nodo, 'valor') and id_nodo.valor:
                identificador = id_nodo.valor
            # Por último, si el tipo es "ID(...)", extraerlo
            elif hasattr(id_nodo, 'tipo') and id_nodo.tipo.startswith('ID('):
                identificador = id_nodo.tipo[3:-1]  # Extraer de "ID(x)"
            
            if identificador:
                # Si hay mensaje, incluirlo en la instrucción
                if mensaje_partes:
                    mensaje = ' '.join(mensaje_partes)
                    self.emit(f"READ {identificador} {mensaje}")
                else:
                    self.emit(f"READ {identificador}")

    def visit_cout(self, node):
        """Genera código para salida: cout << expresion (múltiples elementos en la misma línea)"""
        output_parts = []
        
        for expr_node in node.hijos:
            # Verificar si es una cadena literal
            if hasattr(expr_node, 'tipo') and expr_node.tipo == "cadena":
                # Es una cadena literal - obtener el valor directamente
                valor = expr_node.valor if hasattr(expr_node, 'valor') else expr_node.id
                valor_str = str(valor)
                # Solo agregar comillas si no las tiene
                if not (valor_str.startswith('"') and valor_str.endswith('"')):
                    valor_str = f'"{valor_str}"'
                output_parts.append(valor_str)
            else:
                # Es una expresión, identificador o valor
                result_temp = self.visit(expr_node)
                if result_temp:
                    output_parts.append(result_temp)
                else:
                    # Intentar obtener valor directo del nodo
                    valor = self._get_node_value(expr_node)
                    if valor:
                        output_parts.append(valor)
        
        # Emitir una sola instrucción PRINT con todos los argumentos separados por espacios
        if output_parts:
            self.emit(f"PRINT {' '.join(output_parts)}")

    # --- EXPRESIONES ---
    def _visit_binary_op(self, node, op):
        if len(node.hijos) < 2:
            return None

        # Visitar hijos izquierdo y derecho (intentar generar temporales)
        #print("hijos de operacion:", node.hijos)
        left_temp = self.visit(node.hijos[0])
        right_temp = self.visit(node.hijos[1])


        # Si la visita devolvió None, intentar obtener valor directo
        if left_temp is None:
            left_temp = self._get_node_value(node.hijos[0])
        if right_temp is None:
            right_temp = self._get_node_value(node.hijos[1])

        # Si aún no hay operandos válidos, abortar
        if left_temp is None or right_temp is None:
            return None

        # Crear temporal para el resultado
        result_temp = self.new_temp()

        # Emitir instrucción (asegurarse de que op sea el símbolo correcto)
        op_sym = op if isinstance(op, str) and op.strip() else node.tipo

        # quitar ()
        if op_sym.endswith(")") and "(" in op_sym:
            op_sym = op_sym[:op_sym.index("(")]

        self.emit(f"{result_temp} = {left_temp} {op_sym} {right_temp}")

        return result_temp


    def _get_node_value(self, node):
        """Obtiene el valor de un nodo (número, identificador, etc)"""
        # CORRECCIÓN PRINCIPAL: Primero verificar si tiene 'id' (para identificadores)
        if hasattr(node, 'id') and node.id:
            id_val = str(node.id)
            # Limpiar formato ID(x)
            if id_val.startswith('ID(') and id_val.endswith(')'):
                return id_val[3:-1]
            elif id_val.startswith('id(') and id_val.endswith(')'):
                return id_val[3:-1]
            return id_val
        
        # Luego verificar si tiene 'valor'
        if hasattr(node, 'valor') and node.valor is not None:
            # Si el valor es una cadena que representa el tipo de nodo (como "id(x)"),
            # extraer solo el identificador
            valor_str = str(node.valor)
            if valor_str.startswith('id(') and valor_str.endswith(')'):
                return valor_str[3:-1]
            elif valor_str.startswith('ID(') and valor_str.endswith(')'):
                return valor_str[3:-1]
            return valor_str
        
        # Si el tipo del nodo empieza con "id(" o "ID(", extraer el identificador
        if hasattr(node, 'tipo') and node.tipo:
            tipo_str = str(node.tipo)
            if tipo_str.startswith('id(') and tipo_str.endswith(')'):
                return tipo_str[3:-1]
            elif tipo_str.startswith('ID(') and tipo_str.endswith(')'):
                return tipo_str[3:-1]
            # Si el tipo es un tipo de dato básico, intentar obtener el valor
            if tipo_str in ['entero', 'flotante', 'cadena', 'booleano']:
                if hasattr(node, 'valor'):
                    return str(node.valor)
        
        return None

    def visit_operacion(self, node):
        """Visita operaciones aritméticas (+, -, *, /, %)"""
        op = node.tipo if hasattr(node, 'tipo') else '+'
        return self._visit_binary_op(node, op)

    def visit_operacioncomparacion(self, node):
        """Visita operaciones de comparación (>, <, ==, etc)"""
        op = node.tipo if hasattr(node, 'tipo') else '=='
        return self._visit_binary_op(node, op)

    def visit_operacionlogica(self, node):
        """Visita operaciones lógicas (&&, ||)"""
        op = node.tipo if hasattr(node, 'tipo') else '&&'
        return self._visit_binary_op(node, op)

    # --- INCREMENTO / DECREMENTO ---
    def visit_incremento(self, node):
        """Genera código para incremento: x++
            incremento ++
                ID(x)   
                asignacion
                    ID(x)
                    +(1)
                        ID(x)
                        entero
        """
        #print("Incremento node:", node)
        if node.hijos and node.hijos[1].hijos:
            id_node = node.hijos[1].hijos[0]  # x++ -> asignacion -> id
            identificador = id_node.id if hasattr(id_node, 'id') and id_node.id else id_node.valor
            self.emit(f"{identificador} = {identificador} + 1")

    def visit_decremento(self, node):
        """Genera código para decremento: x--"""
        if node.hijos and node.hijos[1].hijos:
            id_node = node.hijos[1].hijos[0]  # x-- -> asignacion -> id
            identificador = id_node.id if hasattr(id_node, 'id') and id_node.id else id_node.valor
            self.emit(f"{identificador} = {identificador} - 1")

    # --- VALORES BASE (Hojas) ---
    def visit_entero(self, node):
        """Retorna el valor de un número entero"""
        if hasattr(node, 'valor') and node.valor is not None:
            return str(node.valor)
        return "0"

    def visit_flotante(self, node):
        """Retorna el valor de un número flotante"""
        if hasattr(node, 'valor') and node.valor is not None:
            return str(node.valor)
        return "0.0"

    def visit_cadena(self, node):
        """Retorna el valor de una cadena"""
        if hasattr(node, 'valor') and node.valor is not None:
            valor = str(node.valor)
            # Asegurarse de que tenga comillas
            if not valor.startswith('"'):
                valor = f'"{valor}"'
            return valor
        return '""'

    def visit_booleano(self, node):
        """Retorna el valor de un booleano"""
        if hasattr(node, 'valor') and node.valor is not None:
            valor = str(node.valor).lower()
            return "true" if valor in ["true", "1", "verdadero"] else "false"
        return "false"

    def visit_identificador(self, node):
        """Retorna el nombre de un identificador"""
        # CORRECCIÓN: Usar 'id' en lugar de 'valor' para identificadores
        identificador = None
        
        # Intentar obtener de 'id' primero
        if hasattr(node, 'id') and node.id:
            identificador = node.id
        # Luego intentar con 'valor'
        elif hasattr(node, 'valor') and node.valor:
            identificador = node.valor
        # Por último, intentar extraer del tipo
        elif hasattr(node, 'tipo') and node.tipo:
            identificador = node.tipo
        
        if identificador is None:
            return None
        
        # Limpiar el identificador si viene en formato especial
        identificador = str(identificador)
        
        # Si el identificador viene como "id(x)" o "ID(x)", extraer solo 'x'
        if identificador.startswith('id(') and identificador.endswith(')'):
            identificador = identificador[3:-1]
        elif identificador.startswith('ID(') and identificador.endswith(')'):
            identificador = identificador[3:-1]
        
        return identificador

    # --- ESTRUCTURAS DE CONTROL ---
    def visit_if(self, node):
        """Genera código para if-then-else"""
        if not node.hijos:
            return
        
        # Buscar nodo de condición
        condicion_node = None
        bloque_if_node = None
        bloque_else_node = None
        
        for hijo in node.hijos:
            if hijo.tipo.lower() == "condicion":
                condicion_node = hijo
            elif hijo.tipo.lower() == "bloqueif":
                bloque_if_node = hijo
            elif hijo.tipo.lower() == "bloqueelse":
                bloque_else_node = hijo
        
        if not condicion_node or not bloque_if_node:
            return
        
        has_else = bloque_else_node is not None
        
        # Generar etiqueta de salida (al final del IF)
        label_skip = self.new_label()
        
        # Evaluar condición - MEJORADO para manejar operaciones complejas
        cond_temp = None
        if condicion_node.hijos:
            # Visitar el primer hijo (puede ser una operación compleja)
            cond_temp = self.visit(condicion_node.hijos[0])
        
        # Si no se obtuvo temporal, intentar obtener valor directo
        if cond_temp is None:
            cond_temp = self._get_node_value(condicion_node)
        
        # Validar que tenemos una condición válida
        if cond_temp is None:
            raise Exception(f"No se pudo evaluar la condición en línea {condicion_node.linea}")
        
        # Salto si falso (salta el bloque THEN)
        self.emit(f"IF_FALSE {cond_temp} GOTO {label_skip}")
        
        # Bloque THEN
        for hijo in bloque_if_node.hijos:
            self.visit(hijo)
        
        # Si hay else, saltar el bloque else después del then
        if has_else:
            label_end = self.new_label()
            self.emit(f"GOTO {label_end}")
            self.emit(f"LABEL {label_skip}")
            # Bloque ELSE
            for hijo in bloque_else_node.hijos:
                self.visit(hijo)
            self.emit(f"LABEL {label_end}")
        else:
            # Sin else, la etiqueta de salto va aquí
            self.emit(f"LABEL {label_skip}")

    def visit_while(self, node):
        """Genera código para while"""
        if not node.hijos:
            return
        
        # Buscar condición y cuerpo
        condicion_node = None
        cuerpo_node = None
        
        for hijo in node.hijos:
            if hijo.tipo.lower() == "condicion":
                condicion_node = hijo
            elif hijo.tipo.lower() == "cuerpo":
                cuerpo_node = hijo
        
        if not condicion_node or not cuerpo_node:
            return
        
        label_start = self.new_label()
        label_end = self.new_label()
        
        self.emit(f"LABEL {label_start}")
        
        # Evaluar condición
        if condicion_node.hijos:
            cond_temp = self.visit(condicion_node.hijos[0])
        else:
            cond_temp = self._get_node_value(condicion_node)
        
        # Salto de salida
        self.emit(f"IF_FALSE {cond_temp} GOTO {label_end}")
        
        # Cuerpo del loop
        for hijo in cuerpo_node.hijos:
            self.visit(hijo)
        
        # Volver al inicio
        self.emit(f"GOTO {label_start}")
        
        self.emit(f"LABEL {label_end}")

    def visit_dountil(self, node):
        """Genera código para do-until"""
        if not node.hijos:
            return
        
        # Buscar condición y cuerpo
        condicion_node = None
        cuerpo_node = None
        
        for hijo in node.hijos:
            if hijo.tipo.lower() == "condicion":
                condicion_node = hijo
            elif hijo.tipo.lower() == "cuerpo":
                cuerpo_node = hijo
        
        if not condicion_node or not cuerpo_node:
            return
        
        label_start = self.new_label()
        
        self.emit(f"LABEL {label_start}")
        
        # Ejecutar cuerpo
        for hijo in cuerpo_node.hijos:
            self.visit(hijo)
        
        # Evaluar condición
        if condicion_node.hijos:
            cond_temp = self.visit(condicion_node.hijos[0])
        else:
            cond_temp = self._get_node_value(condicion_node)
        
        # Repetir si la condición es falsa (semántica until)
        self.emit(f"IF_FALSE {cond_temp} GOTO {label_start}")

    def visit_for(self, node):
        """Genera código para for
        for (init; condicion; incremento) { cuerpo }
        
        Se traduce a:
            init
            LABEL L_start
            IF_FALSE condicion GOTO L_end
            cuerpo
            incremento
            GOTO L_start
            LABEL L_end
        """
        if len(node.hijos) < 4:
            return
        
        # Buscar componentes del for
        init_node = None
        condicion_node = None
        incremento_node = None
        cuerpo_node = None
        
        for hijo in node.hijos:
            tipo_lower = hijo.tipo.lower()
            if tipo_lower == "inicializacion":
                init_node = hijo
            elif tipo_lower == "condicion":
                condicion_node = hijo
            elif tipo_lower == "incrementofor":
                incremento_node = hijo
            elif tipo_lower == "cuerpofor":
                cuerpo_node = hijo
        
        if not all([init_node, condicion_node, incremento_node, cuerpo_node]):
            return
        
        # 1. INICIALIZACIÓN (ejecutar una sola vez)
        for hijo in init_node.hijos:
            self.visit(hijo)
        
        # 2. Crear etiquetas
        label_start = self.new_label()
        label_end = self.new_label()
        
        # 3. Etiqueta de inicio del loop
        self.emit(f"LABEL {label_start}")
        
        # 4. CONDICIÓN (evaluar y saltar si es falsa)
        cond_temp = None
        if condicion_node.hijos:
            cond_temp = self.visit(condicion_node.hijos[0])
        
        if cond_temp is None:
            cond_temp = self._get_node_value(condicion_node)
        
        # Salto de salida si la condición es falsa
        self.emit(f"IF_FALSE {cond_temp} GOTO {label_end}")
        
        # 5. CUERPO del loop
        for hijo in cuerpo_node.hijos:
            self.visit(hijo)
        
        # 6. INCREMENTO (ejecutar al final de cada iteración)
        for hijo in incremento_node.hijos:
            # print("hijo incremento:", hijo.tipo)
            self.visit(hijo)
        
        # 7. Volver al inicio
        self.emit(f"GOTO {label_start}")
        
        # 8. Etiqueta de salida
        self.emit(f"LABEL {label_end}")

    def print_code(self):
        """Imprime el código generado"""
        print("\n=== CÓDIGO INTERMEDIO DE TRES DIRECCIONES ===")
        for i, instruction in enumerate(self.code, 1):
            print(f"{i:3d}: {instruction}")

    def get_code_string(self):
        """Retorna el código como string"""
        result = "=== CÓDIGO INTERMEDIO DE TRES DIRECCIONES ===\n"
        for i, instruction in enumerate(self.code, 1):
            result += f"{i:3d}: {instruction}\n"
        return result