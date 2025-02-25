from tkinter import *
from tkinter import filedialog as FileDialog
from tkinter import ttk
from tkinter import colorchooser
import threading
import re
from tkinter import messagebox
from Comp import *
from Comp_Lex import *
import json
import os


ruta = ""
# Colores para los tokens
arch_colors = "colores.json"
edit=False  # Bandera para saber si se ha editado el texto

# lista de colores que quedara como uno en comun
colores_comunes_punt = {
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    'MOD',
    'EQUALS',
    'DIFF',
    'LESS',
    'LESSEQ',
    'GREATER',
    'GREATERQ',
    'ASSIGN',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'COLON',
    'TERM',
    'INCREMENT',
    'DECREMENT',
    'AND',
    'OR',
    'NOT'
}

colores_comunes_reserv = {
    'IF',
    'ELSE',
    'WHILE',
    'FOR',
    'IN',
    'RANGE',
    'DEF',
    'TYPE',
    'BOOL',
    'NONE',
    'PRINT',
    'INPUT',
}        


# Cargar colores del archivo si existe
def cargar_colores():
    if os.path.exists(arch_colors):
        with open(arch_colors, "r") as archivo:
            return json.load(archivo)
    # Si no existe, usa colores predeterminados
    else:
        tepcolors = {
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
            'TYPE': '#a6e22e',
            'BOOL': '#a6e22e',
            'NONE': '#a6e22e',
            'PRINT': '#a6e22e',
            'INPUT': '#a6e22e',
            'RETURN': "#f92694",
            'LEN': '#f21231',
            'COMMENT': '#75715e'
        }
        with open(arch_colors, "w") as archivo:
            json.dump(tepcolors, archivo, indent=4)
        return tepcolors 
    
# Cargar colores iniciales
colortex = cargar_colores()

def guardar_colores():
    with open(arch_colors, "w") as archivo:
        json.dump(colortex, archivo, indent=4)

# Función para cambiar el color de un token
    


# Funciones para el menú
def nuevo():
    """Crea un nuevo archivo."""
    global ruta, edit
    mensaje.set("Nuevo fichero")
    ruta = ""
    texto.delete("1.0", END)
    actualizar_numeros_linea()
    root.title("Mi editor")
    edit = False

def abrir():
    """Función para abrir un archivo sin trabar la interfaz gráfica."""
    mensaje.set("Abriendo fichero...")
    opent = threading.Thread(target=open_thread, daemon=True)  # Hilo en segundo plano
    opent.start()  # Iniciar el hilo correctamente

def open_thread():
    """Maneja la apertura del archivo en un hilo secundario."""
    global ruta
    ruta_temp = FileDialog.askopenfilename(
        initialdir=".",
        filetypes=[("Ficheros de texto", "*.txt")],
        title="Abrir un fichero de texto"
    )

    if ruta_temp:
        ruta = ruta_temp
        leer_archivo(ruta)

def leer_archivo(ruta):
    "Lee el contenido de un archivo y lo muestra en la interfaz."""
    try:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as fichero:
            contenido = fichero.read()

        texto.delete("1.0",END)
        texto.insert(INSERT, contenido)

        actualizar_numeros_linea()
        show_cursor_position(None)  # Mostrar posición del cursor
        root.title(f"{ruta} - Mi editor")
        mensaje.set("Archivo cargado correctamente")
        global edit
        edit = False

    except Exception as e:
        mensaje.set("Error al abrir el fichero")
        messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

def guardar():
    """Guarda el archivo en la ruta actual o pide guardarlo si no tiene ruta."""
    global edit
    if ruta:
        contenido = texto.get("1.0", "end-1c")
        try:
            with open(ruta, "w", encoding="utf-8") as fichero:
                fichero.write(contenido)
            mensaje.set("Fichero guardado correctamente")
            edit = False
        except Exception as e:
            mensaje.set("Error al guardar el fichero")
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
    else:
        guardar_como()

def guardar_como():
    """Guarda el archivo con un nuevo nombre."""
    global ruta, edit
    mensaje.set("Guardar fichero como")
    ruta_temp = FileDialog.asksaveasfilename(
        title="Guardar fichero",
        defaultextension=".txt",
        filetypes=[("Ficheros de texto", "*.txt")]
    )

    if ruta_temp:
        ruta = ruta_temp
        contenido = texto.get("1.0", "end-1c")
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            mensaje.set("Fichero guardado correctamente")
            edit = False
        except Exception as e:
            mensaje.set("Error al guardar el fichero")
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
    else:
        mensaje.set("Guardado cancelado")


