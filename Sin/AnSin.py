import re
from collections import namedtuple
from enum import Enum
from typing import List, Optional, Set
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

Token = namedtuple("Token", ["tipo", "lexema", "linea", "columna"])

class ErrorTipo(Enum):
    SINTACTICO = "Error Sintáctico"
    RECUPERACION = "Recuperación"

class Error:
    def __init__(self, tipo: ErrorTipo, mensaje: str, linea: int = 0, columna: int = 0, token: Optional[Token] = None):
        self.tipo = tipo
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        self.token = token
        
    def __str__(self):
        return f"{self.tipo.value} en línea {self.linea}, columna {self.columna}: {self.mensaje}"

def cargar_tokens_desde_archivo(ruta):
    tokens = []
    errores = []
    patron = re.compile(r'^(\w+(?:\s\w+)*)\s+(\S(?:.*\S)?)\s+\(línea (\d+), columna (\d+)\)$')
    
    try:
        with open(ruta, 'r', encoding="utf-8") as archivo:
            numero_linea = 0
            for linea in archivo:
                numero_linea += 1
                linea = linea.strip()
                if not linea:
                    continue
                    
                match = patron.match(linea)
                if match:
                    tipo, lexema, linea_num, columna_num = match.groups()
                    tokens.append(Token(tipo.strip(), lexema.strip(), int(linea_num), int(columna_num)))
                else:
                    errores.append(Error(
                        ErrorTipo.LEXICO, 
                        f"Formato de token inválido: {linea}", 
                        numero_linea, 0
                    ))
    except FileNotFoundError:
        errores.append(Error(ErrorTipo.LEXICO, f"Archivo no encontrado: {ruta}", 0, 0))
    except Exception as e:
        errores.append(Error(ErrorTipo.LEXICO, f"Error al leer archivo: {str(e)}", 0, 0))
    
    return tokens, errores

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
    
    def marcar_warning(self):
        self.es_warning = True

    def __repr__(self):
        return f"ASTNode(nom:{self.tipo}, val:{type(self.valor)}, linea:{self.linea})"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errores: List[Error] = []
        self.variables_declaradas: Set[str] = set()
        self.tokens_sincronizacion = {"SIMBOLO", "RESERVADA"}
        self.modo_panico = False
        
    def actual(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def siguiente(self) -> Optional[Token]:
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def consumir(self, tipo_esperado: Optional[str] = None) -> Optional[Token]:
        tok = self.actual()
        if tok is None:
            error = Error(
                ErrorTipo.SINTACTICO,
                "Fin inesperado del archivo",
                self.tokens[-1].linea if self.tokens else 0,
                self.tokens[-1].columna if self.tokens else 0
            )
            self.errores.append(error)
            return None
            
        if tipo_esperado and tok.tipo != tipo_esperado:
            error = Error(
                ErrorTipo.SINTACTICO,
                f"Esperado '{tipo_esperado}', encontrado '{tok.tipo}' ({tok.lexema})",
                tok.linea,
                tok.columna,
                tok
            )
            self.errores.append(error)
            
            if self.recuperar_hasta_token(tipo_esperado):
                return self.consumir(tipo_esperado)
            else:
                return Token("ERROR", f"Esperado_{tipo_esperado}", tok.linea, tok.columna)
        
        self.pos += 1
        return tok

    def recuperar_hasta_token(self, token_esperado: str) -> bool:
        inicio_pos = self.pos
        
        while self.actual() and self.pos < len(self.tokens):
            tok = self.actual()
            
            if tok.tipo == token_esperado:
                return True
                
            if tok.tipo in self.tokens_sincronizacion:
                self.errores.append(Error(
                    ErrorTipo.RECUPERACION,
                    f"Recuperación: saltando desde posición {inicio_pos} hasta {self.pos}",
                    tok.linea,
                    tok.columna
                ))
                return False
                
            self.pos += 1
            
        return False

    def sincronizar(self):
        while self.actual():
            tok = self.actual()
            
            if (tok.tipo == "SIMBOLO" and tok.lexema == ";") or \
               (tok.tipo == "RESERVADA" and tok.lexema in ["int", "float","bool", "char", "print", "if", "while", "do", "main", "end", "true", "false"]):
                self.pos += 1
                self.modo_panico = False
                return True
                
            self.pos += 1
            
        return False

    def validar_semantica(self, nodo: ASTNode):
        if nodo.tipo == "Asignacion" and len(nodo.hijos) >= 1:
            var_name = nodo.hijos[0].valor
            if var_name and var_name not in self.variables_declaradas:
                self.errores.append(Error(
                    ErrorTipo.SEMANTICO,
                    f"Variable '{var_name}' no declarada",
                    nodo.linea or 0,
                    nodo.columna or 0
                ))
                nodo.marcar_error()
        
        elif nodo.tipo == "Declaracion":
            if nodo.valor:
                parts = nodo.valor.split()
                if len(parts) >= 2:
                    # Manejar declaraciones múltiples como "int x, y, z"
                    tipo = parts[0]
                    vars_str = ' '.join(parts[1:])
                    variables = [v.strip().rstrip(',') for v in vars_str.split(',')]
                    
                    for var_name in variables:
                        if var_name in self.variables_declaradas:
                            nodo.marcar_error()
                        else:
                            self.variables_declaradas.add(var_name)

    def parse(self) -> ASTNode:
        root = ASTNode("Programa", "", 0, 0)
        
        # Verificar si hay main
        if self.actual() and self.actual().tipo == "RESERVADA" and self.actual().lexema == "main":
            main_node = self.parse_main()
            if main_node:
                root.agregar_hijo(main_node)
        else:
            # Parsing original sin main
            while self.actual():
                try:
                    if self.modo_panico:
                        if not self.sincronizar():
                            break
                            
                    tok = self.actual()
                    if not tok:
                        break
                        
                    nodo = self.parse_statement()
                    if nodo:
                        root.agregar_hijo(nodo)
                        
                except Exception as e:
                    tok = self.actual()
                    error = Error(
                        ErrorTipo.SINTACTICO,
                        f"Error interno del parser: {str(e)}",
                        tok.linea if tok else 0,
                        tok.columna if tok else 0,
                        tok
                    )
                    self.errores.append(error)
                    
                    if not self.sincronizar():
                        break
                        
        return root

    def parse_main(self) -> Optional[ASTNode]:
        """Parsea la estructura main { ... }"""
        try:
            main_tok = self.consumir("RESERVADA")  # main
            if not main_tok or main_tok.lexema != "main":
                return None
                
            llave_abrir = self.consumir("SIMBOLO")  # {
            if not llave_abrir or llave_abrir.lexema != "{":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '{' después de 'main'",
                    main_tok.linea,
                    main_tok.columna + len(main_tok.lexema)
                ))
            
            nodo = ASTNode("Main", linea=main_tok.linea, columna=main_tok.columna)
            
            # Parsear el cuerpo del main
            while self.actual() and not (self.actual().tipo == "SIMBOLO" and self.actual().lexema == "}"):
                statement = self.parse_statement()
                if statement:
                    nodo.agregar_hijo(statement)
            
            llave_cerrar = self.consumir("SIMBOLO")  # }
            if not llave_cerrar or llave_cerrar.lexema != "}":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '}' para cerrar main",
                    main_tok.linea,
                    main_tok.columna
                ))
            
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_statement(self) -> Optional[ASTNode]:
        """Parsea una declaración general"""
        tok = self.actual()
        if not tok:
            return None
            
        try:
            if tok.tipo == "RESERVADA":
                if tok.lexema == "print":
                    return self.parse_print()
                elif tok.lexema in ["int", "float", "char", "string", "bool"]:
                    nodo = self.parse_declaracion()
                    # if nodo:
                    #     self.validar_semantica(nodo)
                    return nodo
                elif tok.lexema == "if":
                    return self.parse_if()
                elif tok.lexema == "while":
                    return self.parse_while()
                elif tok.lexema == "do":
                    return self.parse_do_until()
                elif tok.lexema == "cin":
                    return self.parse_cin()
                elif tok.lexema == "cout":
                    return self.parse_cout()
                    
            elif tok.tipo == "IDENTIFICADOR":
                # Verificar si es incremento/decremento o asignación
                siguiente = self.siguiente()
                if siguiente and siguiente.tipo == "OPERADOR" and siguiente.lexema in ["++", "--"]:
                    return self.parse_incremento()
                else:
                    nodo = self.parse_asignacion()
                    # if nodo:
                    #     self.validar_semantica(nodo)
                    return nodo
                    
            else:
                # Token inesperado
                error = Error(
                    ErrorTipo.SINTACTICO,
                    f"Token inesperado: {tok.tipo} ({tok.lexema})",
                    tok.linea,
                    tok.columna,
                    tok
                )
                self.errores.append(error)
                
                nodo_error = ASTNode("Error", f"Token_inesperado: {tok.lexema}", tok.linea, tok.columna)
                nodo_error.marcar_error()
                
                self.pos += 1
                self.modo_panico = True
                
                return nodo_error
                
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_declaracion(self) -> Optional[ASTNode]:
        try:
            tipo = self.consumir("RESERVADA")
            if not tipo:
                return None
                
            # Manejar declaraciones múltiples: int x, y, z;
            variables = []
            
            # Primera variable
            ident = self.consumir("IDENTIFICADOR")
            if not ident:
                return None
            variables.append(ident.lexema)
            
            # Variables adicionales separadas por comas
            while self.actual() and self.actual().tipo == "SIMBOLO" and self.actual().lexema == ",":
                self.consumir("SIMBOLO")  # consumir ","
                ident = self.consumir("IDENTIFICADOR")
                if ident:
                    variables.append(ident.lexema)
            
            nodo = ASTNode("Declaracion", f"{tipo.lexema}",
                          linea=tipo.linea, columna=tipo.columna)
            nodo.agregar_hijo(ASTNode("identificador", f"{', '.join(variables)}",
                          linea=tipo.linea, columna=tipo.columna))

            # Verificar si hay asignación inicial (solo para una variable)
            if self.actual() and self.actual().tipo == "ASIGNACION":
                self.consumir("ASIGNACION")
                nodo_asig = ASTNode("Asignacion", " ", linea=" ", columna=" ")
                nodo_asig.agregar_hijo(ASTNode("identificador", variables[0], linea=tipo.linea, columna=tipo.columna))
                
                expr = self.parse_expresion()
                if expr:
                    nodo_asig.agregar_hijo(expr)
                    nodo.agregar_hijo(nodo_asig)
            
            # Consumir punto y coma
            punto_coma = self.consumir("SIMBOLO")
            if not punto_coma or punto_coma.lexema != ";":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ';' después de la declaración",
                    tipo.linea,
                    tipo.columna + len(tipo.lexema)
                ))
                
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_if(self) -> Optional[ASTNode]:
        """Parsea estructura if-else con end"""
        try:
            if_tok = self.consumir("RESERVADA")  # if
            
            paren_abrir = self.consumir("SIMBOLO")  # (
            if not paren_abrir or paren_abrir.lexema != "(":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '(' después de 'if'",
                    if_tok.linea,
                    if_tok.columna + len(if_tok.lexema)
                ))
            
            condicion = self.parse_expresion_completa()
            
            paren_cerrar = self.consumir("SIMBOLO")  # )
            if not paren_cerrar or paren_cerrar.lexema != ")":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ')' después de la condición",
                    if_tok.linea,
                    if_tok.columna
                ))
            
            nodo = ASTNode("If", linea=if_tok.linea, columna=if_tok.columna)
            if condicion:
                nodo.agregar_hijo(condicion)
            
            # Cuerpo del if
            cuerpo_if = ASTNode("CuerpoIf", " ", linea=" ", columna=" ")
            while self.actual() and not (self.actual().tipo == "RESERVADA" and self.actual().lexema in ["else", "end"]):
                statement = self.parse_statement()
                if statement:
                    cuerpo_if.agregar_hijo(statement)
            nodo.agregar_hijo(cuerpo_if)
            
            # Verificar else
            if self.actual() and self.actual().tipo == "RESERVADA" and self.actual().lexema == "else":
                self.consumir("RESERVADA")  # else
                cuerpo_else = ASTNode("CuerpoElse", " ", linea=" ", columna=" ")
                
                while self.actual() and not (self.actual().tipo == "RESERVADA" and self.actual().lexema == "end"):
                    statement = self.parse_statement()
                    if statement:
                        cuerpo_else.agregar_hijo(statement)
                nodo.agregar_hijo(cuerpo_else)
            
            # Consumir end
            end_tok = self.consumir("RESERVADA")
            if not end_tok or end_tok.lexema != "end":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba 'end' para cerrar if",
                    if_tok.linea,
                    if_tok.columna
                ))
            
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_while(self) -> Optional[ASTNode]:
        """Parsea estructura while con end"""
        try:
            while_tok = self.consumir("RESERVADA")  # while
            
            paren_abrir = self.consumir("SIMBOLO")  # (
            if not paren_abrir or paren_abrir.lexema != "(":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '(' después de 'while'",
                    while_tok.linea,
                    while_tok.columna + len(while_tok.lexema)
                ))
            
            condicion = self.parse_expresion_completa()
            
            paren_cerrar = self.consumir("SIMBOLO")  # )
            if not paren_cerrar or paren_cerrar.lexema != ")":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ')' después de la condición",
                    while_tok.linea,
                    while_tok.columna
                ))
            
            nodo = ASTNode("While", linea=while_tok.linea, columna=while_tok.columna)
            if condicion:
                nodo.agregar_hijo(condicion)
            
            # Cuerpo del while
            cuerpo = ASTNode("CuerpoWhile", " ", linea=" ", columna=" ")
            while self.actual() and not (self.actual().tipo == "RESERVADA" and self.actual().lexema == "end"):
                statement = self.parse_statement()
                if statement:
                    cuerpo.agregar_hijo(statement)
            nodo.agregar_hijo(cuerpo)
            
            # Consumir end
            end_tok = self.consumir("RESERVADA")
            if not end_tok or end_tok.lexema != "end":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba 'end' para cerrar while",
                    while_tok.linea,
                    while_tok.columna
                ))
            
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_do_until(self) -> Optional[ASTNode]:
        """Parsea estructura do-until"""
        try:
            do_tok = self.consumir("RESERVADA")  # do
            
            nodo = ASTNode("DoUntil", linea=do_tok.linea, columna=do_tok.columna)
            
            # Cuerpo del do
            cuerpo = ASTNode("CuerpoDo", " ", linea=" ", columna=" ")
            while self.actual() and not (self.actual().tipo == "RESERVADA" and self.actual().lexema == "until"):
                statement = self.parse_statement()
                if statement:
                    cuerpo.agregar_hijo(statement)
            nodo.agregar_hijo(cuerpo)
            
            # Consumir until
            until_tok = self.consumir("RESERVADA")
            if not until_tok or until_tok.lexema != "until":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba 'until' después del cuerpo do",
                    do_tok.linea,
                    do_tok.columna
                ))
            
            # Condición del until
            paren_abrir = self.consumir("SIMBOLO")  # (
            if not paren_abrir or paren_abrir.lexema != "(":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '(' después de 'until'",
                    do_tok.linea,
                    do_tok.columna
                ))
            
            condicion = self.parse_expresion_completa()
            if condicion:
                nodo.agregar_hijo(condicion)
            
            paren_cerrar = self.consumir("SIMBOLO")  # )
            if not paren_cerrar or paren_cerrar.lexema != ")":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ')' después de la condición until",
                    do_tok.linea,
                    do_tok.columna
                ))
            
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_incremento(self) -> Optional[ASTNode]:
        """Parsea operadores ++ y --"""
        try:
            ident = self.consumir("IDENTIFICADOR")
            op = self.consumir("OPERADOR")
            
            punto_coma = self.consumir("SIMBOLO")
            if not punto_coma or punto_coma.lexema != ";":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ';' después del incremento/decremento",
                    ident.linea,
                    ident.columna
                ))

            nodo = ASTNode("Incremento ++" if op.lexema == "++" else "Decremento --", 
                          linea=ident.linea, columna=ident.columna)
            #nodo asignación
            nodo_asig = ASTNode("Asignacion", " ", linea=ident.linea, columna=ident.columna)
            nodo_asig.agregar_hijo(ASTNode("identificador", ident.lexema, linea=ident.linea, columna=ident.columna))
            nodo.agregar_hijo(nodo_asig)

            # agregar operador
            nodoop = ASTNode("Operacion", "+" if op.lexema == "++" else "-", linea=ident.linea, columna=ident.columna)
            nodo_asig.agregar_hijo(nodoop)
            nodoop.agregar_hijo(ASTNode("identificador", ident.lexema, linea=ident.linea, columna=ident.columna))
            nodoop.agregar_hijo(ASTNode("entero", "1", linea=op.linea, columna=op.columna))

            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_cin(self) -> Optional[ASTNode]:
        """Parsea cin >> variable;"""
        try:
            cin_tok = self.consumir("RESERVADA")  # cin
            
            simbolo = self.consumir("SIMBOLO")  # >>
            if not simbolo or simbolo.lexema != ">>":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '>>' después de 'cin'",
                    cin_tok.linea,
                    cin_tok.columna
                ))
            
            variable = self.consumir("IDENTIFICADOR")
            if not variable:
                return None
            
            punto_coma = self.consumir("SIMBOLO")
            if not punto_coma or punto_coma.lexema != ";":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ';' después de cin",
                    cin_tok.linea,
                    cin_tok.columna
                ))
            
            nodo = ASTNode("Cin", linea=cin_tok.linea, columna=cin_tok.columna)
            nodo.agregar_hijo(ASTNode("identificador", variable.lexema, linea=variable.linea, columna=variable.columna))
            
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_cout(self) -> Optional[ASTNode]:
        """Parsea cout << expresion;"""
        try:
            cout_tok = self.consumir("RESERVADA")  # cout
            
            simbolo = self.consumir("SIMBOLO")  # <<
            if not simbolo or simbolo.lexema != "<<":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '<<' después de 'cout'",
                    cout_tok.linea,
                    cout_tok.columna
                ))
            
            expresion = self.parse_expresion()
            
            punto_coma = self.consumir("SIMBOLO")
            if not punto_coma or punto_coma.lexema != ";":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ';' después de cout",
                    cout_tok.linea,
                    cout_tok.columna
                ))
            
            nodo = ASTNode("Cout", linea=cout_tok.linea, columna=cout_tok.columna)
            if expresion:
                nodo.agregar_hijo(expresion)
            
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_expresion_completa(self) -> Optional[ASTNode]:
        """Parsea expresiones con operadores lógicos y relacionales"""
        try:
            izquierda = self.parse_expresion()
            if not izquierda:
                return None
            
            
            # Verificar operadores relacionales y lógicos
            while self.actual() and self.actual().tipo == "COMPARACION" and \
                  self.actual().lexema in [">", "<", ">=", "<=", "==", "!="] or  (self.actual().tipo == "LOGICO" and self.actual().lexema in ["&&", "||"]):
                if self.actual().tipo == "LOGICO":
                    op = self.consumir("LOGICO")
                else:
                    op = self.consumir("COMPARACION")
                derecha = self.parse_expresion()
                
                if op and derecha:
                    if op.lexema in [">", "<", ">=", "<=", "==", "!="]:
                        nodo = ASTNode("OperacionComparacion", op.lexema, linea=op.linea, columna=op.columna)
                    else:
                        nodo = ASTNode("OperacionLogica", op.lexema, linea=op.linea, columna=op.columna)
                    nodo.agregar_hijo(izquierda)
                    nodo.agregar_hijo(derecha)
                    izquierda = nodo
                else:
                    break
            
            return izquierda
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_asignacion(self) -> Optional[ASTNode]:
        try:
            ident = self.consumir("IDENTIFICADOR")
            if not ident:
                return None
                
            self.consumir("ASIGNACION")
            valor = self.parse_expresion_completa()
            
            punto_coma = self.consumir("SIMBOLO")
            if not punto_coma or punto_coma.lexema != ";":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ';' después de la asignación",
                    ident.linea,
                    ident.columna + len(ident.lexema)
                ))
            
            nodo = ASTNode("Asignacion"," ", linea=" ", columna=" ")
            nodo.agregar_hijo(ASTNode("identificador", ident.lexema, linea=ident.linea, columna=ident.columna))
            if valor:
                nodo.agregar_hijo(valor)
                
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_expresion(self) -> Optional[ASTNode]:
        """Parsea expresiones aritméticas con precedencia"""
        try:
            return self.parse_termino()
        except Exception as e:
            self.modo_panico = True
            return None

    def parse_termino(self) -> Optional[ASTNode]:
        """Parsea términos (suma y resta)"""
        izquierda = self.parse_factor()
        
        while self.actual() and self.actual().tipo == "OPERADOR" and \
              self.actual().lexema in ["+", "-"]:
            op = self.consumir("OPERADOR")
            derecha = self.parse_factor()
            
            if op and derecha:
                nodo = ASTNode("Operacion", op.lexema, linea=op.linea, columna=op.columna)
                nodo.agregar_hijo(izquierda if izquierda else ASTNode("Error"))
                nodo.agregar_hijo(derecha)
                izquierda = nodo
        
        return izquierda

    def parse_factor(self) -> Optional[ASTNode]:
        """Parsea factores (multiplicación y división)"""
        izquierda = self.parse_primario()
        
        while self.actual() and self.actual().tipo == "OPERADOR" and \
              self.actual().lexema in ["*", "/"]:
            op = self.consumir("OPERADOR")
            derecha = self.parse_primario()
            
            if op and derecha:
                nodo = ASTNode("Operacion", op.lexema, linea=op.linea, columna=op.columna)
                nodo.agregar_hijo(izquierda if izquierda else ASTNode("Error"))
                nodo.agregar_hijo(derecha)
                izquierda = nodo
        
        return izquierda

    def parse_primario(self) -> Optional[ASTNode]:
        """Parsea elementos primarios (números, variables, paréntesis)"""
        tok = self.actual()
        if not tok:
            return None
        
        # Paréntesis
        if tok.tipo == "SIMBOLO" and tok.lexema == "(":
            self.consumir("SIMBOLO")  # (
            expr = self.parse_expresion_completa()
            paren_cerrar = self.consumir("SIMBOLO")  # )
            if not paren_cerrar or paren_cerrar.lexema != ")":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ')' para cerrar expresión",
                    tok.linea,
                    tok.columna
                ))
            return expr
        
        # Números, identificadores, booleanos
        #elif tok.tipo in ["NUMERO ENTERO", "NUMERO REAL", "IDENTIFICADOR", "BOOLEANO"]:
        elif tok.tipo == "NUMERO ENTERO":
            token = self.consumir()
            return ASTNode("entero", token.lexema, linea=token.linea, columna=token.columna)   
        
        elif tok.tipo == "NUMERO REAL":
            token = self.consumir()
            return ASTNode("flotante", token.lexema, linea=token.linea, columna=token.columna)

        elif tok.tipo == "BOOLEANO":
            token = self.consumir()
            return ASTNode("booleano", str(token.lexema), linea=token.linea, columna=token.columna)

        elif tok.tipo == "IDENTIFICADOR":
            token = self.consumir()
            return ASTNode("identificador", token.lexema, linea=token.linea, columna=token.columna)

        else:
            # Token no reconocido en expresión
            self.errores.append(Error(
                ErrorTipo.SINTACTICO,
                f"Token inesperado en expresión: {tok.tipo} ({tok.lexema})",
                tok.linea,
                tok.columna
            ))
            self.pos += 1  # Saltar token problemático
            return ASTNode("Error", f"Token_inesperado: {tok.lexema}", tok.linea, tok.columna)

    def parse_print(self) -> Optional[ASTNode]:
        try:
            print_tok = self.consumir("RESERVADA")  # print
            if not print_tok:
                return None
                
            paren_abrir = self.consumir("SIMBOLO")  # (
            if not paren_abrir or paren_abrir.lexema != "(":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba '(' después de 'print'",
                    print_tok.linea,
                    print_tok.columna + len(print_tok.lexema)
                ))
            
            contenido = self.parse_expresion()
            
            paren_cerrar = self.consumir("SIMBOLO")  # )
            if not paren_cerrar or paren_cerrar.lexema != ")":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ')' para cerrar print",
                    print_tok.linea,
                    print_tok.columna + len(print_tok.lexema)
                ))
            
            punto_coma = self.consumir("SIMBOLO")  # ;
            if not punto_coma or punto_coma.lexema != ";":
                self.errores.append(Error(
                    ErrorTipo.SINTACTICO,
                    "Se esperaba ';' después de print",
                    print_tok.linea,
                    print_tok.columna + len(print_tok.lexema)
                ))
            
            nodo = ASTNode("Print", linea=print_tok.linea, columna=print_tok.columna)
            if contenido:
                nodo.agregar_hijo(contenido)
                
            return nodo
            
        except Exception as e:
            self.modo_panico = True
            return None
        
