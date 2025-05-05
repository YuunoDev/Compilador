import tkinter as tk
from tkinter import font
from Anlex import *

def colorear_tokens(texto_entrada, resultado_automata):
    """
    Colorea tokens en un widget Text de Tkinter
    
    Args:
        texto_entrada (str): El código fuente original
        resultado_automata (list): Lista de tuplas (Token, Tipo)
    """
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Coloreador de Tokens")
    root.geometry("800x600")
    
    # Crear un widget Text con fuente monoespaciada
    text_font = font.Font(family="Courier", size=12)
    text_widget = tk.Text(root, wrap="word", font=text_font)
    text_widget.pack(expand=True, fill="both", padx=10, pady=10)
    
    # Insertar el texto original
    text_widget.insert("1.0", texto_entrada)
    
    # Definir colores para cada tipo de token
    colores = {
        "IDENTIFICADOR": "#C678DD",   # Lavanda suave, usado para variables
        "OTRO": "#ABB2BF",            # Gris claro, para texto neutro o no categorizado
        "OPERADOR": "#56B6C2",        # Azul verdoso, bien contrastado
        "NUMERO": "#D19A66",          # Naranja suave, típico para números
        "ASIGNACION": "#E5C07B",      # Amarillo dorado, resalta sin molestar
        "CADENA": "#98C379",          # Verde claro, ideal para cadenas
        "COMENTARIO": "#5C6370",      # Gris azulado apagado, sutil pero visible
        "COMPARACION": "#56B6C2",     # Igual que operador para coherencia
        "SIMBOLO": "#61AFEF",         # Azul claro, resalta bien en fondos oscuros
        "LOGICO": "#BE5046",          # Rojo ladrillo, da contraste a los operadores lógicos
        "RESERVADA": "#61AFEF"        # Azul fuerte, común en palabras clave
    }

    
    # Crear tags para cada tipo de token
    for tipo, color in colores.items():
        text_widget.tag_configure(tipo, foreground=color)
    
    # Colorear tokens en el texto
    for token, tipo in resultado_automata:
        if tipo in colores:
            # Buscar todas las ocurrencias del token en el texto
            start_index = "1.0"
            while True:
                start_index = text_widget.search(token, start_index, stopindex="end", exact=True)
                if not start_index:
                    break
                
                end_index = f"{start_index}+{len(token)}c"
                text_widget.tag_add(tipo, start_index, end_index)
                start_index = end_index
    
    # Hacer que el texto sea de solo lectura
    text_widget.config(state="disabled")
    
    # Agregar scrollbar
    scrollbar = tk.Scrollbar(root, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar.set)
    
    # Crear leyenda de colores
    frame_leyenda = tk.Frame(root)
    frame_leyenda.pack(fill="x", padx=10, pady=5)
    
    tk.Label(frame_leyenda, text="Leyenda:").pack(side="left", padx=5)
    
    for tipo, color in colores.items():
        frame = tk.Frame(frame_leyenda, bg=color, width=15, height=15)
        frame.pack(side="left", padx=2)
        tk.Label(frame_leyenda, text=tipo).pack(side="left", padx=2)
    
    root.mainloop()

DFA = Automata()


# Ejemplo de uso
with open("Lex/prov2.txt", "r", encoding="utf-8", errors="ignore") as file:
    code = file.read()

DFA.process(code)


colorear_tokens(code, DFA.tokens)