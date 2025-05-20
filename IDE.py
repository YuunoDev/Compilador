from tkinter import *
from tkinter import filedialog as FileDialog
from tkinter import ttk
from tkinter import colorchooser
import tkinter as tk
import threading
import re
from tkinter import messagebox
from Comp import *
from Lex.Anlex import *
import json
import os


ruta = ""
# Colores para los tokens
edit=False  # Bandera para saber si se ha editado el texto
#Clase de Lexico
DFA = Automata()
DFAC = Automata()

# Funciones para el menú
#nuevo archivo
def nuevo():
    """Crea un nuevo archivo."""
    global ruta, edit

    if(edit):
        if messagebox.askyesno("Nuevo archivo", "¿Desea guardar los cambios antes de crear un nuevo archivo?"):
            guardar()
            nuevo_arc()
        else:
            nuevo_arc() 
    else:
        nuevo_arc()
    
#ajustes para el nuevou archivo
def nuevo_arc():
    global ruta, edit
    mensaje.set("Nuevo fichero")
    ruta = ""
    texto.delete("1.0", END)
    actualizar_numeros_linea()
    root.title("IDE PyC")
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
        # Colorear el texto cargado
        debounce_colorText()
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
def colorText():
    contenido = texto.get("1.0", 'end-1c')  # Obtiene el contenido del editor

    DFAC.process(contenido)  # Procesar el texto actual

    texto.config(state="disabled")

    # Definir colores para cada tipo de token
    colores = {
        "COMENTARIO": "#407a33",      # Gris azulado apagado, sutil pero visible
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
        "DESCONOCIDO": "#d4d4d4",   # Rojo brillante, para errores
    }

    texto.tag_delete(*texto.tag_names())  # Elimina todos los tags

    # Crear tags para cada tipo de token
    for tipo, color in colores.items():
        texto.tag_configure(tipo, foreground=color)
    
    # Colorear tokens en el texto
    for token_value, token_type, line, col in DFAC.tokens:
        try:
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
                texto.tag_add(token_type, start_pos, end_pos)
                
                # Process middle lines (if any)
                for i in range(1, len(lines) - 1):
                    curr_line = line + i
                    texto.tag_add(token_type, f"{curr_line}.0", f"{curr_line}.{len(lines[i])}")
                
                # Process the last line
                if len(lines) > 1:
                    last_line = line + len(lines) - 1
                    last_line_length = len(lines[-1])
                    texto.tag_add(token_type, f"{last_line}.0", f"{last_line}.{last_line_length}")
            else:
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
                texto.tag_add(token_type, start_pos, end_pos)
        except tk.TclError as e:
            print(f"Error highlighting token {token_value}: {e}")
            continue
    
    # Hacer que el texto sea editable nuevamente
    texto.config(state="normal")
    

# Función para evitar llamadas repetidas a la función de resaltado
def debounce_colorText():
    if hasattr(debounce_colorText, "after_id"):
        texto.after_cancel(debounce_colorText.after_id)
    debounce_colorText.after_id = texto.after(400, colorText) 

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
    if contenido.strip() == "":
        mensaje.set("No hay código para ejecutar")
        return  
    else:
        # Limpiar las terminales
        terminalex.config(state="normal")
        terminalex.delete("1.0", END)
        terminalerlex.config(state="normal")
        terminalerlex.delete("1.0", END)

        # Terminal de ejecución
        terminalej.config(state="normal")
        terminalej.delete("1.0", END)
        terminalej.insert(END, "Ejecutando código...\n")
        terminalej.config(state="disabled")

        mensaje.set("Ejecutando código...")
        
        DFA.process(contenido)  # Establece el texto en el analizador léxico
        DFA.deleteCommentandError()  # Elimina los comentarios del texto

        for token in DFA.tokens:
            terminalex.config(state="normal")
            terminalex.insert(END, f"{token[0]}: {token[1]}\n")


        # print("\nErrores:")
        # for error in DFA.errors:
        #    print(error)
        for error in DFA.errors:
            terminalerlex.config(state="normal")
            terminalerlex.insert(END, error + "\n")

         # Si el archivo existe, lo eliminamos
        if os.path.exists("token.tk"):
            print("El archivo ya existe, se eliminará.")
            os.remove("token.tk")

        DFA.genarch("token.tk")  # Genera el árbol sintáctico
        
        terminalex.config(state="disabled")  # Deshabilitar la edición
        terminalerlex.config(state="disabled")  # Deshabilitar la edición

# Función para mostrar la posición del cursor
def show_cursor_position(event):
    """
    Muestra la posición del cursor en el monitor inferior.
    """
    cursor_pos = texto.index(INSERT)
    mensaje2.set(f"Línea: {cursor_pos.split('.')[0]}, Columna: {cursor_pos.split('.')[1]}")

    
# Ventas fuera de la principal
def colortexto():
    """Abre una ventana para elegir el color del texto."""
    color = colorchooser.askcolor(title="Selecciona un color")
    if color[1]:
        texto.config(fg=color[1])
        lineas.config(fg=color[1])
        mensaje.set("Color de texto cambiado")
    else:
        mensaje.set("Selección de color cancelada")

def on_key_release(event):
    """Maneja tanto la actualización de la posición del cursor como el coloreado del texto."""
    show_cursor_position(event)
    debounce_colorText()

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

#Bar de iconos
iconbar = Frame(root, bg="#2d2d2d")
iconbar.pack(fill="x")

# Iconos
nuevo_icon = PhotoImage(file="icons/nuevo.png")
# ajustar tamaño de icono
nuevo_icon = nuevo_icon.subsample(20, 20)
nuevo_btn = Button(iconbar, image=nuevo_icon, command=nuevo, bg="#999999", activebackground="#3c3c3c")
nuevo_btn.pack(side="left", padx=5, pady=5)

abrir_icon = PhotoImage(file="icons/abrir.png")
abrir_icon = abrir_icon.subsample(20, 20)
abrir_btn = Button(iconbar, image=abrir_icon, command=abrir, bg="#999999", activebackground="#3c3c3c")
abrir_btn.pack(side="left", padx=5, pady=5)

guardar_icon = PhotoImage(file="icons/guardar.png")
guardar_icon = guardar_icon.subsample(20, 20)
guardar_btn = Button(iconbar, image=guardar_icon, command=guardar, bg="#999999", activebackground="#3c3c3c")
guardar_btn.pack(side="left", padx=5, pady=5)

guardar_como_icon = PhotoImage(file="icons/guardar_como.png")
guardar_como_icon = guardar_como_icon.subsample(20, 20)
guardar_como_btn = Button(iconbar, image=guardar_como_icon, command=guardar_como, bg="#999999", activebackground="#3c3c3c")
guardar_como_btn.pack(side="left", padx=5, pady=5)



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
texto.config(bg="#1e1e1e", fg="#407a33", insertbackground="#d4d4d4")

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
texto.bind("<KeyRelease>", on_key_release)
texto.bind("<Button-1>", show_cursor_position)

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