def agregar_nodo(tree, parent_id, nodo):
        # Determinar el color del texto basado en si hay errores
        tags = ["error"] if nodo.es_error else []
        
        texto = f"{nodo.tipo}"
        linea = getattr(nodo, "linea", "")
        columna = getattr(nodo, "columna", "")
        valor = nodo.valor if nodo.valor else ""

        #print(nodo.__repr__())
        
        node_id = tree.insert(
            parent_id, "end", text=texto,
            values=(valor, linea, columna), 
            open=True,
            tags=tags
        )
        
        for hijo in nodo.hijos:
            agregar_nodo(tree, node_id, hijo)

def mostrar_ast_y_errores(ast: ASTNode, errores: List[Error]):
    
    root = tk.Tk()
    root.title("Analizador Sintáctico con Recuperación de Errores - Versión Extendida")
    root.geometry("1200x800")
    
    # Crear notebook para pestañas
    notebook = ttk.Notebook(root)
    
    # Pestaña del AST
    frame_ast = ttk.Frame(notebook)
    notebook.add(frame_ast, text="Árbol de Sintaxis")
    
    # Configurar Treeview
    tree = ttk.Treeview(frame_ast, columns=("Valor", "Línea", "Columna"), show="tree headings")
    
    # Configurar colores para errores
    tree.tag_configure("error", foreground="red")
    
    # Encabezados
    tree.heading("#0", text="Nodo")
    tree.heading("Valor", text="Valor")
    tree.heading("Línea", text="Línea")
    tree.heading("Columna", text="Columna")
    
    # Ajustes de columnas
    tree.column("#0", width=200, anchor="w")
    tree.column("Valor", width=200, anchor="w")
    tree.column("Línea", width=60, anchor="center")
    tree.column("Columna", width=70, anchor="center")
    
    # Scrollbar para el tree
    scrollbar_tree = ttk.Scrollbar(frame_ast, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_tree.set)
    
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar_tree.grid(row=0, column=1, sticky="ns")
    
    frame_ast.grid_rowconfigure(0, weight=1)
    frame_ast.grid_columnconfigure(0, weight=1)
    
    # Pestaña de errores
    frame_errores = ttk.Frame(notebook)
    notebook.add(frame_errores, text=f"Errores ({len(errores)})")
    
    # Área de texto para mostrar errores
    texto_errores = scrolledtext.ScrolledText(frame_errores, wrap=tk.WORD, width=80, height=30)
    texto_errores.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Configurar colores para diferentes tipos de errores
    texto_errores.tag_configure("sintactico", foreground="red")
    texto_errores.tag_configure("semantico", foreground="orange")
    texto_errores.tag_configure("lexico", foreground="purple")
    texto_errores.tag_configure("recuperacion", foreground="blue")
    
    # Pestaña de estadísticas
    frame_stats = ttk.Frame(notebook)
    notebook.add(frame_stats, text="Estadísticas")
    
    stats_text = scrolledtext.ScrolledText(frame_stats, wrap=tk.WORD, width=80, height=30)
    stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Mostrar errores
    if errores:
        for i, error in enumerate(errores, 1):
            tag = error.tipo.name.lower()
            texto_errores.insert(tk.END, f"{i}. {error}\n", tag)
    else:
        texto_errores.insert(tk.END, "¡No se encontraron errores! ✓", "success")
        texto_errores.tag_configure("success", foreground="green")
    
    # Mostrar estadísticas
    def contar_nodos(nodo: ASTNode):
        count = {"total": 0, "errores": 0, "por_tipo": {}}
        
        def contar_recursivo(n):
            count["total"] += 1
            if n.es_error:
                count["errores"] += 1
            
            tipo = n.tipo
            count["por_tipo"][tipo] = count["por_tipo"].get(tipo, 0) + 1
            
            for hijo in n.hijos:
                contar_recursivo(hijo)
        
        contar_recursivo(nodo)
        return count
    
    stats = contar_nodos(ast)
    
    stats_text.insert(tk.END, "=== ESTADÍSTICAS DEL ANÁLISIS ===\n\n")
    stats_text.insert(tk.END, f"Nodos totales en el AST: {stats['total']}\n")
    stats_text.insert(tk.END, f"Nodos con errores: {stats['errores']}\n")
    stats_text.insert(tk.END, f"Errores totales detectados: {len(errores)}\n\n")
    
    stats_text.insert(tk.END, "=== TIPOS DE NODOS ===\n")
    for tipo, cantidad in sorted(stats['por_tipo'].items()):
        stats_text.insert(tk.END, f"{tipo}: {cantidad}\n")
    
    stats_text.insert(tk.END, "\n=== TIPOS DE ERRORES ===\n")
    errores_por_tipo = {}
    for error in errores:
        errores_por_tipo[error.tipo.name] = errores_por_tipo.get(error.tipo.name, 0) + 1
    
    for tipo, cantidad in sorted(errores_por_tipo.items()):
        stats_text.insert(tk.END, f"{tipo}: {cantidad}\n")
    
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Agregar el AST al tree
    agregar_nodo(tree, '', ast)


    
    # Estadísticas en la barra de estado
    frame_estado = ttk.Frame(root)
    frame_estado.pack(fill=tk.X, side=tk.BOTTOM)
    
    estado_texto = f"Nodos: {stats['total']} | Errores: {len(errores)}"
    if errores_por_tipo:
        detalles = [f"{tipo}: {cantidad}" for tipo, cantidad in errores_por_tipo.items()]
        estado_texto += f" | {' | '.join(detalles)}"
    
    label_estado = ttk.Label(frame_estado, text=estado_texto)
    label_estado.pack(pady=5)
    
    root.mainloop()