def exit():
    """Cierra la aplicación, preguntando si se deben guardar cambios."""
    global edit
    if edit:
        if messagebox.askyesno("Salir", "¿Desea guardar los cambios antes de salir?"):
            guardar()
    root.quit()


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
    global edit
    edit=True
    #colorTexto(None)
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
    colorthread.start()

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
    
    for token_type, token_value, token_ID in tokens:
        # Encontrar la siguiente ocurrencia del token
        try:
            
            # Buscar el token exacto
            start_pos = texto.search(
                re.escape(token_value),
                pos,
                END,
                regexp=True
            )
            
            if not start_pos:
                continue
                
            # Calcular la posición final
            end_pos = f"{start_pos}+{len(token_value)}c"
            
            # Aplicar el tag correspondiente
            if token_type in colortex:
                texto.tag_add(token_type, start_pos, end_pos)                
            else:
                texto.tag_add("ID", start_pos, end_pos)
            
            # Actualizar la posición para la siguiente búsqueda
            pos = end_pos

            
        except Exception as e:
            print(f"Error al colorear token {token_type}: {token_value}", e)
            re.purge()
            continue
    re.purge()

# Función para ejecutar el código
def ejecutar_codigo():
    """
    Función que ejecuta el código ingresado.
    """
    ejecutar = threading.Thread(target=thread_ejecutar)
    ejecutar.start()

def thread_ejecutar():
    """
    Función que simula la ejecución del código ingresado.
    """
    contenido = texto.get("1.0", 'end-1c')  # Obtiene el contenido del editor
    mensaje.set("Ejecutando código...")  
    tokens, errors = lexer(contenido)
    #mandar a la terminal lexica
    terminalex.config(state="normal")  # Habilitar la edición
    terminalex.delete("1.0", END)

    terminalerlex.config(state="normal")  # Habilitar la edición
    terminalerlex.delete("1.0", END)
    #abrir terminal
    for token in tokens:
        terminalex.insert(END, f"{token}\n")

    for error in errors:
        #print(f"Línea {error[0]}, Columna {error[1]}: {error[2]}")
        terminalerlex.insert(END, f"Línea {error[0]}, Columna {error[1]}: {error[2]}\n")

    terminalex.config(state="disabled")  # Deshabilitar la edición
    terminalerlex.config(state="disabled")  # Deshabilitar la edición

# Función para mostrar la posición del cursor
def show_cursor_position(event):
    """
    Muestra la posición del cursor en el monitor inferior.
    """
    treadsh=threading.Thread(target=tread_showcursor)
    treadsh.start()

def tread_showcursor():
    cursor_pos = texto.index(INSERT)
    mensaje2.set(f"Línea: {cursor_pos.split('.')[0]}, Columna: {cursor_pos.split('.')[1]}")

