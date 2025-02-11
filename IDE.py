from tkinter import *
from tkinter import filedialog as FileDialog
from tkinter import ttk
from tkinter import colorchooser
import threading
import re
from Comp import *
from Comp_Lex import *


ruta = ""  # Almacena la ruta del fichero actual
# Colores para los tokens
colortex = {
    'ID': '#f92672',
    'FLOAT': '#ae81ff',
    'INT': '#ae81ff',
    'STRING': '#EBA500',#color naranja
    'PLUS': '#f8f8f2',
    'MINUS': '#f8f8f2',
    'MULT': '#f8f8f2',
    'DIV': '#f8f8f2',
    'MOD': '#f8f8f2',
    'EQUALS': '#f8f8f2',
    'DIFF': '#f8f8f2',
    'LESS': '#f8f8f2',
    'LESSEQ': '#f8f8f2',
    'GREATER': '#f8f8f2',
    'GREATERQ': '#f8f8f2',
    'ASSIGN': '#f8f8f2',
    'LPAREN': '#f8f8f2',
    'RPAREN': '#f8f8f2',
    'LBRACE': '#f8f8f2',
    'RBRACE': '#f8f8f2',
    'LBRACKET': '#f8f8f2',
    'RBRACKET': '#f8f8f2',
    'COMMA': '#f8f8f2',
    'COLON': '#f8f8f2',
    'TERM': '#f8f8f2',
    'INCREMENT': '#f8f8f2',
    'DECREMENT': '#f8f8f2',
    'AND': '#f8f8f2',
    'OR': '#f8f8f2',
    'NOT': '#f8f8f2',
    'IF': '#a6e22e',
    'ELSE': '#a6e22e',
    'WHILE': '#a6e22e',
    'FOR': '#a6e22e',
    'IN': '#a6e22e',
    'RANGE': '#a6e22e',
    'DEF': '#a6e22e',
    'RETURN': '#a6e22e',
    'TYPE': '#a6e22e',
    'BOOL': '#a6e22e',
    'NONE': '#a6e22e',
    'PRINT': '#a6e22e',
    'INPUT': '#a6e22e',
    'LEN': '#a6e22e',
    'PLUS': '#f8f8f2',
    'COMMENT': '#75715e'
}

# Funciones para el menú
def nuevo():#nuevo archivo
    global ruta
    mensaje.set("Nuevo fichero")
    ruta = ""
    texto.delete("1.0", END)
    actualizar_numeros_linea()
    root.title("Mi editor")

def abrir():#abrir archivo
    global ruta
    mensaje.set("Abrir fichero")
    ruta = FileDialog.askopenfilename(
        initialdir='.',
        filetypes=(("Ficheros de texto", "*.txt"),),
        title="Abrir un fichero de texto"
    )

    if ruta != "":
        try:
            with open(ruta, 'r', encoding='utf-8') as fichero:
                contenido = fichero.read()
            texto.delete("1.0", END)
            terminalex.delete("1.0", END)
            texto.insert(INSERT, contenido)
            actualizar_numeros_linea()
            colorTexto()
            show_cursor_position(None)  # Mostrar la posición del cursor
            root.title(ruta + " - Mi editor")
        except Exception as e:
            mensaje.set("Error al abrir el fichero")
            print("Error:", e)

def guardar():
    mensaje.set("Guardar fichero")
    if ruta != "":
        contenido = texto.get("1.0", 'end-1c')
        try:
            with open(ruta, 'w+', encoding='utf-8') as fichero:
                fichero.write(contenido)
            mensaje.set("Fichero guardado correctamente")
        except Exception as e:
            mensaje.set("Error al guardar el fichero")
            print("Error:", e)
    else:
        guardar_como()

def guardar_como():
    global ruta
    mensaje.set("Guardar fichero como")
    fichero = FileDialog.asksaveasfile(title="Guardar fichero", mode="w", defaultextension=".txt")
    if fichero is not None:
        ruta = fichero.name
        contenido = texto.get("1.0", 'end-1c')
        try:
            with open(ruta, 'w+', encoding='utf-8') as f:
                f.write(contenido)
            mensaje.set("Fichero guardado correctamente")
        except Exception as e:
            mensaje.set("Error al guardar el fichero")
            print("Error:", e)
    else:
        mensaje.set("Guardado cancelado")
        ruta = ""