def programain():
    # Cargar tokens y manejar errores de lectura
    tokens, errores_lexicos = cargar_tokens_desde_archivo("token.tk")
    
    if errores_lexicos:
        print("Errores encontrados al cargar tokens:")
        for error in errores_lexicos:
            print(f"  {error}")
    
    if not tokens:
        print("No se encontraron tokens válidos en el archivo.")
        # Mostrar solo los errores léxicos si no hay tokens
        mostrar_ast_y_errores(ASTNode("Programa_Vacío"), errores_lexicos)
    else:
        print(f"Se cargaron {len(tokens)} tokens exitosamente.")
        
        # Crear parser y analizar
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Combinar errores léxicos y de parsing
        todos_errores = errores_lexicos + parser.errores
        
        # Mostrar resultados
        print(f"\nAnálisis completado:")
        print(f"  - Errores encontrados: {len(todos_errores)}")
        print(f"  - Variables declaradas: {parser.variables_declaradas}")
        
        # Mostrar nuevas construcciones detectadas
        def contar_construcciones(nodo):
            construcciones = {}
            def contar(n):
                if n.tipo in ["Main", "If", "While", "DoUntil", "Cin", "Cout", "Incremento", "Decremento"]:
                    construcciones[n.tipo] = construcciones.get(n.tipo, 0) + 1
                for hijo in n.hijos:
                    contar(hijo)
            contar(nodo)
            return construcciones
        
        construcciones = contar_construcciones(ast)
        if construcciones:
            print(f"  - Nuevas construcciones detectadas:")
            for const, cant in construcciones.items():
                print(f"    * {const}: {cant}")
        
        # Mostrar interfaz gráfica
        mostrar_ast_y_errores(ast, todos_errores)

    

if __name__ == "__main__":
    programain()