# Ventas fuera de la principal
def colortexto():
    # Crear y configurar la ventana principal
    colorselec = Tk()
    colorselec.title("Personalización de Colores IDE")
    colorselec.configure(bg="#1e1e1e")
    
    # Agregar un poco de padding general
    colorselec.geometry("900x500")
    colorselec.resizable(False, False)
    
    # Marco principal con efecto de sombra
    marco_principal = Frame(
        colorselec,
        bg="#1e1e1e",
        highlightbackground="#333333",
        highlightthickness=1
    )
    marco_principal.pack(padx=20, pady=20, fill=BOTH, expand=True)
    
    # Título decorativo
    Label(
        marco_principal,
        text="Vista Previa del Código",
        font=("Arial", 12, "bold"),
        bg="#1e1e1e",
        fg="#ffffff"
    ).grid(row=0, column=0, pady=10, padx=10, sticky="w")
    
    # Área de texto mejorada
    texto_muestra = Text(
        marco_principal,
        height=12,
        width=50,
        bg="#1e1e1e",
        fg="white",
        font=("Consolas", 12),
        padx=15,
        pady=15,
        wrap=WORD,
        insertbackground="white"  # Cursor blanco
    )
    texto_muestra.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
    
    # Texto de ejemplo más elaborado
    codigo_ejemplo = '''def ejemplo_funcion():
    # Este es un comentario de ejemplo
    mensaje = "¡Hola, mundo!"
    print(mensaje)
    
    # Prueba los colores aquí
    for i in range(3):
        print(f"Contador: {i}")'''
    
    texto_muestra.insert(INSERT, codigo_ejemplo)
    
    # Marco para selección de colores con título
    Label(
        marco_principal,
        text="Selección de Colores",
        font=("Arial", 12, "bold"),
        bg="#1e1e1e",
        fg="#ffffff"
    ).grid(row=0, column=2, pady=10, padx=10, sticky="w")
    
    # Contenedor con scroll para los colores
    contenedor_scroll = Frame(marco_principal)
    contenedor_scroll.grid(row=1, column=2, padx=20, pady=5, sticky="nsew")
    
    canvas = Canvas(contenedor_scroll, bg="#1e1e1e", highlightthickness=0)
    scrollbar = Scrollbar(contenedor_scroll, orient=VERTICAL, command=canvas.yview)
    marco_derecho = Frame(canvas, bg="#1e1e1e")
    
    marco_derecho.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=marco_derecho, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    # Función para crear filas de colores más estilizadas
    def crear_fila_color(parent, texto, color, textocop):
        frame = Frame(parent, bg="#1e1e1e", pady=5)
        frame.pack(fill=X)

        # Etiqueta con el nombre del color
        Label(
            frame,
            text=texto,
            width=15,
            anchor="w",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 10)
        ).pack(side=LEFT)
        
        # Muestra del color actual
        muestra_color = Label(
            frame,
            bg=color,
            width=8,
            height=1,
            relief="raised"
        )
        muestra_color.pack(side=LEFT, padx=10)
        
        # Botón para cambiar el color
        btn= Button(
            frame,
            text="Cambiar",
            command=lambda: cambiar_color(texto, muestra_color),
            bg="#333333",
            fg="white",
            relief="raised"
        )
        btn.pack(side=LEFT, padx=10)
    
    # Función para cambiar el color de un token
    def cambiar_color(id_label, color_label):
        colorsec = colorchooser.askcolor(title=f"Selecciona un color para {id_label}", parent=colorselec)
        if colorsec[1]:  # color[1] contiene el valor hexadecimal del color
            color_label.config(bg=colorsec[1])
            if id_label=="Operadores":
                print("Operadores")
                for nombre, color in colortex.items():
                    if nombre in colores_comunes_punt:
                        colortex[nombre] = colorsec[1]
            elif id_label=="Palabras Reservadas":
                for nombre, color in colortex.items():
                    if nombre in colores_comunes_reserv:
                        colortex[nombre] = colorsec[1]
            else:
                colortex[id_label] = colorsec[1]
            guardar_colores()
            colorcambsel(texto_muestra)

    # si se encontro un color comun
    ccp=False
    ccr=False

    # Crear filas de colores
    for nombre, color in colortex.items():
        #si es difernete a los colores comunes agregarlo
        if nombre not in colores_comunes_punt and nombre not in colores_comunes_reserv:
            crear_fila_color(marco_derecho, nombre, color, texto_muestra)
        #si es igual a los colores comunes agregarlo
        elif nombre in colores_comunes_punt:
            if not ccp:
                crear_fila_color(marco_derecho, "Operadores", color,texto_muestra)
                ccp=True
        elif nombre in colores_comunes_reserv:
            if not ccr:
                crear_fila_color(marco_derecho, "Palabras Reservadas", color,texto_muestra)
                ccr=True
        else:
            print("Error al agregar el color", nombre)
                
        

    # Hacer que el área de texto sea expandible
    marco_principal.grid_columnconfigure(0, weight=1)
    marco_principal.grid_rowconfigure(1, weight=1)

    #poner color en el texto
    colorcambsel(texto_muestra)
    
    # Iniciar la ventana
    colorselec.mainloop()

    # Función para colorear el texto de cambio de color
def colorcambsel(intput_text):

    # Obtener el contenido completo del texto
    contenido = intput_text.get("1.0", END)
    
    # Obtener los tokens
    tokens = lexer_color(contenido)
    
    # Eliminar cualquier formato previo
    for tag in intput_text.tag_names():
        intput_text.tag_remove(tag, "1.0", END)
    
    # Configurar los tags de colores
    for palabra, color in colortex.items():
        intput_text.tag_config(palabra, foreground=color)
    
    # Posición actual en el texto
    pos = "1.0"
    
    for token_type, token_value in tokens:
        # Encontrar la siguiente ocurrencia del token
        try:
            
            # Buscar el token exacto
            start_pos = intput_text.search(
                re.escape(token_value),
                pos,
                END,
                regexp=True # No usar expresiones regulares
            )

            
            if not start_pos:
                continue
                
            # Calcular la posición final
            end_pos = f"{start_pos}+{len(token_value)}c"
            
            # Aplicar el tag correspondiente
            if token_type in colortex:
                intput_text.tag_add(token_type, start_pos, end_pos)                
            else:
                intput_text.tag_add("ID", start_pos, end_pos)
            
            # Actualizar la posición para la siguiente búsqueda
            pos = end_pos

            
        except Exception as e:
            print(f"Error al colorear token {token_type}: {token_value}", e)
            re.purge()
            continue
    re.purge()
