"""Clase para administrar la ejecucion, si solo se compilara o se ejecuta el codigo, o los dos"""
class Exec:
    def __init__(self):
        self.modo = 'compilar_ejecutar'  # Por defecto: compilar y ejecutar
        # Modos disponibles: 'compilar', 'ejecutar', 'compilar_ejecutar'

    def setModo(self, modo):
        """
        Establece el modo de ejecución.
        Modos disponibles:
        - 'compilar': Solo compila (análisis léxico, sintáctico y semántico)
        - 'ejecutar': Solo ejecuta (requiere que ya esté compilado)
        - 'compilar_ejecutar': Compila y ejecuta
        """
        if modo in ['compilar', 'ejecutar', 'compilar_ejecutar']:
            self.modo = modo
        else:
            print(f"Modo inválido: {modo}. Usando 'compilar_ejecutar' por defecto.")
            self.modo = 'compilar_ejecutar'

    def getModo(self):
        """Retorna el modo de ejecución actual"""
        return self.modo

    def esCompilacion(self):
        """Retorna True si se debe compilar"""
        return self.modo in ['compilar', 'compilar_ejecutar']

    def esEjecucion(self):
        """Retorna True si se debe ejecutar"""
        return self.modo in ['ejecutar', 'compilar_ejecutar']
    