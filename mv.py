class VirtualMachine:
    def __init__(self, input_handler=input, output_handler=print):
        self.memory = {}
        self.instructions = []
        self.labels = {}
        self.pc = 0 # Program Counter
        self.input_handler = input_handler
        self.output_handler = output_handler

    def run(self, code_list):
        # 1. Limpiar líneas vacías
        self.instructions = [line.strip() for line in code_list if line.strip()]
        self.memory = {}
        self.pc = 0
        self.labels = {}
        
        # 2. Pre-escaneo de etiquetas (ANTES de ejecutar nada)
        for i, line in enumerate(self.instructions):
            if line.startswith("LABEL "):
                parts = line.split()
                if len(parts) >= 2:
                    label_name = parts[1]
                    self.labels[label_name] = i
                    # Debug: mostrar etiquetas encontradas
                    print(f"DEBUG: Etiqueta '{label_name}' en índice {i}")

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
            
        # Literal Numérico (intentar primero antes de buscar en memoria)
        try:
            # Verificar si tiene punto decimal
            if '.' in val_str:
                return float(val_str)
            # Verificar si es un número entero (positivo o negativo)
            # Usar isdigit() después de quitar el signo
            clean_val = val_str.lstrip('-+')
            if clean_val.isdigit():
                return int(val_str)
        except (ValueError, AttributeError):
            pass
            
        # Variable (incluye temporales como t1, t2, etc.)
        if val_str in self.memory:
            return self.memory[val_str]
        
        # Si es una variable que no existe, retornar 0 por defecto
        # (esto puede pasar con variables no inicializadas)
        # Pero mostrar advertencia
        print(f"Advertencia: Variable '{val_str}' no encontrada en memoria, usando 0")
        return 0
        
    def execute_instruction(self, line):
        if line == "START" or line == "END" or line.startswith("LABEL "):
            self.pc += 1
            return

        # --- SALIDA ---
        if line.startswith("PRINT "):
            # Formato: PRINT <valor1> <valor2> <valor3> ...
            # Ejemplo: PRINT "Hola" x "mundo" t1
            content = line[6:].strip()
            
            # Procesar argumentos respetando cadenas entre comillas
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
            
            # Procesar cada parte y concatenar en una sola línea
            output = ""
            for part in parts:
                val = self.get_value(part)
                # Si es un número float que termina en .0, mostrarlo como entero
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                output += str(val)
            
            self.output_handler(output + "\n")
            self.pc += 1
            return

        # --- ENTRADA ---
        if line.startswith("READ "):
            # Formato: READ <variable> [mensaje opcional]
            # Ejemplo: READ x o READ x "Ingrese x: "
            content = line[5:].strip()
            
            # Dividir por espacios, respetando cadenas entre comillas
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
            
            # Primera parte es el nombre de la variable
            var_name = parts[0]
            
            # Si hay más partes, es el mensaje personalizado
            if len(parts) > 1:
                # Unir el resto como mensaje
                mensaje = ' '.join(parts[1:])
                # Limpiar comillas
                if mensaje.startswith('"') and mensaje.endswith('"'):
                    mensaje = mensaje[1:-1]
                # Si hay mensaje personalizado, usar SOLO ese mensaje (sin agregar el nombre de la variable)
                prompt = mensaje
            else:
                # Mensaje por defecto más amigable (solo si NO hay mensaje personalizado)
                prompt = f"{var_name}: "
            
            # Solicitar input
            user_input = self.input_handler(prompt)
            
            if user_input is None: # Usuario canceló
                raise Exception("Entrada cancelada por el usuario.")

            # Intentar convertir a número
            try:
                if '.' in user_input:
                    val = float(user_input)
                else:
                    val = int(user_input)
            except:
                val = user_input # Mantener como string si falla
                
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
            # Formato: IF_FALSE <cond> GOTO <label>
            parts = line.split()
            # parts[0]=IF_FALSE, parts[1]=var_cond, parts[2]=GOTO, parts[3]=label
            if len(parts) < 4:
                raise Exception(f"Instrucción IF_FALSE mal formada: {line}")
            
            cond_var = parts[1]
            label = parts[3]
            
            cond_val = self.get_value(cond_var)
            
            # Si es falso (False, 0, None), saltamos
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
            # Formato: target = op1 [operador binario] op2
            # O: target = valor
            parts = line.split("=", 1)
            target = parts[0].strip()
            expr = parts[1].strip()
            
            # Dividir la expresión por espacios
            expr_parts = expr.split()
            
            if len(expr_parts) == 3:  # Operación binaria: v1 op v2
                v1_str = expr_parts[0]
                op = expr_parts[1]
                v2_str = expr_parts[2]
                
                # Obtener valores (esto ahora busca en memoria correctamente)
                v1 = self.get_value(v1_str)
                v2 = self.get_value(v2_str)
                
                # Debug: Mostrar valores obtenidos
                # print(f"Debug: {v1_str}={v1}, {v2_str}={v2}")
                
                # Realizar operación
                res = self.compute_op(v1, op, v2)
                
                # Guardar resultado en memoria
                self.memory[target] = res
                
                # Debug: Mostrar resultado
                # print(f"Debug: {target} = {res}")
            
            elif len(expr_parts) == 1:  # Asignación simple: target = valor
                val = self.get_value(expr_parts[0])
                self.memory[target] = val
                # print(f"Debug: {target} = {val}")
            
            else:
                # Expresión compleja o mal formada
                # Intentar evaluar como está
                try:
                    val = self.get_value(expr.strip())
                    self.memory[target] = val
                except:
                    raise Exception(f"No se pudo evaluar la expresión: {expr}")
                 
            self.pc += 1
            return
            
        # Si llegamos aquí, instrucción desconocida
        self.pc += 1

    def compute_op(self, v1, op, v2):
        """Realiza operaciones aritméticas, lógicas y de comparación"""
        try:
            # Operaciones aritméticas
            if op == '+':
                # Permitir concatenación de strings
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
            
            # Operador desconocido
            raise Exception(f"Operador desconocido: {op}")
            
        except ZeroDivisionError:
            raise Exception("División por cero")
        except Exception as e:
            raise Exception(f"Error en operación '{v1} {op} {v2}': {e}")