##### Fin de ventanas fuera de la principal


# Configuración de la ventana principal
root = Tk()
root.title("IDE PyC")  # Título de la ventana   
#abrir ventana completa
root.state('zoomed')

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
Configmenu.add_command(label="Color texto", command=colortexto)
menubar.add_cascade(menu=Configmenu, label="Configuración")

# Menú superior
menubar.config(bg="#2d2d2d", fg="#d4d4d4")
filemenu.config(bg="#2d2d2d", fg="#d4d4d4", activebackground="#3c3c3c", activeforeground="#d4d4d4")
Configmenu.config(bg="#2d2d2d", fg="#d4d4d4", activebackground="#3c3c3c", activeforeground="#d4d4d4")
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
texto = Text(frame, bd=0, padx=6, pady=4, font=("Consolas", 12), undo=True,  wrap="none")

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

# Frame para terminales
frame_terminal = Frame(frame, bg="#1e1e1e")
frame_terminal.pack(fill="both", expand=True, side="right")

#Pestañas para la terminal
notebook_terminal = ttk.Notebook(frame_terminal, style="Custom.TNotebook")
notebook_terminal.pack(fill="both", expand=True)

# Terminal léxica
framelexer = Frame(notebook_terminal, bg="#1e1e1e") # Fondo oscuro
terminalex = Text(framelexer, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalex.pack(fill="both", expand=True)
terminalex.config(state="disabled")

notebook_terminal.add(framelexer, text="Terminal Léxica")

# Terminal sintáctica
frame_terminalsy = Frame(notebook_terminal, bg="#1e1e1e")
terminalsy = Text(frame_terminalsy, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalsy.pack(fill="both", expand=True)
terminalsy.config(state="disabled")

notebook_terminal.add(frame_terminalsy, text="Terminal Sintáctica")

# Terminal semántica
frame_terminalse = Frame(notebook_terminal, bg="#1e1e1e")
terminalse = Text(frame_terminalse, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalse.pack(fill="both", expand=True)
terminalse.config(state="disabled")

notebook_terminal.add(frame_terminalse, text="Terminal Semántica")


# Contenedor de ventanas (Notebook)
notebook = ttk.Notebook(root, style="Custom.TNotebook")
notebook.pack(fill="both", expand=True, pady=(4, 0))

# Terminal de Ejecución
frame_terminalex = Frame(notebook, bg="#1e1e1e")
terminalej = Text(frame_terminalex, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalej.pack(fill="both", expand=True)

notebook.add(frame_terminalex, text="Terminal de Ejecución")

# Terminal de Errores lexicos
frame_terminalerlex = Frame(notebook, bg="#1e1e1e")
terminalerlex = Text(frame_terminalerlex, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalerlex.pack(fill="both", expand=True)
terminalerlex.config(state="disabled")

notebook.add(frame_terminalerlex, text="Errores Léxicos")

# Terminal de Errores sintácticos
frame_terminalsin = Frame(notebook, bg="#1e1e1e")
terminalsin = Text(frame_terminalsin, height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalsin.pack(fill="both", expand=True)
terminalsin.config(state="disabled")

notebook.add(frame_terminalsin, text="Errores Sintácticos")

# Terminal de Errores Semánticos
frame_terminalsem = Frame(notebook, bg="#1e1e1e")
terminalsem= Text(frame_terminalsem,height=5, bg="#1e1e1e", fg="#d4d4d4")
terminalsem.pack(fill="both",expand=TRUE)
terminalsem.config(state="disabled")

notebook.add(frame_terminalsem, text="Errores Semáticos")

# Vincular el evento de modificación para actualizar los números de línea automáticamente
texto.bind("<<Modified>>", on_text_change)
texto.bind("<KeyRelease>", show_cursor_position)

#combinaciones de teclas
root.bind("<Control-n>", lambda e: nuevo())
root.bind("<Control-o>", lambda e: abrir())
root.bind("<Control-s>", lambda e: guardar())
root.bind("<Control-g>", lambda e: guardar_como())
root.bind("<Control-w>", lambda e: exit())

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

tread_main=threading.Thread(target=root.mainloop())  # Bucle principal