from tkinter import *
from tkinter import filedialog as FileDialog
from tkinter import ttk
from tkinter import colorchooser
import tkinter as tk
import threading
import re
from tkinter import messagebox
from Lex.Anlex import *
from Sin.AnSin import *
from Sem.AnSem import *
from Ad_Ex.Exec import *
import json
import os
from Fileamd.File import *

# Clase para archivo
FILER = Fileamin()
#Clase de Lexico
DFA = Automata()
DFAC = Automata()
# Clase de sematico
SEM= SemAnalyzer()

#Configuración
CONF = Exec()
#colores
# Definir colores para cada tipo de token
COLORES = {
        "COMENTARIO": "#407a33",      # Gris azulado apagado, sutil pero visible
        "IDENTIFICADOR": "#C678DD",   # Lavanda suave, usado para variables
        "RESERVADA": "#61AFEF",        # Azul fuerte, común en palabras clave
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
        "CADENA": "#98C379",          # Verde claro, ideal para cadenas
        "OPERATORIO": "#56B6C2",        # << y >> para entrada/salida
        "BOOlEANO":"#61AFEF",
        "OTRO": "#ABB2BF",            # Gris claro, para texto neutro o no categorizado
    }

# Funciones para el menú
#nuevo archivo
def nuevo():
    """Crea un nuevo archivo."""
    if(FILER.edit):
        if messagebox.askyesno("Nuevo archivo", "¿Desea guardar los cambios antes de crear un nuevo archivo?"):
            guardar()
            nuevo_arc()
        else:
            nuevo_arc() 
    else:
        nuevo_arc()
    
#ajustes para el nuevou archivo
def nuevo_arc():
    mensaje.set("Nuevo fichero")
    FILER.Dfile()
    texto.delete("1.0", END)
    actualizar_numeros_linea()
    root.title("IDE PyC")
    FILER.setEdit(False)

def abrir():
    """Función para abrir un archivo sin trabar la interfaz gráfica."""
    mensaje.set("Abriendo fichero...")
    opent = threading.Thread(target=open_thread, daemon=True)  # Hilo en segundo plano
    opent.start()  # Iniciar el hilo correctamente

def open_thread():
    """Maneja la apertura del archivo en un hilo secundario."""
    ruta_temp = FileDialog.askopenfilename(
        initialdir=".",
        filetypes=[("Ficheros de texto", "*.txt")],
        title="Abrir un fichero de texto"
    )

    if ruta_temp:
        FILER.setRuta(ruta_temp)
        leer_archivo(FILER.getRuta())

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
        FILER.setEdit(False)

    except Exception as e:
        mensaje.set("Error al abrir el fichero")
        messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

def guardar():
    """Guarda el archivo en la ruta actual o pide guardarlo si no tiene ruta."""
    if FILER.getEdit():
        contenido = texto.get("1.0", "end-1c")
        try:
            with open(FILER.getRuta(), "w", encoding="utf-8") as fichero:
                fichero.write(contenido)
            mensaje.set("Fichero guardado correctamente")
            FILER.setEdit(False)
        except Exception as e:
            mensaje.set("Error al guardar el fichero")
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
    else:
        guardar_como()

def guardar_como():
    """Guarda el archivo con un nuevo nombre."""
    mensaje.set("Guardar fichero como")
    ruta_temp = FileDialog.asksaveasfilename(
        title="Guardar fichero",
        defaultextension=".txt",
        filetypes=[("Ficheros de texto", "*.txt")]
    )

    if ruta_temp:
        FILER.setRuta(ruta_temp)
        contenido = texto.get("1.0", "end-1c")
        try:
            with open(FILER.getRuta(), "w", encoding="utf-8") as f:
                f.write(contenido)
            mensaje.set("Fichero guardado correctamente")
            FILER.setEdit(False)
        except Exception as e:
            mensaje.set("Error al guardar el fichero")
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
    else:
        mensaje.set("Guardado cancelado")

def exit():
    """Cierra la aplicación, preguntando si se deben guardar cambios."""
    if FILER.getEdit():
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
    FILER.setEdit(True)

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

    texto.tag_delete(*texto.tag_names())  # Elimina todos los tags

    # Crear tags para cada tipo de token
    for tipo, color in COLORES.items():
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

def archivo_erroresSintacticos(errores):
    """
    Guarda los errores sintácticos en un archivo.
    """
    with open("errores_sintacticos.tk", "w", encoding="utf-8") as f:
        for error in errores:
            f.write(f"{error}\n")
    mensaje.set("Errores sintácticos guardados en 'errores_sintacticos.tk'")

