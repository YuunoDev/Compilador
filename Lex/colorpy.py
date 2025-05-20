import tkinter as tk
from tkinter import font
from Anlex import Automata

def apply_syntax_highlighting(text_widget, tokens):
    """
    Apply syntax highlighting to a Tk Text widget based on a list of tokens.
    
    Args:
        text_widget: A Tk Text widget
        tokens: A list of tokens in the format (value, type, line, col)
        
    Note: col represents the starting position of the token
    """
    # Clear any previous tags
    for tag in text_widget.tag_names():
        if tag != "sel":  # Don't remove selection tag
            text_widget.tag_remove(tag, "1.0", "end")
    
    # Define colors for different token types
    colors = {
        "RESERVADA": "#0000FF",       # Blue for reserved keywords
        "IDENTIFICADOR": "#000000",   # Black for identifiers
        "NUMERO ENTERO": "#FF6600",   # Orange for integers
        "NUMERO REAL": "#FF6600",     # Orange for floats
        "SIMBOLO": "#666666",         # Gray for symbols
        "ASIGNACION": "#666666",      # Gray for assignment
        "OPERADOR": "#666666",        # Gray for operators
        "COMENTARIO": "#008800",      # Green for comments
        "ERROR": "#FF0000"            # Red for errors
    }
    
    # Create tags for each token type
    for token_type, color in colors.items():
        text_widget.tag_configure(token_type, foreground=color)
    
    # Apply highlighting for each token
    for token_value, token_type, line, col in tokens:
        try:
            # Handle multiline tokens (like multiline comments)
            if '\n' in token_value:
                # Split the token value by newline
                lines = token_value.split('\n')
                
                # Process the first line
                start_line = line
                start_col = col
                end_line = line
                end_col = len(lines[0])  # End of first line
                
                start_pos = f"{start_line}.{start_col}"
                end_pos = f"{end_line}.{end_col}"
                text_widget.tag_add(token_type, start_pos, end_pos)
                
                # Process middle lines (if any)
                for i in range(1, len(lines) - 1):
                    curr_line = line + i
                    text_widget.tag_add(token_type, f"{curr_line}.0", f"{curr_line}.{len(lines[i])}")
                
                # Process the last line
                if len(lines) > 1:
                    last_line = line + len(lines) - 1
                    last_line_length = len(lines[-1])
                    text_widget.tag_add(token_type, f"{last_line}.0", f"{last_line}.{last_line_length}")
            else:
                # Standard single-line token handling
                start_line = line
                start_col = col
                
                # Calculate the end position by adding the length of the token
                end_line = line
                end_col = col + len(token_value)
                
                # Convert to string format for Tkinter
                start_pos = f"{start_line}.{start_col}"
                end_pos = f"{end_line}.{end_col}"
                
                # Apply the tag
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


    
    # Sample code with multiline comment
    # code = "int a;\n\na=12;\n\nint b=23;\n\nif (a == b) {\n    print(\"Equal\");\n}\n\n/* Este es un\ncomentario de\nmúltiples líneas */\n\nfloat bc=10.0;\n\nbool v=True;\n\nprint(\"a\");\n\nprint(\"Hola que tal\");\n\n//asdasdadsasd\nprint(1+3);"
    
    # Tokens with positions at the START of each token
    #tokens = [
    #     ('int', 'RESERVADA', 1, 0), 
    #     ('a', 'IDENTIFICADOR', 1, 4), 
    #     (';', 'SIMBOLO', 1, 5), 
    #     ('a', 'IDENTIFICADOR', 3, 0), 
    #     ('=', 'ASIGNACION', 3, 1), 
    #     ('12', 'NUMERO ENTERO', 3, 2), 
    #     (';', 'SIMBOLO', 3, 4), 
    #     ('int', 'RESERVADA', 5, 0), 
    #     ('b', 'IDENTIFICADOR', 5, 4), 
    #     ('=', 'ASIGNACION', 5, 5), 
    #     ('23', 'NUMERO ENTERO', 5, 6), 
    #     (';', 'SIMBOLO', 5, 8),
    #     ('if', 'RESERVADA', 7, 0),
    #     ('(', 'SIMBOLO', 7, 3),
    #     ('a', 'IDENTIFICADOR', 7, 4),
    #     ('==', 'OPERADOR', 7, 6),
    #     ('b', 'IDENTIFICADOR', 7, 9),
    #     (')', 'SIMBOLO', 7, 10),
    #     ('{', 'SIMBOLO', 7, 12),
    #     ('print', 'IDENTIFICADOR', 8, 4),
    #     ('(', 'SIMBOLO', 8, 9),
    #     ('"', 'ERROR', 8, 10),
    #     ('Equal', 'IDENTIFICADOR', 8, 11),
    #     ('"', 'ERROR', 8, 16),
    #     (')', 'SIMBOLO', 8, 17),
    #     (';', 'SIMBOLO', 8, 18),
    #     ('}', 'SIMBOLO', 9, 0),
    #     ('/* Este es un\ncomentario de\nmúltiples líneas */', 'COMENTARIO', 11, 0),  # Comentario multilínea
    #     ('float', 'RESERVADA', 15, 0), 
    #     ('bc', 'IDENTIFICADOR', 15, 6), 
    #     ('=', 'ASIGNACION', 15, 8), 
    #     ('10.0', 'NUMERO REAL', 15, 9), 
    #     (';', 'SIMBOLO', 15, 13), 
    #     ('bool', 'RESERVADA', 17, 0), 
    #     ('v', 'IDENTIFICADOR', 17, 5), 
    #     ('=', 'ASIGNACION', 17, 6), 
    #     ('True', 'RESERVADA', 17, 7), 
    #     (';', 'SIMBOLO', 17, 11), 
    #     ('print', 'IDENTIFICADOR', 19, 0), 
    #     ('(', 'SIMBOLO', 19, 5), 
    #     ('"', 'ERROR', 19, 6), 
    #     ('a', 'IDENTIFICADOR', 19, 7), 
    #     ('"', 'ERROR', 19, 8), 
    #     (')', 'SIMBOLO', 19, 9), 
    #     (';', 'SIMBOLO', 19, 10), 
    #     ('print', 'IDENTIFICADOR', 21, 0), 
    #     ('(', 'SIMBOLO', 21, 5), 
    #     ('"', 'ERROR', 21, 6), 
    #     ('Hola', 'IDENTIFICADOR', 21, 7), 
    #     ('que', 'IDENTIFICADOR', 21, 12), 
    #     ('tal', 'IDENTIFICADOR', 21, 16), 
    #     ('"', 'ERROR', 21, 19), 
    #     (')', 'SIMBOLO', 21, 20), 
    #     (';', 'SIMBOLO', 21, 21), 
    #     ('//asdasdadsasd', 'COMENTARIO', 23, 0), 
    #     ('print', 'IDENTIFICADOR', 24, 0), 
    #     ('(', 'SIMBOLO', 24, 5), 
    #     ('1', 'NUMERO ENTERO', 24, 6), 
    #     ('+', 'OPERADOR', 24, 7), 
    #     ('3', 'NUMERO ENTERO', 24, 8), 
    #     (')', 'SIMBOLO', 24, 9), 
    #     (';', 'SIMBOLO', 24, 10)
    # ]
    
    DFA = Automata()

    #lectura de archivo
    with open("prov2.txt", "r", encoding="utf-8", errors="ignore") as file:
        code = file.read()

    DFA.process(code)

    # Create and pack the text widget
    text_widget = create_syntax_highlighter(root, DFA.tokens, code)
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