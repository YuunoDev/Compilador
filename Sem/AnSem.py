from dataclasses import dataclass, field
import enum
from typing import Any,Optional

class ASTNode:
    def __init__(self, tipo, valor=None, linea=None, columna=None):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna
        self.hijos :ASTNode = []
        self.es_error = False
        self.tipo_dato = None  # Para almacenar el tipo de dato inferido
        self.scope = None  # Para almacenar el scope donde se define
        self.use = False
    
    def agregar_hijo(self, hijo):
        if hijo:
            self.hijos.append(hijo)
    
    def marcar_error(self):
        self.es_error = True
    
    def __repr__(self):
        return f"ASTNode({self.tipo}, {self.valor})"

class DataType(enum.Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    ERROR = "error"

#sacar tipo de operacion
def tipo_op(nodo:ASTNode)-> str:
        
        if nodo.valor == "+":
            return "suma"
        elif nodo.valor == "-":
            return "resta"
        elif nodo.valor == "*":
            return "multiplicacion"
        elif nodo.valor == "/":
            return "division"
            

# Clase para representar un símbolo en la tabla
@dataclass
class Symbol:
    name: str
    data_type: DataType
    value: Any = None
    scope: str = "global"
    lines: list[int] = field(default_factory=list)
    is_initialized: bool = False
    is_constant: bool = False

    def add(self,line):
        self.lines.append(line)

class SymbolTable:
    def __init__(self):
        self.scopes = [{}] #pila
        self.current_scope = "global"

    def insert(self, symbol: Symbol)-> bool:
        """Inserta en tabla """
        if symbol.name in self.scopes[-1]:
            return False  # Ya existe en el ámbito actual
        self.scopes[-1][symbol.name] = symbol
        return True
    
    def lookup(self, name:str)-> Optional[Symbol]:
        """Buscar simbolo """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def update(self, name: str, value: Any) -> bool:
        """Actualiza el valor de un símbolo existente"""
        symbol = self.lookup(name)
        if symbol:
            symbol.value = value
            symbol.is_initialized = True
            return True
        return False
    
    def update_lines(self, name: str, line: int) -> bool:
        """Actualiza las líneas de un símbolo existente"""
        symbol = self.lookup(name)
        if symbol:
            symbol.lines.append(line)
            return True
        return False
    
    def update_lines_r(self, symbol: Symbol, line: int) -> bool:
        """Actualiza las líneas de un símbolo existente"""
        symbol = self.lookup(str(symbol.name))
        if symbol:
            symbol.lines.append(line)
            return True
        return False
    
    def display(self):
        """Muestra el contenido de la tabla de símbolos"""
        print("\n=== TABLA DE SÍMBOLOS ===")
        for i, scope in enumerate(self.scopes):
            scope_name = "global" if i == 0 else f"scope_{i}"
            print(f"\nÁmbito: {scope_name}")
            print("-" * 60)
            print(f"{'Nombre':<15} {'Tipo':<10} {'Valor':<15} {'Inicializado':<12} {'Línea'}")
            print("-" * 60)
            for name, symbol in scope.items():
                init_status = "Sí" if symbol.is_initialized else "No"
                print(f"{symbol.name:<15} {symbol.data_type.value:<10} {str(symbol.value):<15} {init_status:<12} {symbol.lines}")

    def display_r(self):
        resp= "\n=== TABLA DE SÍMBOLOS ==="
        for i, scope in enumerate(self.scopes):
            scope_name = "global" if i == 0 else f"scope_{i}"
            resp += f"\n\nÁmbito: {scope_name}"
            resp += "\n" + ("-" * 60)
            resp += f"\n{'Nombre':<15} {'Tipo':<10} {'Valor':<15} {'Usada':<12} {'Línea':<20}"
            resp += "\n" + ("-" * 60)
            for name, symbol in scope.items():
                init_status = "Sí" if symbol.is_initialized else "No"
                resp += f"\n{symbol.name:<15} {symbol.data_type.value:<10} {str(symbol.value):<15} {init_status:<12} {symbol.lines}"
                resp += "\n" + ("-" * 60)
                resp += "\n"

        return resp
       
class SemAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []

    def analizar(self, nodo: ASTNode):
        """Analiza el AST recursivamente"""
        if nodo is None:
            return
        
        metodo = f"analizar_{str.lower(nodo.tipo)}"
        if hasattr(self, metodo):
            getattr(self, metodo)(nodo)
        else:
            for hijo in nodo.hijos:
                self.analizar(hijo)
        return nodo
    
    def analizar_programa(self, nodo: ASTNode):
        for hijo in nodo.hijos:
            self.analizar(hijo)
        self.symbol_table.display()

    def analizar_declaracion(self, nodo: ASTNode):
        tipo = nodo.valor  # Tipo de dato
        identificador = nodo.hijos[0].valor  # Nombre de la variable
        linea = nodo.linea

        # Cuando se encunetran varias variables en la misma declaración, cortarlas cuando tengan coma ","
        if "," in identificador:
            vars = identificador.split(",")
            for var in vars:
                var = var.strip()
                if self.symbol_table.lookup(var):
                    self.errors.append(f"Error semántico: La variable '{var}' ya está declarada. Línea {linea}")
                    nodo.marcar_error()
                    continue
                data_type = self.map_tipo(tipo)
                symbol = Symbol(name=var, data_type=data_type, scope=self.symbol_table.current_scope, lines=[linea])
                self.symbol_table.insert(symbol)

                if len(nodo.hijos) > 1:  # Si hay una inicialización
                    valor_nodo = nodo.hijos[1]
                    valor = self.evaluar_expresion(valor_nodo)
                    if valor is not None:
                        symbol.value = valor
                        symbol.is_initialized = True
                        valor_nodo.use = True
                        if not self.check_tipo_compatibility(data_type, valor_nodo.tipo_dato):
                            self.errors.append(f"Error semántico: Incompatibilidad de tipos en la inicialización de '{identificador}'. Línea {linea}")
                            nodo.marcar_error()
                        else:
                            nodo.tipo_dato = data_type
                    else:
                        nodo.marcar_error()
                else:
                    nodo.tipo_dato = data_type
        else:
            if self.symbol_table.lookup(identificador):
                self.errors.append(f"Error semántico: La variable '{identificador}' ya está declarada. Línea {linea}")
                nodo.marcar_error()
                return

            data_type = self.map_tipo(tipo)
            symbol = Symbol(name=identificador, data_type=data_type, scope=self.symbol_table.current_scope, lines=[linea])
            self.symbol_table.insert(symbol)

            if len(nodo.hijos) > 1:  # Si hay una inicialización
                valor_nodo = nodo.hijos[1]
                valor = self.evaluar_expresion(valor_nodo)
                if valor is not None:
                    symbol.value = valor
                    symbol.is_initialized = True
                    valor_nodo.use = True
                    if not self.check_tipo_compatibility(data_type, valor_nodo.tipo_dato):
                        self.errors.append(f"Error semántico: Incompatibilidad de tipos en la inicialización de '{identificador}'. Línea {linea}")
                        nodo.marcar_error()
                    else:
                        nodo.tipo_dato = data_type
                else:
                    nodo.marcar_error()
            else:
                nodo.tipo_dato = data_type

                
        nodo.scope = self.symbol_table.current_scope
        nodo.use = True
        nodo.tipo_dato = data_type
        self.analizar(valor_nodo) if len(nodo.hijos) > 2 else None

    def analizar_asignacion(self, nodo: ASTNode):
        identificador = nodo.hijos[0].valor
        linea = nodo.hijos[0].linea

        symbol = self.symbol_table.lookup(identificador)
        if not symbol:
            self.errors.append(f"Error semántico: La variable '{identificador}' no está declarada. Línea {linea}")
            nodo.marcar_error()
            return
            
        valor_nodo = nodo.hijos[1]
        valor = self.evaluar_expresion(valor_nodo)
        if valor is not None:
            if not self.check_tipo_compatibility(symbol.data_type, valor_nodo.tipo_dato):
                self.errors.append(f"Error semántico: Incompatibilidad de tipos en la asignación a '{identificador}'. Línea {linea}")
                nodo.marcar_error()
            else:
                # si se detecta que es tipo diferente a lo ingresado mandar error de asignación
                if symbol.data_type == DataType.INT and valor_nodo.tipo_dato == DataType.FLOAT:
                    self.symbol_table.update_lines(identificador, linea)
                    self.errors.append(f"Error semántico: No se puede asignar un valor de tipo 'float' a una variable de tipo 'int' en '{identificador}'. Línea {linea}")
                    nodo.marcar_error()
            
                elif symbol.data_type == DataType.FLOAT and valor_nodo.tipo_dato == DataType.INT:
                    self.symbol_table.update(identificador, float(valor))
                    self.symbol_table.update_lines(identificador, linea)
                    valor_nodo.use = True
                    nodo.tipo_dato = symbol.data_type
                else:
                    self.symbol_table.update(identificador, valor)
                    self.symbol_table.update_lines(identificador, linea)
                    valor_nodo.use = True
                    nodo.tipo_dato = symbol.data_type
        else:
            nodo.marcar_error()
        
        nodo.scope = symbol.scope
        nodo.use = True
        self.analizar(valor_nodo)

    
    def analizar_expresion(self, nodo: ASTNode):
        if nodo.tipo == "entero":
            nodo.tipo_dato = DataType.INT
            return nodo.valor
        elif nodo.tipo == "flotante":
            nodo.tipo_dato = DataType.FLOAT
            return nodo.valor
        elif nodo.tipo == "cadena":
            nodo.tipo_dato = DataType.STRING
            return nodo.valor
        elif nodo.tipo == "booleano":
            nodo.tipo_dato = DataType.BOOL
            return nodo.valor
        elif nodo.tipo == "identificador":
            symbol = self.symbol_table.lookup(nodo.valor)
            if not symbol:
                self.errors.append(f"Error semántico: La variable '{nodo.valor}' no está declarada. Línea {nodo.linea}")
                nodo.marcar_error()
                self.symbol_table.update_lines_r(symbol,nodo.linea)
                return None
            if not symbol.is_initialized:
                self.warnings.append(f"Advertencia semántica: La variable '{nodo.valor}' no está inicializada. Línea {nodo.linea}")
            nodo.tipo_dato = symbol.data_type
            self.symbol_table.update_lines_r(symbol,nodo.linea)
            symbol.use = True
            return symbol.value
        elif nodo.tipo is "Operacion":
            left_nodo = nodo.hijos[0]
            right_nodo = nodo.hijos[1]
            left_val = self.evaluar_expresion(left_nodo)
            right_val = self.evaluar_expresion(right_nodo)
            if left_val is None or right_val is None:
                nodo.marcar_error()
                return None

            if not self.check_tipo_compatibility(left_nodo.tipo_dato, right_nodo.tipo_dato):
                self.errors.append(f"Error semántico: Incompatibilidad de tipos en la expresión. Línea {nodo.linea}")
                nodo.marcar_error()
                return None
            
            tipo=tipo_op(nodo.valor)

            if left_nodo.tipo_dato == DataType.INT and right_nodo.tipo_dato == DataType.INT:
                if tipo == "suma":
                    resultado = left_val + right_val
                elif tipo == "resta":
                    resultado = left_val - right_val
                elif tipo == "multiplicacion":
                    resultado = left_val * right_val
                elif tipo == "division":
                    if right_val == 0:
                        self.errors.append(f"Error semántico: División por cero. Línea {nodo.linea}")
                        nodo.marcar_error()
                        return None
                    resultado = left_val / right_val
                nodo.tipo_dato = DataType.INT
                return resultado
            elif (left_nodo.tipo_dato == DataType.INT and right_nodo.tipo_dato == DataType.FLOAT) or \
                    (left_nodo.tipo_dato == DataType.FLOAT and right_nodo.tipo_dato == DataType.INT) or \
                    (left_nodo.tipo_dato == DataType.FLOAT and right_nodo.tipo_dato == DataType.FLOAT):
                if tipo == "suma":
                    resultado = float(left_val) + float(right_val)
                elif tipo == "resta":
                    resultado = float(left_val) - float(right_val)
                elif tipo == "multiplicacion":
                    resultado = float(left_val) * float(right_val)
                elif tipo == "division":
                    if right_val == 0:
                        self.errors.append(f"Error semántico: División por cero. Línea {nodo.linea}")
                        nodo.marcar_error()
                        return None
                    resultado = float(left_val) / float(right_val)
                nodo.tipo_dato = DataType.FLOAT
                return resultado
            elif left_nodo.tipo_dato == DataType.STRING and right_nodo.tipo_dato == DataType.STRING and nodo.tipo == "suma":
                resultado = left_val + right_val
                nodo.tipo_dato = DataType.STRING
                return resultado
            else:
                self.errors.append(f"Error semántico: Operación no soportada entre tipos '{left_nodo.tipo_dato}' y '{right_nodo.tipo_dato}'. Línea {nodo.linea}")
                nodo.marcar_error()
                return None
        else:
            self.errors.append(f"Error semántico: Nodo de expresión desconocido '{nodo.tipo}'. Línea {nodo.linea}")
            nodo.marcar_error()
            return None
        
    def evaluar_expresion(self, nodo: ASTNode):
        return self.analizar_expresion(nodo)
    
    def map_tipo(self, tipo_str: str) -> DataType:
        if tipo_str == "int":
            return DataType.INT
        elif tipo_str == "float":
            return DataType.FLOAT
        elif tipo_str == "string":
            return DataType.STRING
        elif tipo_str == "bool":
            return DataType.BOOL
        else:
            return DataType.ERROR
        
    def check_tipo_compatibility(self, tipo1: DataType, tipo2: DataType) -> bool:
        if tipo1 == tipo2:
            return True
        if (tipo1 == DataType.INT and tipo2 == DataType.FLOAT) or (tipo1 == DataType.FLOAT and tipo2 == DataType.INT):
            return True
        return False
    
    def report_errors(self):
        for error in self.errors:
            print(error)
        for warning in self.warnings:
            print(warning)
        
    
    def report_errors_r(self):
        """Retornar el texto a imprimir, errores y warnings"""
        report = ""
        for error in self.errors:
            report += error + "\n"
        for warning in self.warnings:
            report += warning + "\n"
        return report

# Ejemplo de uso
if __name__ == "__main__":
    # Construcción de un AST de ejemplo
    programa = ASTNode("programa")
    
    decl1 = ASTNode("declaracion", linea=1, valor="int")
    decl1.agregar_hijo(ASTNode("identificador", valor="x,a"))
    decl1.agregar_hijo(ASTNode("entero", valor=10))
    
    decl2 = ASTNode("declaracion", linea=2, valor="float")
    decl2.agregar_hijo(ASTNode("identificador", valor="y"))
    
    asignacion = ASTNode("asignacion", linea=3)
    asignacion.agregar_hijo(ASTNode("identificador", valor="y",linea=3))
    expr = ASTNode("suma")
    expr.agregar_hijo(ASTNode("identificador", valor="x",linea=3))
    expr.agregar_hijo(ASTNode("flotante", valor=5.5))
    asignacion.agregar_hijo(expr)
    
    # Error de suma a un int con un float
    asignacion2 = ASTNode("asignacion", linea=4)
    asignacion2.agregar_hijo(ASTNode("identificador", valor="x",linea=4))
    expr2 = ASTNode("suma")
    expr2.agregar_hijo(ASTNode("identificador", valor="x", linea=4))
    expr2.agregar_hijo(ASTNode("flotante", valor=5.5))
    asignacion2.agregar_hijo(expr2)

    # asignación de un float a un int

    # asignacion2 = ASTNode("asignacion", linea=4)
    # asignacion2.agregar_hijo(ASTNode("identificador", valor="y"))   
    # asignacion2.agregar_hijo(ASTNode("entero", valor=3))

    programa.agregar_hijo(decl1)
    programa.agregar_hijo(decl2)
    programa.agregar_hijo(asignacion)
    programa.agregar_hijo(asignacion2)

    # Análisis semántico
    analyzer = SemAnalyzer()
    analyzer.analizar(programa)
    print(analyzer.report_errors_r())
