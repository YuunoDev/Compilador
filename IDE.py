from tkinter import *
from tkinter import filedialog as FileDialog
import threading
import re


ruta = ""  # Almacena la ruta del fichero actual
# Almacena los colores de las palabras reservadas
colortex = {
    "def": "#ff7f00",  # Naranja brillante para definiciones
    "if": "#569cd6",  # Azul cielo para condiciones
    "else": "#569cd6",
    "elif": "#569cd6",
    "while": "#569cd6",
    "for": "#569cd6",
    "in": "#569cd6",
    "return": "#c586c0",  # Púrpura suave para declaraciones clave
    "print": "#9cdcfe",  # Azul claro para funciones comunes
    "True": "#dcdcaa",  # Amarillo suave para valores booleanos
    "False": "#dcdcaa",
    "None": "#dcdcaa",
    "and": "#569cd6",
    "or": "#569cd6",
    "not": "#569cd6",
    "import": "#c586c0",
    "from": "#c586c0",
    "as": "#c586c0",
    "break": "#c586c0",
    "continue": "#c586c0",
    "pass": "#c586c0",
    "class": "#4ec9b0",  # Verde azulado para clases
    "is": "#c586c0",
    "lambda": "#c586c0",
    "global": "#c586c0",
    "nonlocal": "#c586c0",
    "assert": "#c586c0",
    "try": "#c586c0",
    "except": "#c586c0",
    "finally": "#c586c0",
    "raise": "#c586c0",
    "with": "#c586c0",
    "yield": "#c586c0",
    "del": "#c586c0",
    "exec": "#c586c0",
    "eval": "#c586c0",
    "int": "#b5cea8",  # Verde suave para tipos de datos
    "float": "#b5cea8",
}


def nuevo():
    global ruta
    mensaje.set("Nuevo fichero")
    ruta = ""
    texto.delete("1.0", END)
    actualizar_numeros_linea()
    root.title("Mi editor")

def abrir():
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
            texto.insert(INSERT, contenido)
            actualizar_numeros_linea()
            colorTexto()
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

def actualizar_numeros_linea(event=None):
    """
    Actualiza el widget 'lineas' con el número de línea correspondiente.
    """
    # Se activa el widget para poder modificarlo
    lineas.config(state='normal')
    lineas.delete("1.0", END)
    
    # Obtener el número total de líneas (sin contar la línea extra al final)
    total_lineas = int(texto.index('end-1c').split('.')[0])
    numeros = "\n".join(str(i) for i in range(1, total_lineas + 1))
    lineas.insert("1.0", numeros)
    lineas.config(state='disabled')
    
    #mover la barra de desplazamiento al mismo nivel que el texto
    multiple_yview("moveto", texto.yview()[0])

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

def colorTexto(event=None):
    # Obtener el contenido del widget de texto
    contenido = texto.get("1.0", END)
    
    for palabra, color in colortex.items():
        # Crear un patrón de búsqueda para cada palabra reservada
        patron = r"\b" + palabra + r"\b"
        # Buscar todas las coincidencias de la palabra reservada
        for match in re.finditer(patron, contenido):
            # Obtener el índice de inicio y fin de la palabra reservada
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            # Colorear la palabra reservada
            texto.tag_add(palabra, start, end)
            texto.tag_config(palabra, foreground=color)

# Configuración de la ventana principal
root = Tk()
root.title("IDE PyC")  # Título de la ventana   

# Color de fondo de la ventana principal
root.configure(bg="#1e1e1e")  # Fondo oscuro

# Menú superior
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Nuevo", command=nuevo)
filemenu.add_command(label="Abrir", command=abrir)
filemenu.add_command(label="Guardar", command=guardar)
filemenu.add_command(label="Guardar como", command=guardar_como)
filemenu.add_separator()
filemenu.add_command(label="Salir", command=root.quit)
menubar.add_cascade(menu=filemenu, label="Archivo")

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

# Vincular el evento de modificación para actualizar los números de línea automáticamente
texto.bind("<<Modified>>", on_text_change)
texto.bind("<KeyRelease>", colorTexto)

#combinaciones de teclas
root.bind("<Control-n>", lambda e: nuevo())
root.bind("<Control-o>", lambda e: abrir())
root.bind("<Control-s>", lambda e: guardar())
root.bind("<Control-g>", lambda e: guardar_como())
root.bind("<Control-w>", lambda e: root.quit())

# Monitor inferior para mostrar mensajes al usuario
mensaje = StringVar()
mensaje.set("Editor PyC")
monitor = Label(root, textvariable=mensaje, anchor="w")
# Monitor inferior para mostrar mensajes al usuario
monitor.config(bg="#1e1e1e", fg="#d4d4d4")
monitor.pack(side="left", fill="x")

# vincular hilo para cambiar el color del texto
threadcolor = threading.Thread(target=colorTexto)

# Inicializa los números de línea
actualizar_numeros_linea()

root.mainloop()  # Bucle principal