def cargar_arbol(ast: ASTNode, errores: List[Error]):
    terminalsin.config(state="normal")
    terminalsin.delete("1.0", tk.END)
    # Mostrar errores
    if errores:
        for i, error in enumerate(errores, 1):
            tag = error.tipo.name.lower()
            #borrar el texto anterior
            terminalsin.config(state="normal")
            terminalsin.insert(tk.END, f"{i}. {error}\n", tag)
            terminalsin.config(state="disabled")
    else:
        terminalsin.config(state="normal")
        terminalsin.delete("1.0", tk.END)
        terminalsin.insert(tk.END, "¡No se encontraron errores! ✓", "success")
        terminalsin.tag_configure("success", foreground="green")
        terminalsin.config(state="disabled")

    # Mostrar estadísticas
    def contar_nodos(nodo):
        count = {"total": 0, "errores": 0, "por_tipo": {}}
        
        def contar_recursivo(n):
            count["total"] += 1
            if n.es_error:
                count["errores"] += 1
            
            tipo = n.tipo
            count["por_tipo"][tipo] = count["por_tipo"].get(tipo, 0) + 1
            
            for hijo in n.hijos:
                contar_recursivo(hijo)
        
        contar_recursivo(nodo)
        return count
    
    stats = contar_nodos(ast)

    # Agregar el AST al tree
    agregar_nodo(terminaltreeSin, '', ast)

def preparar_arbol():
    #lipiar arbol
    terminaltreeSin.delete(*terminaltreeSin.get_children())  # Limpiar el árbol
   
    tokens, errores_lexicos = cargar_tokens_desde_archivo("token.tk")

    if errores_lexicos:
        print("Errores encontrados al cargar tokens:")
        for error in errores_lexicos:
            print(f"  {error}")

    if not tokens:
        print("No se encontraron tokens válidos en el archivo.")
        # Mostrar solo los errores léxicos si no hay tokens
        cargar_arbol(ASTNode("Programa_Vacío"), errores_lexicos)
    else:
        # print(f"Se cargaron {len(tokens)} tokens exitosamente.")
        
        # Crear parser y analizar
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Combinar errores léxicos y de parsing
        todos_errores = errores_lexicos + parser.errores
    
        # Mostrar resultados
        # print(f"\nAnálisis completado:")
        # print(f"  - Errores encontrados: {len(todos_errores)}")
        # print(f"  - Variables declaradas: {parser.variables_declaradas}")
        
        archivo_erroresSintacticos(todos_errores)  # Guardar errores sintácticos en un archivo
        cargar_arbol(ast, todos_errores)

        ejecución_sem(ast)
        

def ejecución_sem(ast: ASTNode):
    #print("analisis sem")
    SEM.analizar(ast)
    #Tablas
    terminalej.config(state="normal")
    terminalej.insert(tk.END, SEM.symbol_table.display_r())
    terminalej.config(state="disabled")

    #arbol semantico
    terminalse.delete(*terminalse.get_children())  # Limpiar el árbol
    SEM.agregar_nodo(terminalse, '', SEM.tree)

    #errores
    terminalsem.config(state="normal")
    terminalsem.delete("1.0", tk.END)
    terminalsem.config(state="normal")
    terminalsem.insert(tk.END, SEM.report_errors_r())
    terminalsem.config(state="disabled")   


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
        
        terminalsin.config(state="normal")
        terminalsin.delete("1.0", END)

        SEM.erase()

        terminalsem.config(state="normal")
        terminalsem.delete("1.0", END)

        # Terminal de ejecución
        terminalej.config(state="normal")
        terminalej.delete("1.0", END)
        terminalej.insert(END, "Ejecutando código...\n")
        terminalej.config(state="disabled")

        mensaje.set("Ejecutando código...")
        
        DFA.process(contenido)  # Establece el texto en el analizador léxico
        DFA.genarcherrores("errores.tk")  # Generar archivo de errores
        DFA.deleteCommentandError()  # Elimina los comentarios del texto

        for token in DFA.tokens:
            terminalex.config(state="normal")
            terminalex.insert(END, f"{token[1]:<20} {token[0]:<18} (línea {token[2]}, columna {token[3]})\n")

        # print("\nErrores:")
        # for error in DFA.errors:
        #    print(error)
        if DFA.errors:
            terminalerlex.config(state="normal")
            terminalerlex.insert(END, "Errores encontrados:\n")
            for error in DFA.errors:
                terminalerlex.insert(END, f"{error}\n")
            terminalerlex.config(state="disabled")
            mensaje.set("Errores encontrados, revisa la terminal de errores.")
        else:
            terminalerlex.config(state="normal")
            terminalerlex.insert(END, "¡No se encontraron errores! ✓\n")
            terminalerlex.config(state="disabled")

         # Si el archivo existe, lo eliminamos
        if os.path.exists("token.tk"):
            #print("El archivo ya existe, se eliminará.")
            os.remove("token.tk")

        DFA.genarch("token.tk")  # Genera el archivo de tokens
        
        terminalex.config(state="disabled")  # Deshabilitar la edición
        terminalerlex.config(state="disabled")  # Deshabilitar la edición

        # Preparar el árbol de sintaxis
        preparar_arbol()
        

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

