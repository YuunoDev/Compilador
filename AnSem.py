from dataclasses import dataclass, field
import enum
from typing import Any,Optional

class ASTNode:
    def __init__(self, tipo, valor=None, linea=None, columna=None, id=""):
        self.tipo = tipo
        self.valor = valor
        self.id = id
        self.linea = linea
        self.columna = columna
        self.hijos :ASTNode = []
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

class DataType(enum.Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    ERROR = "error"
    UNDEFINED = "undefined"
    INCOMPATIBLE = "incompatible"

def tipo_op(op):
    if op == "+":
        return "suma"
    elif op == "-":
        return "resta"
    elif op == "*":
        return "multiplicacion"
    elif op == "/":
        return "division"
    elif op == ">":
        return "mayor"
    elif op == "<":
        return "menor"
    elif op == ">=":
        return "mayor_igual"
    elif op == "<=":
        return "menor_igual"
    elif op == "==":
        return "igual"
    elif op == "!=":
        return "diferente"
    elif op == "&&":
        return "and"
    elif op == "||":
        return "or"
    elif op == "!":
        return "not"
    elif op == "%":
        return "modulo"
    else:
        return "desconocido"

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
        self.scopes = [{}]
        self.current_scope = "global"

    def erase(self):
        self.scopes = [{}]

    def insert(self, symbol: Symbol)-> bool:
        if symbol.name in self.scopes[-1]:
            return False
        self.scopes[-1][symbol.name] = symbol
        return True
    
    def lookup(self, name:str)-> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def update(self, name: str, value: Any) -> bool:
        symbol = self.lookup(name)
        if symbol:
            symbol.value = value
            symbol.is_initialized = True
            return True
        return False
    
    def update_lines(self, name: str, line: int) -> bool:
        symbol = self.lookup(name)
        if symbol:
            symbol.lines.append(line)
            return True
        return False
    
    def update_lines_r(self, symbol: Symbol, line: int) -> bool:
        symbol = self.lookup(str(symbol.name))
        if symbol:
            symbol.lines.append(line)
            return True
        return False
    
    def display(self):
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
        """
        Devuelve la tabla de símbolos en un formato estructurado para insertar en Treeview.
        """
        tabla = []

        for i, scope in enumerate(self.scopes):
            scope_name = "global" if i == 0 else f"scope_{i}"

            # ordenar líneas
            for name, symbol in scope.items():
                symbol.lines.sort()

            for name, symbol in scope.items():
                tabla.append({
                    "ambito": scope_name,
                    "nombre": symbol.name,
                    "tipo": symbol.data_type.value,
                    "valor": symbol.value,
                    "usada": "Sí" if symbol.is_initialized else "No",
                    "lineas": ", ".join(map(str, symbol.lines))
                })

        return tabla


class SemAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.tree = ASTNode("Raiz", valor="", linea="", columna="")

    def erase(self):
        self.symbol_table.erase()
        self.errors = []
        self.warnings = []
        self.tree = ASTNode("Raiz", valor="", linea="", columna="")

    def analizar(self, nodo: ASTNode, parent_tree_node=None):
        """Analiza el AST recursivamente con contexto de padre"""
        if nodo is None:
            return None
        
        metodo = f"analizar_{str.lower(nodo.tipo)}"
        if hasattr(self, metodo):
            return getattr(self, metodo)(nodo, parent_tree_node)
        else:
            #si tiene hijos los analiza
            if nodo.hijos:
                for hijo in nodo.hijos:
                    self.analizar(hijo, parent_tree_node)
            else:
                #si no retorna el hijo
                return nodo
            return None

    def analizar_programa(self, nodo: ASTNode, parent_tree_node=None):
        for hijo in nodo.hijos:
            self.analizar(hijo, self.tree)

    
    def analizar_declaracion(self, nodo: ASTNode, parent_tree_node=None):
        tipo = nodo.valor
        identificador = nodo.hijos[0].valor
        linea = nodo.linea
        columna = nodo.columna
        tree_declaracion= ASTNode("Declaracion",valor="",linea="", columna="")
        tree_declaracion.agregar_hijo(ASTNode(tipo,valor=" ",linea=linea, columna=nodo.columna))
        tree_dec_vars= []
        var_nodo = None
        
        # INICIALIZAR data_type al inicio
        data_type = self.map_tipo(tipo)

        if "," in identificador:
            vars = identificador.split(",")
            #print(f"Declarando multiples variables: {vars} de tipo {tipo}")
            for var in vars:
                #print(f"Declarando variable: {var} de tipo {tipo}")
                var = var.strip()
                if self.symbol_table.lookup(var):
                    self.errors.append(f"Error semántico: La variable '{var}' ya está declarada. Línea {linea}")
                    nodo.marcar_error()
                    continue
                
                symbol = Symbol(name=var, data_type=data_type, scope=self.symbol_table.current_scope, lines=[linea])
                self.symbol_table.insert(symbol)

                if len(nodo.hijos) > 1:
                    # No redefinir data_type aquí, ya lo tenemos
                    symbol = Symbol(name=identificador, data_type=data_type, scope=self.symbol_table.current_scope, lines=[linea])
                    self.symbol_table.insert(symbol)

                    nodo.tipo_dato = data_type
                    var_nodo = ASTNode(("ID("+identificador+")"),id=str(identificador),valor="",linea=linea, columna=nodo.columna)
                    var_nodo.tipo_dato=data_type
                    tree_dec_vars.append(var_nodo)
                else:
                    nodo.tipo_dato = data_type
                    var_nodo = ASTNode(("ID("+var+")"),id=str(var),valor="",linea=linea, columna=columna)
                    var_nodo.tipo_dato=data_type
                    tree_dec_vars.append(var_nodo)
        else:
            if self.symbol_table.lookup(identificador):
                self.errors.append(f"Error semántico: La variable '{identificador}' ya está declarada. Línea {linea}")
                nodo.marcar_error()
                # Agregar al menos el nodo de declaración aunque tenga error
                if parent_tree_node is not None:
                    parent_tree_node.agregar_hijo(tree_declaracion)
                return tree_declaracion
            # asignacion o detecto asignacion
            if len(nodo.hijos) > 1:
                # data_type ya está definido al inicio
                symbol = Symbol(name=identificador, data_type=data_type, scope=self.symbol_table.current_scope, lines=[linea])
                self.symbol_table.insert(symbol)

                nodo.tipo_dato = data_type
                var_nodo = ASTNode(("ID("+identificador+")"),id=str(identificador),valor="",linea=linea, columna=nodo.columna)
                var_nodo.tipo_dato=data_type
                tree_dec_vars.append(var_nodo)
            else:
                # Declaración sin asignación
                symbol = Symbol(name=identificador, data_type=data_type, scope=self.symbol_table.current_scope, lines=[linea])
                self.symbol_table.insert(symbol)
                
                nodo.tipo_dato = data_type
                var_nodo = ASTNode(("ID("+identificador+")"),id=str(identificador),valor="",linea=linea, columna=columna)
                var_nodo.tipo_dato=data_type
                tree_dec_vars.append(var_nodo)

        nodo.scope = self.symbol_table.current_scope
        nodo.use = True
        nodo.tipo_dato = data_type  # Ahora data_type siempre está definido
        
        for var_nodo in tree_dec_vars:
            tree_declaracion.agregar_hijo(var_nodo)
        
        # Agregar al padre correspondiente (self.tree o el nodo padre de control)
        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(tree_declaracion)
        
        for hijo in nodo.hijos:
            #print(f"Analizando hijo de declaracion: {hijo}")
            self.analizar(hijo, tree_declaracion)
        
        return tree_declaracion


    def analizar_asignacion(self, nodo: ASTNode, parent_tree_node=None):
        for hijo in nodo.hijos:
            self.analizar(hijo, parent_tree_node)
        
        identificador = nodo.hijos[0].valor
        linea = nodo.hijos[0].linea
        columna = nodo.hijos[0].columna
        tree_asignacion= ASTNode("Asignacion",valor="",linea="", columna="")

        symbol = self.symbol_table.lookup(identificador)
        if not symbol:
            self.errors.append(f"Error semántico: La variable '{identificador}' no está declarada. Línea {linea}")
            node_id = ASTNode("ID("+identificador+")",id=str(identificador), valor="Error", linea=linea, columna=columna)
            node_id.tipo_dato = DataType.UNDEFINED
            tree_asignacion.agregar_hijo(node_id)
            if parent_tree_node is not None:
                parent_tree_node.agregar_hijo(tree_asignacion)
            nodo.marcar_error()
            return tree_asignacion
            
        valor_nodo = nodo.hijos[1]
        valor, arbol_valor = self.evaluar_expresion(valor_nodo)

        if valor is not None:
            if not self.check_tipo_compatibility(symbol.data_type, valor_nodo.tipo_dato):
                self.errors.append(f"Error semántico: Incompatibilidad de tipos en la asignación a '{identificador}'. Línea {linea}")
                tree_asignacion.agregar_hijo(ASTNode("ID("+identificador+")",id=str(identificador),tipo_dato=DataType.INCOMPATIBLE,valor="Error",linea=linea, columna=columna))
                self.symbol_table.update_lines(identificador, linea)
                nodo.marcar_error()
            else:
                if symbol.data_type == DataType.INT and valor_nodo.tipo_dato == DataType.FLOAT:
                    self.symbol_table.update_lines(identificador, linea)
                    self.errors.append(f"Error semántico: No se puede asignar un valor de tipo 'float' a una variable de tipo 'int' en '{identificador}'. Línea {linea}")
                    node_id= ASTNode("ID("+identificador+")",id=str(identificador),valor="Error",linea=linea, columna=columna)
                    node_id.tipo_dato = DataType.INCOMPATIBLE
                    tree_asignacion.agregar_hijo(node_id)
                    nodo.marcar_error()
                elif symbol.data_type == DataType.FLOAT and valor_nodo.tipo_dato == DataType.INT:
                    self.symbol_table.update(identificador, float(valor))
                    self.symbol_table.update_lines(identificador, linea)
                    valor_nodo.use = True
                    nodo_id = ASTNode("ID("+identificador+")",id=str(identificador),valor=valor,linea=linea, columna=columna)
                    nodo_id.tipo_dato = symbol.data_type
                    tree_asignacion.agregar_hijo(nodo_id)
                    nodo.tipo_dato = symbol.data_type
                else:
                    if symbol.data_type == DataType.INT:
                        self.symbol_table.update(identificador, int(valor))
                    else:
                        self.symbol_table.update(identificador, valor)
                    self.symbol_table.update_lines(identificador, linea)
                    valor_nodo.use = True
                    nodo_id = ASTNode("ID("+identificador+")",id=str(identificador),valor=valor,linea=linea, columna=columna)
                    nodo_id.tipo_dato = symbol.data_type
                    tree_asignacion.agregar_hijo(nodo_id)
                    nodo.tipo_dato = symbol.data_type
                #self.symbol_table.update_lines(identificador, linea)
        else:
            nodo_id = ASTNode("ID("+identificador+")",id=str(identificador),valor="Error",linea=linea, columna=columna)
            nodo_id.tipo_dato = DataType.UNDEFINED
            tree_asignacion.agregar_hijo(nodo_id)
            self.symbol_table.update_lines(identificador, linea)
            nodo.marcar_error()
        
        nodo.scope = symbol.scope
        nodo.use = True
        tree_asignacion.agregar_hijo(arbol_valor if arbol_valor else valor_nodo)
        
        # Agregar al padre correspondiente
        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(tree_asignacion)
        
       # print(f"Asignación analizada: {tree_asignacion}")
        return tree_asignacion
   
    def analizar_expresion(self, nodo: ASTNode):
        for hijo in nodo.hijos:
            self.analizar(hijo)

        if nodo.tipo == "entero":
            nodo.tipo_dato = DataType.INT
            nodo_valor = ASTNode("entero", valor=nodo.valor, linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.INT
            return nodo.valor, nodo_valor
        elif nodo.tipo == "flotante":
            nodo.tipo_dato = DataType.FLOAT
            nodo_valor = ASTNode("flotante",valor=nodo.valor,linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.FLOAT
            return nodo.valor, nodo_valor
        elif nodo.tipo == "cadena":
            nodo.tipo_dato = DataType.STRING
            nodo_valor = ASTNode("cadena",valor=nodo.valor,linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.STRING
            return nodo.valor, nodo_valor
        elif nodo.tipo == "booleano":
            nodo.tipo_dato = DataType.BOOL
            nodo_valor = ASTNode("booleano",valor=nodo.valor,linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.BOOL
            return nodo.valor, nodo_valor
        elif nodo.tipo == "identificador":
            symbol = self.symbol_table.lookup(nodo.valor)
            if not symbol:
                self.errors.append(f"Error semántico: La variable '{nodo.valor}' no está declarada. Línea {nodo.linea}")
                nodo_valor = ASTNode("ID("+nodo.valor+")",id=str(nodo.valor),valor="Error",linea=nodo.linea, columna=nodo.columna)
                nodo_valor.tipo_dato = DataType.UNDEFINED
                nodo.marcar_error()
                return None, nodo_valor
            if not symbol.is_initialized:
                if not self.warnings or f"Advertencia semántica: La variable '{nodo.valor}' no está inicializada. Línea {nodo.linea}" not in self.warnings:
                    self.warnings.append(f"Advertencia semántica: La variable '{nodo.valor}' no está inicializada. Línea {nodo.linea}")
                nodo.marcar_warning()
                nodo_valor = ASTNode("ID("+nodo.valor+")",id=str(nodo.valor),valor="Uninitialized",linea=nodo.linea, columna=nodo.columna)
                nodo_valor.tipo_dato = symbol.data_type
                self.symbol_table.update_lines(nodo.valor, nodo.linea)
                return None, nodo_valor
            nodo.tipo_dato = symbol.data_type
            self.symbol_table.update_lines_r(symbol,nodo.linea)
            symbol.use = True
            nodo_valor = ASTNode("ID("+nodo.valor+")",id=str(nodo.valor),valor=symbol.value,linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = symbol.data_type
            return symbol.value, nodo_valor
        elif nodo.tipo in ["Operacion","operacion"]:
            left_nodo = nodo.hijos[0]
            right_nodo = nodo.hijos[1]
            
            # Evaluar las subexpresiones para obtener sus valores y árboles
            left_val, left_val_nodo = self.analizar_expresion(left_nodo)
            right_val, right_val_nodo = self.analizar_expresion(right_nodo)
            
            nodo_op = ASTNode(nodo.valor,valor="",linea=nodo.linea, columna=nodo.columna)
            nodo_op.tipo_dato = ""
            nodo_op.agregar_hijo(left_val_nodo)
            nodo_op.agregar_hijo(right_val_nodo)

            if left_val is None or right_val is None:
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op

            if not self.check_tipo_compatibility(left_nodo.tipo_dato, right_nodo.tipo_dato):
                self.errors.append(f"Error semántico: Incompatibilidad de tipos en la expresión. Línea {nodo.linea}")
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op
            
            tipo=tipo_op(nodo.valor)

            if left_nodo.tipo_dato == DataType.INT and right_nodo.tipo_dato == DataType.INT:
                if isinstance(left_val,str):
                    left_val=float(left_val) if '.' in left_val else int(left_val)
                if isinstance(right_val,str):
                    right_val=float(right_val) if '.' in right_val else int(right_val)

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
                        nodo_op.tipo_dato = DataType.ERROR
                        return None, nodo_op
                    resultado = left_val / right_val
                    resultado = int(resultado)  # Truncar a entero
                elif tipo == "modulo":
                    if right_val == 0:
                        self.errors.append(f"Error semántico: Módulo por cero. Línea {nodo.linea}")
                        nodo.marcar_error()
                        nodo_op.tipo_dato = DataType.ERROR
                        return None, nodo_op
                    resultado = left_val % right_val

                nodo.tipo_dato = DataType.INT
                nodo_op.tipo_dato = DataType.INT
                nodo_op.set_tipo(nodo.valor+"("+str(resultado)+")")
                return resultado, nodo_op
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
                        nodo_op.tipo_dato = DataType.ERROR
                        return None, nodo_op
                    resultado = float(left_val) / float(right_val)
                    #truncar resultado a 4 decimales
                    #resultado = float(f"{resultado:.4f}")
                elif tipo == "modulo":
                    if right_val == 0:
                        self.errors.append(f"Error semántico: Módulo por cero. Línea {nodo.linea}")
                        nodo.marcar_error()
                        nodo_op.tipo_dato = DataType.ERROR
                        return None, nodo_op
                    resultado = float(left_val) % float(right_val)

                nodo.tipo_dato = DataType.FLOAT
                nodo_op.tipo_dato = DataType.FLOAT
                nodo_op.set_tipo(nodo.valor+"("+str(resultado)+")")
                return resultado, nodo_op
            elif left_nodo.tipo_dato == DataType.STRING and right_nodo.tipo_dato == DataType.STRING and nodo.tipo == "suma":
                resultado = left_val + right_val
                nodo.tipo_dato = DataType.STRING
                nodo_op.tipo_dato = DataType.STRING
                return resultado, nodo_op
            else:
                self.errors.append(f"Error semántico: Operación no soportada entre tipos '{left_nodo.tipo_dato}' y '{right_nodo.tipo_dato}'. Línea {nodo.linea}")
                nodo_op = ASTNode(nodo.valor,valor="Error",linea=nodo.linea, columna=nodo.columna)
                nodo_op.tipo_dato = DataType.ERROR
                nodo.marcar_error()
                return None, nodo_op
        elif nodo.tipo in ["OperacionComparacion","Operacioncomparacion"]:    
            left_nodo = nodo.hijos[0]
            right_nodo = nodo.hijos[1]
            left_val, left_val_nodo = self.analizar_expresion(left_nodo)
            right_val, right_val_nodo = self.analizar_expresion(right_nodo)
            nodo_op = ASTNode(nodo.valor,valor="",linea=nodo.linea, columna=nodo.columna)
            nodo_op.tipo_dato = DataType.BOOL
            nodo_op.agregar_hijo(left_val_nodo)
            nodo_op.agregar_hijo(right_val_nodo)

            if left_val is None or right_val is None:
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op

            if not self.check_tipo_compatibility(left_nodo.tipo_dato, right_nodo.tipo_dato):
                self.errors.append(f"Error semántico: Incompatibilidad de tipos en la expresión de comparación. Línea {nodo.linea}")
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op

            # Asegurar los tipos de cada lado para la comparación
            if left_nodo.tipo_dato == DataType.INT and right_nodo.tipo_dato == DataType.INT:
                if isinstance(left_val,str):
                    left_val=int(left_val)
                if isinstance(right_val,str):
                    right_val=int(right_val)
            elif (left_nodo.tipo_dato == DataType.INT and right_nodo.tipo_dato == DataType.FLOAT) or \
                        (left_nodo.tipo_dato == DataType.FLOAT and right_nodo.tipo_dato == DataType.INT) or \
                        (left_nodo.tipo_dato == DataType.FLOAT and right_nodo.tipo_dato == DataType.FLOAT):
                left_val=float(left_val)
                right_val=float(right_val)
            elif left_nodo.tipo_dato == DataType.STRING and right_nodo.tipo_dato == DataType.STRING:
                pass
            else:
                self.errors.append(f"Error semántico: Operación de comparación no soportada entre tipos '{left_nodo.tipo_dato}' y '{right_nodo.tipo_dato}'. Línea {nodo.linea}")
                nodo_op = ASTNode(nodo.valor,valor="Error",linea=nodo.linea, columna=nodo.columna)
                nodo_op.tipo_dato = DataType.ERROR
                nodo.marcar_error()
                return None, nodo_op

            if nodo.valor == ">":
                resultado = left_val > right_val
            elif nodo.valor == "<":
                resultado = left_val < right_val
            elif nodo.valor == ">=":
                resultado = left_val >= right_val
            elif nodo.valor == "<=":
                resultado = left_val <= right_val
            elif nodo.valor == "==":
                resultado = left_val == right_val
            elif nodo.valor == "!=":
                resultado = left_val != right_val
            else:
                self.errors.append(f"Error semántico: Operador de comparación desconocido '{nodo.valor}'. Línea {nodo.linea}")
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op

            nodo_op.setvalor(str(resultado))
            nodo.tipo_dato = DataType.BOOL
            return resultado, nodo_op
        
        elif nodo.tipo in ["OperacionLogica","Operacionlogica"]:
            left_nodo = nodo.hijos[0]
            right_nodo = nodo.hijos[1]
            left_val, left_val_nodo = self.analizar_expresion(left_nodo)
            right_val, right_val_nodo = self.analizar_expresion(right_nodo)
            nodo_op = ASTNode(nodo.valor,valor="",linea=nodo.linea, columna=nodo.columna)
            nodo_op.tipo_dato = DataType.BOOL
            nodo_op.agregar_hijo(left_val_nodo)
            nodo_op.agregar_hijo(right_val_nodo)

            if left_val is None or right_val is None:
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op

            if left_nodo.tipo_dato != DataType.BOOL or right_nodo.tipo_dato != DataType.BOOL:
                self.errors.append(f"Error semántico: Operación lógica requiere operandos de tipo 'bool'. Línea {nodo.linea}")
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op

            if nodo.valor == "&&":
                resultado = left_val and right_val
            elif nodo.valor == "||":
                resultado = left_val or right_val
            else:
                self.errors.append(f"Error semántico: Operador lógico desconocido '{nodo.valor}'. Línea {nodo.linea}")
                nodo.marcar_error()
                nodo_op.tipo_dato = DataType.ERROR
                return None, nodo_op
            
            nodo_op.setvalor(str(resultado))
            nodo.tipo_dato = DataType.BOOL
            return resultado, nodo_op
        else:
             self.errors.append(f"Error semántico: Nodo de expresión desconocido '{nodo.tipo}'. Línea {nodo.linea}")
             nodo_op = ASTNode(nodo.valor,valor="Error",linea=nodo.linea, columna=nodo.columna)
             nodo_op.tipo_dato = DataType.ERROR
             nodo.marcar_error()
             return None, nodo_op

    def evaluar_expresion_simple(self, nodo: ASTNode):
        if nodo.tipo == "entero":
            nodo_valor = ASTNode("entero", valor=nodo.valor, linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.INT
            return nodo.valor, nodo_valor
        elif nodo.tipo == "flotante":
            nodo_valor = ASTNode("flotante", valor=nodo.valor, linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.FLOAT
            return nodo.valor, nodo_valor
        elif nodo.tipo == "cadena":
            nodo_valor = ASTNode("cadena", valor=nodo.valor, linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.STRING
            return nodo.valor, nodo_valor
        elif nodo.tipo == "booleano":
            nodo_valor = ASTNode("booleano", valor=nodo.valor, linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = DataType.BOOL
            return nodo.valor, nodo_valor
        elif nodo.tipo == "identificador":
            symbol = self.symbol_table.lookup(nodo.valor)
            if not symbol:
                nodo_valor = ASTNode("ID("+nodo.valor+")",id=str(nodo.valor), valor="Error", linea=nodo.linea, columna=nodo.columna)
                nodo_valor.tipo_dato = DataType.UNDEFINED
                self.symbol_table.update_lines(nodo.valor, nodo.linea)
                return None, nodo_valor
            nodo_valor = ASTNode("ID("+nodo.valor+")",id=str(nodo.valor), valor=symbol.value, linea=nodo.linea, columna=nodo.columna)
            nodo_valor.tipo_dato = symbol.data_type
            self.symbol_table.update_lines(nodo.valor, nodo.linea)
            return symbol.value, nodo_valor
        elif nodo.tipo in ["Operacion", "operacion", "OperacionComparacion", "Operacioncomparacion", "OperacionLogica", "Operacionlogica"]:
            # Para operaciones complejas, evaluarlas recursivamente
            return self.analizar_expresion(nodo)
        else:
            return None, nodo
        
    def analizar_if(self, nodo: ASTNode, parent_tree_node=None):
        condicion_nodo = nodo.hijos[0]
        condicion_val, condicion_arbol = self.evaluar_expresion(condicion_nodo)
        
        nodo_if = ASTNode("If", valor="", linea=nodo.linea, columna=nodo.columna)
        
        nodo_condicion = ASTNode("Condicion", valor="", linea=condicion_nodo.linea, columna=condicion_nodo.columna)
        nodo_condicion.agregar_hijo(condicion_arbol if condicion_arbol else condicion_nodo)
        nodo_if.agregar_hijo(nodo_condicion)

        # Verificar el tipo de dato del árbol devuelto, no del nodo original
        arbol_tipo_dato = condicion_arbol.tipo_dato if condicion_arbol else condicion_nodo.tipo_dato
        
        if condicion_val is None:
            self.errors.append(f"Error semántico: La condición del 'if' no es válida. Línea {nodo.linea}")
            nodo.marcar_error()
        elif arbol_tipo_dato is None or arbol_tipo_dato != DataType.BOOL:
            self.errors.append(f"Error semántico: La condición del 'if' debe ser de tipo 'bool'. Línea {nodo.linea}")
            nodo.marcar_error()
        
        bloque_if = nodo.hijos[1]
        nodo_bloque_if = ASTNode("BloqueIf", valor="", linea=bloque_if.linea, columna=bloque_if.columna)
        for hijo in bloque_if.hijos:
            self.analizar(hijo, nodo_bloque_if)
        nodo_if.agregar_hijo(nodo_bloque_if)

        if len(nodo.hijos) > 2:
            bloque_else = nodo.hijos[2]
            nodo_bloque_else = ASTNode("BloqueElse", valor="", linea=bloque_else.linea, columna=bloque_else.columna)
            for hijo in bloque_else.hijos:
                self.analizar(hijo, nodo_bloque_else)
            nodo_if.agregar_hijo(nodo_bloque_else)

        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_if)
        
        return nodo_if

    def analizar_else(self, nodo: ASTNode, parent_tree_node=None):
        for hijo in nodo.hijos:
            self.analizar(hijo, parent_tree_node)

    def analizar_incremento(self, nodo: ASTNode, parent_tree_node=None):
        # Primero obtener la información básica
        asignacion_nodo = nodo.hijos[0]
        identificador = asignacion_nodo.hijos[0].valor
        linea = nodo.linea
        
        # Verificar el símbolo primero
        symbol = self.symbol_table.lookup(identificador)
        
        if not symbol:
            self.errors.append(f"Error semántico: La variable '{identificador}' no está declarada. Línea {linea}")
            nodo.marcar_error()
            return None
        
        if symbol.data_type not in [DataType.INT, DataType.FLOAT]:
            self.errors.append(f"Error semántico: La variable '{identificador}' no es de tipo numérico. Línea {linea}")
            self.symbol_table.update_lines(identificador, linea)
            nodo.marcar_error()
            return None
        
        if not symbol.is_initialized:

            #verificar que el error no este ya marcado 
            if not self.warnings or f"Advertencia semántica: La variable '{identificador}' no está inicializada. Línea {linea}" not in self.warnings:
                self.warnings.append(f"Advertencia semántica: La variable '{identificador}' no está inicializada. Línea {linea}")
            self.symbol_table.update_lines(identificador, linea)
            nodo.marcar_warning()
        
        # Crear el nodo de incremento primero
        nodo_inc = ASTNode("Incremento", valor="++", linea=linea, columna=nodo.columna)
        nodo_id = ASTNode(("ID("+identificador+")"),id=str(identificador), valor=identificador, linea=linea, columna=nodo.columna)
        nodo_id.tipo_dato = symbol.data_type
        nodo_inc.agregar_hijo(nodo_id)
        
        # AHORA analizar la asignación, pasando el nodo_inc como padre para el árbol
        asignacion_arbol = self.analizar(asignacion_nodo, nodo_inc)
        
        # Si no se generó un árbol para la asignación, agregar el nodo original
        if not asignacion_arbol:
            nodo_inc.agregar_hijo(asignacion_nodo)
        
        # Finalmente agregar al padre principal
        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_inc)
        
        return nodo_inc

    def analizar_decremento(self, nodo: ASTNode, parent_tree_node=None):
        # Primero obtener la información básica
        asignacion_nodo = nodo.hijos[0]
        identificador = asignacion_nodo.hijos[0].valor
        linea = nodo.linea
        
        # Verificar el símbolo primero
        symbol = self.symbol_table.lookup(identificador)
        if not symbol:
            self.errors.append(f"Error semántico: La variable '{identificador}' no está declarada. Línea {linea}")
            nodo.marcar_error()
            return None
        
        if symbol.data_type not in [DataType.INT, DataType.FLOAT]:
            self.errors.append(f"Error semántico: La variable '{identificador}' no es de tipo numérico. Línea {linea}")
            self.symbol_table.update_lines(identificador, linea)
            nodo.marcar_error()
            return None
        
        if not symbol.is_initialized:
            self.warnings.append(f"Advertencia semántica: La variable '{identificador}' no está inicializada. Línea {linea}")
            self.symbol_table.update_lines(identificador, linea)
            nodo.marcar_warning()
        
        # Crear el nodo de decremento primero
        nodo_dec = ASTNode("Decremento", valor="--", linea=linea, columna=nodo.columna)
        nodo_id = ASTNode(("ID("+identificador+")"),id=str(identificador), valor=identificador, linea=linea, columna=nodo.columna)
        nodo_id.tipo_dato = symbol.data_type
        nodo_dec.agregar_hijo(nodo_id)
        
        # AHORA analizar la asignación, pasando el nodo_dec como padre para el árbol
        asignacion_arbol = self.analizar(asignacion_nodo, nodo_dec)
        
        # Si no se generó un árbol para la asignación, agregar el nodo original
        if not asignacion_arbol:
            nodo_dec.agregar_hijo(asignacion_nodo)
        
        # Finalmente agregar al padre principal
        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_dec)
        
        return nodo_dec

    def analizar_while(self, nodo: ASTNode, parent_tree_node=None):
        condicion_nodo = nodo.hijos[0]
        condicion_val, condicion_arbol = self.evaluar_expresion(condicion_nodo)
        
        nodo_while = ASTNode("While", valor="", linea=nodo.linea, columna=nodo.columna)
        
        nodo_condicion = ASTNode("Condicion", valor="", linea=condicion_nodo.linea, columna=condicion_nodo.columna)
        nodo_condicion.agregar_hijo(condicion_arbol if condicion_arbol else condicion_nodo)
        nodo_while.agregar_hijo(nodo_condicion)

        # Verificar el tipo de dato del árbol devuelto, no del nodo original
        arbol_tipo_dato = condicion_arbol.tipo_dato if condicion_arbol else condicion_nodo.tipo_dato
        
        if condicion_val is None:
            self.errors.append(f"Error semántico: La condición del 'while' no es válida. Línea {nodo.linea}")
            nodo.marcar_error()
        elif arbol_tipo_dato is None or arbol_tipo_dato != DataType.BOOL:
            self.errors.append(f"Error semántico: La condición del 'while' debe ser de tipo 'bool'. Línea {nodo.linea}")
            nodo.marcar_error()
        
        cuerpo = nodo.hijos[1]
        nodo_cuerpo = ASTNode("Cuerpo", valor="", linea=cuerpo.linea, columna=cuerpo.columna)
        for hijo in cuerpo.hijos:
            self.analizar(hijo, nodo_cuerpo)
        nodo_while.agregar_hijo(nodo_cuerpo)

        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_while)
        
        return nodo_while

    def analizar_dountil(self, nodo: ASTNode, parent_tree_node=None):
        cuerpo = nodo.hijos[0]
        condicion_nodo = nodo.hijos[1]
        
        condicion_val, condicion_arbol = self.evaluar_expresion(condicion_nodo)
        
        nodo_do_while = ASTNode("DoUntil", valor="", linea=nodo.linea, columna=nodo.columna)
        
        nodo_cuerpo = ASTNode("Cuerpo", valor="", linea=cuerpo.linea, columna=cuerpo.columna)
        for hijo in cuerpo.hijos:
            self.analizar(hijo, nodo_cuerpo)
        nodo_do_while.agregar_hijo(nodo_cuerpo)
        
        nodo_condicion = ASTNode("Condicion", valor="", linea=condicion_nodo.linea, columna=condicion_nodo.columna)
        nodo_condicion.agregar_hijo(condicion_arbol if condicion_arbol else condicion_nodo)
        nodo_do_while.agregar_hijo(nodo_condicion)

        # Verificar el tipo de dato del árbol devuelto, no del nodo original
        arbol_tipo_dato = condicion_arbol.tipo_dato if condicion_arbol else condicion_nodo.tipo_dato
        
        if condicion_val is None:
            self.errors.append(f"Error semántico: La condición del 'do-while' no es válida. Línea {nodo.linea}")
            nodo.marcar_error()
        elif arbol_tipo_dato is None or arbol_tipo_dato != DataType.BOOL:
            self.errors.append(f"Error semántico: La condición del 'do-while' debe ser de tipo 'bool'. Línea {nodo.linea}")
            nodo.marcar_error()

        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_do_while)
        
        return nodo_do_while
    
    def analizar_for(self, nodo: ASTNode, parent_tree_node=None):
        """Analiza la estructura for"""
        if len(nodo.hijos) < 4:
            self.errors.append(f"Error semántico: Estructura 'for' incompleta. Línea {nodo.linea}")
            return None
        
        nodo_for = ASTNode("For", valor="", linea=nodo.linea, columna=nodo.columna)
        
        # 1. INICIALIZACIÓN
        init_nodo = nodo.hijos[0]
        nodo_init = ASTNode("Inicializacion", valor="", linea=init_nodo.linea, columna=init_nodo.columna)
        
        if init_nodo.hijos:
            for hijo in init_nodo.hijos:
                self.analizar(hijo, nodo_init)
        
        nodo_for.agregar_hijo(nodo_init)
        
        # 2. CONDICIÓN
        condicion_nodo = nodo.hijos[1]
        
        condicion_val = None
        condicion_arbol = None
        
        if condicion_nodo.hijos:
            condicion_val, condicion_arbol = self.evaluar_expresion(condicion_nodo.hijos[0])
        
        nodo_condicion = ASTNode("Condicion", valor="", linea=condicion_nodo.linea, columna=condicion_nodo.columna)
        nodo_condicion.agregar_hijo(condicion_arbol if condicion_arbol else condicion_nodo)
        nodo_for.agregar_hijo(nodo_condicion)
        
        # Verificar el tipo de dato del árbol devuelto
        arbol_tipo_dato = condicion_arbol.tipo_dato if condicion_arbol else None
        
        if condicion_val is None:
            self.errors.append(f"Error semántico: La condición del 'for' no es válida. Línea {nodo.linea}")
            nodo.marcar_error()
        elif arbol_tipo_dato is None or arbol_tipo_dato != DataType.BOOL:
            self.errors.append(f"Error semántico: La condición del 'for' debe ser de tipo 'bool'. Línea {nodo.linea}")
            nodo.marcar_error()
        
        # 3. INCREMENTO
        incremento_nodo = nodo.hijos[2]
        nodo_incremento = ASTNode("IncrementoFor", valor="", linea=incremento_nodo.linea, columna=incremento_nodo.columna)
        
        if incremento_nodo.hijos:
            for hijo in incremento_nodo.hijos:
                self.analizar(hijo, nodo_incremento)
        
        nodo_for.agregar_hijo(nodo_incremento)
        
        # 4. CUERPO
        cuerpo = nodo.hijos[3]
        nodo_cuerpo = ASTNode("CuerpoFor", valor="", linea=cuerpo.linea, columna=cuerpo.columna)
        
        for hijo in cuerpo.hijos:
            self.analizar(hijo, nodo_cuerpo)
        
        nodo_for.agregar_hijo(nodo_cuerpo)
        
        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_for)
        
        return nodo_for
    
    def analizar_cin(self, nodo: ASTNode, parent_tree_node=None):
        # Procesar todos los hijos: pueden ser cadenas de mensaje e identificador
        nodo_cin = ASTNode("Cin", valor="", linea=nodo.linea, columna=nodo.columna)
        
        identificador = None
        linea = nodo.linea
        columna = nodo.columna
        
        # Recorrer todos los hijos
        for hijo in nodo.hijos:
            if hijo.tipo == "cadena":
                # Es un mensaje, agregarlo al nodo cin
                nodo_cadena = ASTNode("cadena", valor=hijo.valor, linea=hijo.linea, columna=hijo.columna)
                nodo_cin.agregar_hijo(nodo_cadena)
            elif hijo.tipo == "identificador":
                # Es el identificador de la variable
                identificador = hijo.valor
                linea = hijo.linea
                columna = hijo.columna
        
        # Validar que existe el identificador
        if not identificador:
            self.errors.append(f"Error semántico: Se esperaba un identificador en cin. Línea {linea}")
            nodo.marcar_error()
            if parent_tree_node is not None:
                parent_tree_node.agregar_hijo(nodo_cin)
            return nodo_cin
        
        symbol = self.symbol_table.lookup(identificador)
        if not symbol:
            self.errors.append(f"Error semántico: La variable '{identificador}' no está declarada. Línea {linea}")
            nodo_id = ASTNode("ID("+identificador+")",id=str(identificador), valor="", linea=linea, columna=columna)
            nodo_id.tipo_dato = DataType.UNDEFINED
            nodo_cin.agregar_hijo(nodo_id)
            nodo.marcar_error()

            if parent_tree_node is not None:
                parent_tree_node.agregar_hijo(nodo_cin)
            return nodo_cin
        
        symbol.is_initialized = True
        # colocar valor por defecto segun el tipo
        if symbol.data_type == DataType.INT:
            symbol.value = 0
        elif symbol.data_type == DataType.FLOAT:
            symbol.value = 0.0
        elif symbol.data_type == DataType.STRING:
            symbol.value = ""
        elif symbol.data_type == DataType.BOOL:
            symbol.value = False
        self.symbol_table.update_lines(identificador, linea)
        symbol.use = True
        
        nodo_id = ASTNode("ID("+identificador+")",id=str(identificador), valor="", linea=linea, columna=columna)
        nodo_id.tipo_dato = symbol.data_type
        nodo_cin.agregar_hijo(nodo_id)
        
        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_cin)
        
        return nodo_cin
    
    def analizar_cout(self, nodo: ASTNode, parent_tree_node=None):
        for hijo in nodo.hijos:
            self.analizar(hijo, parent_tree_node)
        
        nodo_cout = ASTNode("Cout", valor="", linea=nodo.linea, columna=nodo.columna)
        for hijo in nodo.hijos:
            nodo_cout.agregar_hijo(hijo)
        
        if parent_tree_node is not None:
            parent_tree_node.agregar_hijo(nodo_cout)
        
        return nodo_cout

    def evaluar_expresion(self, nodo: ASTNode):
        # Solo procesar hijos si no son operaciones (para evitar recursión infinita)
        if nodo.tipo not in ["Operacion", "operacion", "OperacionComparacion", "Operacioncomparacion", "OperacionLogica", "Operacionlogica"]:
            for hijo in nodo.hijos:
                self.analizar(hijo)
        
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
    
    def agregar_nodo(self, tree, parent_id, nodo):
        tags = ["error"] if nodo.es_error else []
        
        texto = f"{nodo.tipo}"
        linea = getattr(nodo, "linea", "")
        columna = getattr(nodo, "columna", "")
        tipo = nodo.tipo_dato.value if nodo.tipo_dato else ""
        valor = nodo.valor if nodo.valor else ""
        
        node_id = tree.insert(
            parent_id, "end", text=texto,
            values=(tipo, valor, linea, columna), 
            open=True,
            tags=tags
        )
        
        for hijo in nodo.hijos:
            self.agregar_nodo(tree, node_id, hijo)