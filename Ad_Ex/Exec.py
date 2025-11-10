import tkinter as tk
from tkinter import ttk

class Exec(tk.Tk):
    def __init__(self):
        
        # Estado de las opciones
        self.var_semantico = False
        self.var_sintactico = False
        self.var_lexico = False
        self.var_errores = False

    def all_mark(self):
        """Marca todas las opciones si alguna no está marcada,
        desmarca todas si todas están marcadas."""
        if not (self.var_lexico and self.var_sintactico and self.var_semantico and self.var_errores):
            self.var_lexico = True
            self.var_sintactico = True
            self.var_semantico = True
            self.var_errores = True
        else:
            self.var_lexico = False
            self.var_sintactico = False
            self.var_semantico = False
            self.var_errores = False