def confex():
    pass

##### Fin de ventanas fuera de la principal


# Configuración de la ventana principal
root = Tk()
root.title("IDE PyC")  # Título de la ventana   
#abrir ventana completa
root.state('zoomed')

# Color de fondo de la ventana principal
root.configure(bg="#1e1e1e")  # Fondo oscuro
style = ttk.Style()
style.theme_use('clam')
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
Configmenu.add_command(label="Ejecución", command=confex)
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

# divicion
mainpanel = ttk.PanedWindow(root, orient=tk.VERTICAL)
mainpanel.pack(fill="both", expand=True)

#superior horizontal
toppanel = ttk.PanedWindow(mainpanel, orient=tk.HORIZONTAL)
mainpanel.add(toppanel, weight=1)


# Frame para contener el área de texto y los números de línea
frame = Frame(toppanel, bg="#1e1e1e")
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
toppanel.add(frame, weight=1)

# Frame para terminales derechas,
frame_terminal = Frame(toppanel, bg="#1e1e1e")
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
frame_terminaltreeSin = Frame(notebook_terminal, bg="#1e1e1e")
terminaltreeSin = ttk.Treeview(frame_terminaltreeSin, columns=("Valor", "Línea", "Columna"), show="tree headings")

# Configurar colores para errores
terminaltreeSin.tag_configure("error", foreground="red")

# Encabezados
terminaltreeSin.heading("#0", text="Nodo")
terminaltreeSin.heading("Valor", text="Valor")
terminaltreeSin.heading("Línea", text="Línea")
terminaltreeSin.heading("Columna", text="Columna")
    
# Ajustes de columnas
terminaltreeSin.column("#0", width=200, anchor="w")
terminaltreeSin.column("Valor", width=200, anchor="w")
terminaltreeSin.column("Línea", width=60, anchor="center")
terminaltreeSin.column("Columna", width=70, anchor="center")

# Scrollbar para el tree
scrollbar_tree = ttk.Scrollbar(frame_terminaltreeSin, orient="vertical", command=terminaltreeSin.yview)
terminaltreeSin.configure(yscrollcommand=scrollbar_tree.set)

terminaltreeSin.grid(row=0, column=0, sticky="nsew")
scrollbar_tree.grid(row=0, column=1, sticky="ns")
    
frame_terminaltreeSin.grid_rowconfigure(0, weight=1)
frame_terminaltreeSin.grid_columnconfigure(0, weight=1)

notebook_terminal.add(frame_terminaltreeSin, text="Terminal Sintáctica")

# Terminal semántica árbol
frame_terminalse = Frame(notebook_terminal, bg="#1e1e1e")
terminalse = ttk.Treeview(frame_terminalse, columns=("Tipo","Valor", "Linea", "Columna"), show="tree headings")
# Encabezados
terminalse.heading("#0", text="Símbolo")
terminalse.heading("Tipo", text="Tipo")
terminalse.heading("Valor", text="Valor")
terminalse.heading("Linea", text="Linea")
terminalse.heading("Columna", text="Columna")
# Ajustes de columnas
terminalse.column("#0", width=200, anchor="w")
terminalse.column("Tipo", width=150, anchor="w")
terminalse.column("Valor", width=150, anchor="w")
terminalse.column("Linea", width=100, anchor="center")
terminalse.column("Columna", width=100, anchor="center")
# Scrollbar para el tree
scrollbar_tree_se = ttk.Scrollbar(frame_terminalse, orient="vertical", command=terminalse.yview)
terminalse.configure(yscrollcommand=scrollbar_tree_se.set)
terminalse.grid(row=0, column=0, sticky="nsew")
scrollbar_tree_se.grid(row=0, column=1, sticky="ns")
frame_terminalse.grid_rowconfigure(0, weight=1)
frame_terminalse.grid_columnconfigure(0, weight=1)

notebook_terminal.add(frame_terminalse, text="Terminal Semántica Árbol")
toppanel.add(frame_terminal, weight=1)

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
mainpanel.add(notebook, weight=2)

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