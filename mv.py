class VirtualMachine:
    def __init__(self, input_handler=input, output_handler=print):
        self.memory = {}
        self.instructions = []
        self.labels = {}
        self.pc = 0
        self.input_handler = input_handler
        self.output_handler = output_handler

    def run(self, code_list):
        # 1. Limpiar líneas vacías
        self.instructions = [line.strip() for line in code_list if line.strip()]
        self.memory = {}
        self.pc = 0
        self.labels = {}
        
        # 2. Pre-escaneo de etiquetas
        for i, line in enumerate(self.instructions):
            if line.startswith("LABEL "):
                parts = line.split()
                if len(parts) >= 2:
                    label_name = parts[1]
                    self.labels[label_name] = i

        # 3. Ciclo de ejecución
        while self.pc < len(self.instructions):
            try:
                self.execute_instruction(self.instructions[self.pc].strip())
            except Exception as e:
                self.output_handler(f"Error en tiempo de ejecución (Línea {self.pc}): {e}\n")
                break
            
    def get_value(self, val_str):
        """Obtiene el valor de un literal o variable"""
        val_str = val_str.strip()
        
        # Literal Cadena
        if val_str.startswith('"') and val_str.endswith('"'):
            return val_str[1:-1]
        
        # Booleanos
        if val_str.lower() == "true":
            return True
        if val_str.lower() == "false":
            return False
            
        # Literal Numérico
        try:
            if '.' in val_str:
                return float(val_str)
            clean_val = val_str.lstrip('-+')
            if clean_val.isdigit():
                return int(val_str)
        except (ValueError, AttributeError):
            pass
            
        # Variable (incluye temporales)
        if val_str in self.memory:
            return self.memory[val_str]
        
        print(f"Advertencia: Variable '{val_str}' no encontrada en memoria, usando 0")
        return 0
        
    def execute_instruction(self, line):
        if line == "START" or line == "END" or line.startswith("LABEL "):
            self.pc += 1
            return

        # --- SALIDA ---
        if line.startswith("PRINT "):
            content = line[6:].strip()
            
            parts = []
            current = ""
            in_string = False
            
            for char in content:
                if char == '"':
                    in_string = not in_string
                    current += char
                elif char == ' ' and not in_string:
                    if current.strip():
                        parts.append(current.strip())
                    current = ""
                else:
                    current += char
            
            if current.strip():
                parts.append(current.strip())
            
            output = ""
            for part in parts:
                val = self.get_value(part)
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                output += str(val)
            
            self.output_handler(output + "\n")
            self.pc += 1
            return

        # --- ENTRADA ---
        if line.startswith("READ "):
            # READ var_name [mensaje] [tipo]
            content = line[5:].strip()

            # --- PARSER para dividir respetando strings ---
            parts = []
            current = ""
            in_string = False

            for char in content:
                if char == '"':
                    in_string = not in_string
                    current += char
                elif char == ' ' and not in_string:
                    if current.strip():
                        parts.append(current.strip())
                    current = ""
                else:
                    current += char

            if current.strip():
                parts.append(current.strip())

            # parts = [var_name, (mensaje opcional), (tipo opcional)]
            var_name = parts[0]

            # ---------------- MENSAJE ----------------
            mensaje = ""
            input_type = "string"  # default

            # 2 o más parámetros: ver si el último es un tipo válido
            valid_types = ["int", "float", "bool", "string"]

            if len(parts) >= 2:
                # ¿Es tipo válido el último parámetro?
                last = parts[-1].lower()
                if last in valid_types:
                    input_type = last
                    msg_parts = parts[1:-1]  # lo que queda es el mensaje
                else:
                    msg_parts = parts[1:]    # todo es mensaje
                
                # reconstruir mensaje (sin comillas)
                if msg_parts:
                    mensaje = " ".join(msg_parts)
                    if mensaje.startswith('"') and mensaje.endswith('"'):
                        mensaje = mensaje[1:-1]
            
            # Si no hay mensaje
            if mensaje == "":
                prompt = f"{var_name}: "
            else:
                prompt = mensaje + " "

            # ---------------- PEDIR INPUT ----------------
            user_input = self.input_handler(prompt)

            if user_input is None:
                raise Exception("Entrada cancelada por el usuario.")

            # ---------------- VALIDAR SEGÚN TIPO ----------------
            def error_tipo():
                raise Exception(f"Error: '{user_input}' no coincide con el tipo esperado '{input_type}'.")

            if input_type == "int":
                if "." in user_input:
                    error_tipo()
                if not user_input.lstrip("-").isdigit():
                    error_tipo()
                val = int(user_input)

            elif input_type == "float":
                try:
                    val = float(user_input)
                except:
                    error_tipo()

            elif input_type == "bool":
                if user_input not in ["0", "1"]:
                    error_tipo()
                val = True if user_input == "1" else False

            elif input_type == "string":
                # Se guarda tal cual
                val = user_input

            # ---------------- GUARDAR Y CONTINUAR ----------------
            self.memory[var_name] = val
            self.pc += 1
            return

        # --- SALTOS ---
        if line.startswith("GOTO "):
            label = line[5:].strip()
            if label in self.labels:
                self.pc = self.labels[label]
            else:
                raise Exception(f"Etiqueta no encontrada: {label}")
            return

        if line.startswith("IF_FALSE "):
            parts = line.split()
            if len(parts) < 4:
                raise Exception(f"Instrucción IF_FALSE mal formada: {line}")
            
            cond_var = parts[1]
            label = parts[3]
            
            cond_val = self.get_value(cond_var)
            
            if not cond_val: 
                if label in self.labels:
                    self.pc = self.labels[label]
                else:
                    raise Exception(f"Etiqueta no encontrada: {label}")
            else:
                self.pc += 1
            return

        # --- ASIGNACIONES Y OPERACIONES ---
        if "=" in line:
            parts = line.split("=", 1)
            target = parts[0].strip()
            expr = parts[1].strip()
            
            expr_parts = expr.split()
            
            # NUEVO: Detectar conversión TO_INT
            if len(expr_parts) == 2 and expr_parts[0] == "TO_INT":
                # Formato: variable = TO_INT valor
                val = self.get_value(expr_parts[1])
                # Convertir a int (truncar si es float)
                if isinstance(val, float):
                    res = int(val)
                elif isinstance(val, str):
                    try:
                        res = int(float(val))
                    except:
                        res = 0
                else:
                    res = int(val)
                
                self.memory[target] = res
            
            elif len(expr_parts) == 3:
                # Operación binaria: v1 op v2
                v1_str = expr_parts[0]
                op = expr_parts[1]
                v2_str = expr_parts[2]
                
                v1 = self.get_value(v1_str)
                v2 = self.get_value(v2_str)
                
                res = self.compute_op(v1, op, v2)
                
                self.memory[target] = res
            
            elif len(expr_parts) == 1:
                # Asignación simple: target = valor
                val = self.get_value(expr_parts[0])
                self.memory[target] = val
            
            else:
                # Expresión compleja
                try:
                    val = self.get_value(expr.strip())
                    self.memory[target] = val
                except:
                    raise Exception(f"No se pudo evaluar la expresión: {expr}")
                 
            self.pc += 1
            return
            
        self.pc += 1

    def compute_op(self, v1, op, v2):
        """Realiza operaciones aritméticas, lógicas y de comparación"""
        try:
            # Operaciones aritméticas
            if op == '+':
                if isinstance(v1, str) or isinstance(v2, str):
                    return str(v1) + str(v2)
                return v1 + v2
            if op == '-': 
                return v1 - v2
            if op == '*': 
                return v1 * v2
            if op == '/':
                if v2 == 0:
                    raise Exception("División por cero")
                # IMPORTANTE: División normal (puede retornar float)
                # La conversión a int se hace con TO_INT si es necesario
                return v1 / v2
            if op == '%': 
                return v1 % v2
            if op == '^': 
                return v1 ** v2
            
            # Operaciones de comparación
            if op == '>': 
                return v1 > v2
            if op == '<': 
                return v1 < v2
            if op == '>=': 
                return v1 >= v2
            if op == '<=': 
                return v1 <= v2
            if op == '==': 
                return v1 == v2
            if op == '!=': 
                return v1 != v2
            
            # Operaciones lógicas
            if op == '&&': 
                return bool(v1) and bool(v2)
            if op == '||': 
                return bool(v1) or bool(v2)
            
            raise Exception(f"Operador desconocido: {op}")
            
        except ZeroDivisionError:
            raise Exception("División por cero")
        except Exception as e:
            raise Exception(f"Error en operación '{v1} {op} {v2}': {e}")