# Función para actualizar los números de línea
def actualizar_numeros_linea(event=None):
    """
    Actualiza el widget 'lineas' con el número de línea correspondiente.
    """
    # Se activa el widget para poder modificarlo
    lineas.config(state='normal')
    lineas.delete("1.0", END)
    
    # Obtener el número total de líneas (sin contar la línea extra al final)
    total_lineas = int(texto.index('end-1c').split('.')[0]);
    numeros = "\n".join(str(i) for i in range(1, total_lineas + 1))
    lineas.insert("1.0", numeros)
    lineas.config(state='disabled')
    
    #mover la barra de desplazamiento al mismo nivel que el texto
    multiple_yview("moveto", texto.yview()[0])

# Función para el evento de cambio de texto
def on_text_change(event):
    """
    Esta función se llama cada vez que el widget 'texto' se modifica.
    Se actualizan los números de línea y se restablece la bandera 'modified'.
    """
    actualizar_numeros_linea()
    texto.edit_modified(False)  # Restablecer la bandera de modificación
    

# Función para sincronizar el desplazamiento
def multiple_yview(*args):
    texto.yview(*args)
    lineas.yview(*args)

# Función para sincronizar el scrollbar cuando se mueve el texto
def sync_scroll(*args):
    scrollbar.set(*args)
    lineas.yview("moveto", args[0])

# Función para iniciar el hilo de coloreado de texto
def colorTexto(event=None):
    colorthread = threading.Thread(target=colorTextoThread)
    colorthread.run()

# Función para colorear el texto
def colorTextoThread():
    # Obtener el contenido completo del texto
    contenido = texto.get("1.0", END)
    
    # Obtener los tokens
    tokens = lexer_color(contenido)
    
    # Eliminar cualquier formato previo
    for tag in texto.tag_names():
        texto.tag_remove(tag, "1.0", END)
    
    # Configurar los tags de colores
    for palabra, color in colortex.items():
        texto.tag_config(palabra, foreground=color)
    
    # Posición actual en el texto
    pos = "1.0"
    
    for token_type, token_value in tokens:
        try:
            # Buscar el token exacto
            start_pos = texto.search(
                re.escape(token_value),
                pos,
                END,
                regexp=False  # Evitar errores por secuencias especiales
            )

            if not start_pos:
                continue

            end_pos = f"{start_pos}+{len(token_value)}c"

            # Aplicar el tag correspondiente
            if token_type in colortex:
                texto.tag_add(token_type, start_pos, end_pos)
            else:
                texto.tag_add("ID", start_pos, end_pos)

            pos = end_pos

        except Exception as e:
            print(f"Error al colorear token {token_type}: {token_value}", e)
            re.purge()
            continue


# Función para ejecutar el código
def ejecutar_codigo():
    """
    Función que simula la ejecución del código ingresado.
    Actualmente solo imprime el contenido y hace un 'pass'.
    """
    contenido = texto.get("1.0", 'end-1c')  # Obtiene el contenido del editor
    mensaje.set("Ejecutando código...")  
    tokens = lexer(contenido)
    #mandar a la terminal lexica
    terminalex.delete("1.0", END)
    for token in tokens:
        terminalex.insert(END, f"{token}\n")

# Función para mostrar la posición del cursor
def show_cursor_position(event):
    """
    Muestra la posición del cursor en el monitor inferior.
    """
    cursor_pos = texto.index(INSERT)
    mensaje2.set(f"Línea: {cursor_pos.split('.')[0]}, Columna: {cursor_pos.split('.')[1]}")
    colorTexto(None)

# Ventas fuera de la principal

def colortexto():
    colorselec=Tk()
    colorselec.title("Configurar color de IDE")

    
    

    
def selectorcl(color):
    selectcl= colorchooser.askcolor(title="Selecciona un color")




# Fin de ventanas fuera de la principal


# Configuración de la ventana principal
root = Tk()
root.title("IDE PyC")  # Título de la ventana   

# Color de fondo de la ventana principal
root.configure(bg="#1e1e1e")  # Fondo oscuro
style = ttk.Style()
style.theme_use('alt')
style.configure("TNotebook", background="#1e1e1e")
style.configure("TNotebook.Tab", background="#2d2d2d", foreground="#d4d4d4", lightcolor="#2d2d2d", borderwidth=0)
style.map("TNotebook.Tab", background=[("selected", "#1e1e1e")])

