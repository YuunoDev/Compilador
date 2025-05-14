import tkinter as tk
from tkinter import font
import Anlex

def apply_syntax_highlighting(text_widget, tokens):
    """
    Apply syntax highlighting to a Tk Text widget based on a list of tokens.
    
    Args:
        text_widget: A Tk Text widget
        tokens: A list of tokens in the format (value, type, line, col)
    """
    # Clear any previous tags
    for tag in text_widget.tag_names():
        if tag != "sel":  # Don't remove selection tag
            text_widget.tag_remove(tag, "1.0", "end")
    
    # Define colors for different token types
    colors = {
        "COMENTARIO": "#5C6370",      # Gris azulado apagado, sutil pero visible
        "IDENTIFICADOR": "#C678DD",   # Lavanda suave, usado para variables
        "RESERVADA": "#61AFEF",        # Azul fuerte, común en palabras clave
        "OTRO": "#ABB2BF",            # Gris claro, para texto neutro o no categorizado
        "OPERADOR": "#56B6C2",        # Azul verdoso, bien contrastado
        "NUMERO ENTERO": "#D19A66",          # Naranja suave, típico para números
        "ASIGNACION": "#E5C07B",      # Amarillo dorado, resalta sin molestar
        "CADENA": "#98C379",          # Verde claro, ideal para cadenas
        "COMPARACION": "#56B6C2",     # Igual que operador para coherencia
        "SIMBOLO": "#61AFEF",         # Azul claro, resalta bien en fondos oscuros
        "LOGICO": "#BE5046",          # Rojo ladrillo, da contraste a los operadores lógicos
        "ERRORES": "#FF0000",          # Rojo brillante, para errores
        "NUMERO REAL": "#D19A66",     # Naranja suave, para números reales
    }
    
    # Create tags for each token type
    for token_type, color in colors.items():
        text_widget.tag_configure(token_type, foreground=color)
    
    # Apply highlighting for each token
    for token_value, token_type, line, col in tokens:
        try:
             # Calculate positions where col is the START of the token
            start_line = line
            start_col = col
            
            # Calculate the end position by adding the length of the token
            end_line = line
            end_col = col + len(token_value)
            
            # Convert to string format for Tkinter
            start_pos = f"{start_line}.{start_col}"
            end_pos = f"{end_line}.{end_col}"
            
            # Apply the tag - make sure the positions are valid
            text_widget.tag_add(token_type, start_pos, end_pos)
        except tk.TclError as e:
            print(f"Error highlighting token {token_value}: {e}")
            continue

def create_syntax_highlighter(parent_widget, tokens_list=None, initial_text=None):
    """
    Creates a syntax highlighting text widget with the given tokens list.
    
    Args:
        parent_widget: The parent widget to contain the text widget
        tokens_list: List of tokens in format (value, type, line, col)
        initial_text: Initial text to display
    
    Returns:
        A text widget with syntax highlighting capabilities
    """
    # Create a Text widget with a monospace font
    text_font = font.Font(family="Courier", size=12)
    text_widget = tk.Text(parent_widget, font=text_font)
    
    # Insert initial text if provided
    if initial_text:
        text_widget.insert("1.0", initial_text)
    
    # Apply syntax highlighting if tokens are provided
    if tokens_list:
        apply_syntax_highlighting(text_widget, tokens_list)
    
    return text_widget

def main():
    root = tk.Tk()
    root.title("Syntax Highlighter Demo")

    DFA = Anlex.Automata()
    
    # # Sample code
    with open("prov2.txt", "r", encoding="utf-8", errors="ignore") as file:
        code = file.read()

    DFA.process(code)
    #code = "int a;\n\na=12;\n\nint b=23;\n\nfloat bc=10.0;\n\nbool v=True;\n\nprint(\"a\");\n\nprint(\"Hola que tal\");\n\n//asdasdadsasd\nprint(1+3);"
    
    # Corrected tokens with proper positions
    # tokens = [
    #     ('int', 'RESERVADA', 1, 3), 
    #     ('a', 'IDENTIFICADOR', 1, 5), 
    #     (';', 'SIMBOLO', 1, 6), 
    #     ('a', 'IDENTIFICADOR', 3, 1), 
    #     ('=', 'ASIGNACION', 3, 2), 
    #     ('12', 'NUMERO ENTERO', 3, 4), 
    #     (';', 'SIMBOLO', 3, 5), 
    #     ('int', 'RESERVADA', 5, 3), 
    #     ('b', 'IDENTIFICADOR', 5, 5), 
    #     ('=', 'ASIGNACION', 5, 6), 
    #     ('23', 'NUMERO ENTERO', 5, 8), 
    #     (';', 'SIMBOLO', 5, 9), 
    #     ('float', 'RESERVADA', 7, 5), 
    #     ('bc', 'IDENTIFICADOR', 7, 8), 
    #     ('=', 'ASIGNACION', 7, 9), 
    #     ('10.0', 'NUMERO REAL', 7, 13), 
    #     (';', 'SIMBOLO', 7, 14), 
    #     ('bool', 'RESERVADA', 9, 4), 
    #     ('v', 'IDENTIFICADOR', 9, 6), 
    #     ('=', 'ASIGNACION', 9, 7), 
    #     ('True', 'RESERVADA', 9, 11), 
    #     (';', 'SIMBOLO', 9, 12), 
    #     ('print', 'IDENTIFICADOR', 11, 5), 
    #     ('(', 'SIMBOLO', 11, 6), 
    #     ('"', 'ERROR', 11, 7), 
    #     ('a', 'IDENTIFICADOR', 11, 8), 
    #     ('"', 'ERROR', 11, 9), 
    #     (')', 'SIMBOLO', 11, 10), 
    #     (';', 'SIMBOLO', 11, 11), 
    #     ('print', 'IDENTIFICADOR', 13, 5), 
    #     ('(', 'SIMBOLO', 13, 6), 
    #     ('"', 'ERROR', 13, 7), 
    #     ('Hola', 'IDENTIFICADOR', 13, 11), 
    #     ('que', 'IDENTIFICADOR', 13, 15), 
    #     ('tal', 'IDENTIFICADOR', 13, 19), 
    #     ('"', 'ERROR', 13, 20), 
    #     (')', 'SIMBOLO', 13, 21), 
    #     (';', 'SIMBOLO', 13, 22), 
    #     ('//asdasdadsasd', 'COMENTARIO', 15, 14), 
    #     ('print', 'IDENTIFICADOR', 16, 5), 
    #     ('(', 'SIMBOLO', 16, 6), 
    #     ('1', 'NUMERO ENTERO', 16, 7), 
    #     ('+', 'OPERADOR', 16, 8), 
    #     ('3', 'NUMERO ENTERO', 16, 9), 
    #     (')', 'SIMBOLO', 16, 10), 
    #     (';', 'SIMBOLO', 16, 11)
    # ]

    tokens = DFA.tokens
    
    # Create and pack the text widget
    text_widget = create_syntax_highlighter(root, tokens, code)
    text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Add a scrollbar
    scrollbar = tk.Scrollbar(root, command=text_widget.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.config(yscrollcommand=scrollbar.set)
    
    # Set minimum window size
    root.geometry("600x400")
    
    root.mainloop()

if __name__ == "__main__":
    main()