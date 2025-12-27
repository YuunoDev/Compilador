import sys

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