# Menú superior
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Nuevo   Ctrl+n", command=nuevo)
filemenu.add_command(label="Abrir   Ctrl+o", command=abrir)
filemenu.add_command(label="Guardar Ctrl+s", command=guardar)
filemenu.add_command(label="Guardar como Ctrl+g", command=guardar_como)
filemenu.add_separator()
filemenu.add_command(label="Salir   Ctrl+w", command=root.quit)
menubar.add_cascade(menu=filemenu, label="Archivo")
menubar.add_separator()
menubar.add_checkbutton(label="Ejecutar", command=ejecutar_codigo)
menubar.add_separator()

Configmenu= Menu(menubar, tearoff=0)
Configmenu.add_command(label="Color texto", command=colorTexto)
menubar.add_cascade(menu=Configmenu, label="Configuración")

# Menú superior
menubar.config(bg="#2d2d2d", fg="#d4d4d4")
filemenu.config(bg="#2d2d2d", fg="#d4d4d4", activebackground="#3c3c3c", activeforeground="white")

root.config(menu=menubar)

# Frame para contener el área de texto y los números de línea
frame = Frame(root)
frame.pack(fill="both", expand=True)

# Widget para los números de línea
lineas = Text(frame, width=4, padx=4, takefocus=0, border=0,
               state='disabled',
              font=("Consolas", 12))
lineas.pack(side="left", fill="y")
# Colores para la barra de números de línea
lineas.config(bg="#2d2d2d", fg="#d4d4d4")

# Widget de texto principal
texto = Text(frame, bd=0, padx=6, pady=4, font=("Consolas", 12), undo=True)

# Colores para el área de texto principal
texto.config(bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4")

# Añadir el widget de texto al frame
texto.pack(side="left", fill="both", expand=True)

# Scrollbar para sincronizar el desplazamiento
scrollbar = Scrollbar(frame)
scrollbar.pack(side="right", fill="y")
scrollbar.config(bg="#2d2d2d", troughcolor="#1e1e1e", activebackground="#555555")

# Configurar el scrollbar y los widgets de texto
scrollbar.config(command=multiple_yview)
texto.config(yscrollcommand=sync_scroll)
lineas.config(yscrollcommand=scrollbar.set)

# Contenedor de ventanas (Notebook)
notebook = ttk.Notebook(root, style="Custom.TNotebook")
notebook.pack(fill="both", expand=True, pady=(4, 0))

# Terminal Léxica
frame_terminalex = Frame(notebook, bg="#1e1e1e")
terminalex = Text(frame_terminalex, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalex.pack(fill="both", expand=True)

notebook.add(frame_terminalex, text="Terminal Léxica")

# Terminal Sintáctica
frame_terminal = Frame(notebook, bg="#1e1e1e")
terminalsy = Text(frame_terminal, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalsy.pack(fill="both", expand=True)

notebook.add(frame_terminal, text="Terminal Sintáctica")




# Vincular el evento de modificación para actualizar los números de línea automáticamente
texto.bind("<<Modified>>", on_text_change)
texto.bind("<KeyRelease>", show_cursor_position)

#combinaciones de teclas
root.bind("<Control-n>", lambda e: nuevo())
root.bind("<Control-o>", lambda e: abrir())
root.bind("<Control-s>", lambda e: guardar())
root.bind("<Control-g>", lambda e: guardar_como())
root.bind("<Control-w>", lambda e: root.quit())

# Tecla rápida para ejecutar el código
root.bind("<Control-e>", lambda e: ejecutar_codigo())

# Barra de estado
status_frame = Frame(root, bg="#2d2d2d", height=25)
status_frame.pack(fill="x", side="bottom")

# Mensaje de estado
mensaje = StringVar(value="Ready")
status_left = Label(status_frame, textvariable=mensaje, bg="#2d2d2d", fg="#d4d4d4", padx=5, pady=2)
status_left.pack(side="left")

# Posición del cursor
mensaje2 = StringVar(value="Ln 1, Col 0")
status_right = Label(status_frame, textvariable=mensaje2, bg="#2d2d2d", fg="#d4d4d4", padx=5, pady=2)
status_right.pack(side="right")

# Inicializa los números de línea
actualizar_numeros_linea()

root.mainloop()  # Bucle principal