from tkinter import *
from tkinter import filedialog as FileDialog
from tkinter import ttk
from tkinter import colorchooser
import tkinter as tk
import threading
import re
from tkinter import messagebox
from Anlex import *
from AnSin import *
from AnSem import *
from Ad_Ex.Exec import *
import json
import os
from Fileamd.File import *
import generador_codigo as gc
import mv as VirtualMachine
from tkinter import simpledialog

# Clase para crear tooltips en Tkinter
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        self.id = None
        self.x = self.y = 0
        
        self.widget.bind("<Enter>", self.on_enter, add="+")
        self.widget.bind("<Leave>", self.on_leave, add="+")
        self.widget.bind("<Motion>", self.on_motion, add="+")

    def on_enter(self, event):
        if self.id:
            self.widget.after_cancel(self.id)
        self.id = self.widget.after(500, self.show_tip, event)

    def on_leave(self, event):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        self.hide_tip()

    def on_motion(self, event):
        self.x = event.x_root + 10
        self.y = event.y_root + 10
        if self.tip:
            self.tip.geometry(f"+{self.x}+{self.y}")

    def show_tip(self, event):
        if self.tip or not self.text:
            return
        
        self.x = event.x_root + 10
        self.y = event.y_root + 10
        
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{self.x}+{self.y}")
        
        label = tk.Label(
            self.tip,
            text=self.text,
            background="#ffffe0",
            foreground="#000000",
            relief=tk.SOLID,
            borderwidth=1,
            padx=5,
            pady=3,
            font=("Arial", 9)
        )
        label.pack()

    def hide_tip(self):
        if self.tip:
            self.tip.destroy()
            self.tip = None

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
        initialdir=FILER.getRuta() if FILER.getRuta() else ".",
        filetypes=[("Ficheros de texto", "*.txt")],
        title="Abrir un fichero de texto"
    )

    if ruta_temp:
        FILER.setRuta(ruta_temp)
        # Guardar la carpeta del archivo abierto
        carpeta = os.path.dirname(ruta_temp)
        FILER.save_folder(carpeta)
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
    contenido = texto.get("1.0", "end-1c")
    
    # Si no hay ruta asignada, abre el diálogo guardar como
    if not FILER.getRuta() or FILER.getRuta() == "":
        guardar_como()
        return
    
    try:
        with open(FILER.getRuta(), "w", encoding="utf-8") as fichero:
            fichero.write(contenido)
        mensaje.set("Fichero guardado correctamente")
        FILER.setEdit(False)
    except Exception as e:
        mensaje.set("Error al guardar el fichero")
        messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

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
        # Guardar la carpeta del archivo guardado
        carpeta = os.path.dirname(ruta_temp)
        FILER.save_folder(carpeta)
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

# Función auxiliar para limpiar números de línea
def clean_instruction(instruction):
    """Elimina los números de línea del formato '123: instrucción' si existen"""
    instruction = instruction.strip()
    if instruction and ': ' in instruction:
        # Verificar si comienza con números
        parts = instruction.split(': ', 1)
        if parts[0].strip().isdigit():
            return parts[1]  # Retornar solo la instrucción
    return instruction

# Función para ejecutar el código
def ejecutar_codigo(modo):
    """
    Función que ejecuta el código ingresado.
    Modos disponibles:
    - 'compilar': Solo compila (análisis léxico, sintáctico y semántico)
    - 'ejecutar': Solo ejecuta (requiere que ya esté compilado)
    - 'compilar_ejecutar': Compila y ejecuta
    """
    CONF.setModo(modo)
    ejecutar = threading.Thread(target=thread_ejecutar, daemon=True)
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
        terminalsin.tag_configure("success", foreground="white")
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
    
        SEM.analizar(ast)
        
        #Tablas
        terminaltab.delete(*terminaltab.get_children())  # limpiar primero
        symbols = SEM.symbol_table.display_r()

        for entry in symbols:
            terminaltab.insert(
                "",
                "end",
                text=entry["nombre"], 
                values=(entry["tipo"], entry["valor"], entry["usada"], entry["lineas"])
        )
            
         #arbol semantico
        terminalse.delete(*terminalse.get_children())  # Limpiar el árbol
        SEM.agregar_nodo(terminalse, '', SEM.tree)

        #errores
        if SEM.errors:
            terminalsem.config(state="normal")
            terminalsem.delete("1.0", tk.END)
            for i, error in enumerate(SEM.errors, 1):
                # Manejar tanto strings como objetos Error
                if isinstance(error, str):
                    tag = "error"
                    error_text = error
                else:
                    tag = error.tipo.name.lower()
                    error_text = str(error)
                terminalsem.insert(tk.END, f"{i}. {error_text}\n", tag)
            terminalsem.config(state="disabled")
        else:
            terminalsem.config(state="normal")
            terminalsem.delete("1.0", tk.END)
            terminalsem.insert(tk.END, "¡No se encontraron errores semánticos! ✓", "success")
            # no se ve el
            terminalsem.tag_configure("success", foreground="white")
            terminalsem.config(state="disabled")

        # Generar código intermedio SIEMPRE (independientemente del modo)
        # El modo controla si se ejecuta o no
        exe_ci_debug(SEM.tree)


# Variable global para controlar la ejecución
vm_running = False
vm_instance = None

def exe_ci_debug(ast: ASTNode):
    """Genera código intermedio, lo guarda en un archivo y prepara la ejecución CON DEBUG"""
    global vm_instance
    
    try:
        # Generar código intermedio
        generator = gc.IntermediateCodeGenerator()
        code = generator.generate(ast)
        
        print("\n=== CÓDIGO INTERMEDIO GENERADO ===")
        for i, instruction in enumerate(code, 1):
            print(f"{i:3d}: {instruction}")
        print("="*50)
        
        # Obtener la ruta del archivo actual
        ruta_archivo = FILER.getRuta()
        
        # Determinar la ruta para guardar el código intermedio
        if ruta_archivo and ruta_archivo != "":
            # Si hay un archivo abierto, guardar en la misma carpeta con el mismo nombre
            import os
            carpeta = os.path.dirname(ruta_archivo)  # Obtener la carpeta
            nombre_archivo = os.path.splitext(os.path.basename(ruta_archivo))[0]  # Nombre sin extensión
            archivo_ci = os.path.join(carpeta, f"{nombre_archivo}.ci")  # Extensión .ci
        else:
            # Si no hay archivo abierto, usar la ruta por defecto
            archivo_ci = "codigo_intermedio.ci"
        
        # Guardar código intermedio SIN números
        with open(archivo_ci, "w", encoding="utf-8") as f:
            for instruction in code:
                f.write(f"{instruction}\n")
        
        mensaje.set(f"Código intermedio guardado en '{archivo_ci}'")
        
        # Verificar el modo de ejecución
        modo = CONF.getModo()
        
        if modo == 'compilar':
            # Solo compilar, no ejecutar
            terminalej.config(state="normal")
            terminalej.delete("1.0", tk.END)
            terminalej.insert(tk.END, "=== COMPILACIÓN COMPLETADA ===\n")
            terminalej.insert(tk.END, f"\nCódigo intermedio generado y guardado en:\n{archivo_ci}\n")
            terminalej.config(state="disabled")
            mensaje.set("Compilación completada exitosamente")
        else:
            # Compilar y ejecutar o solo ejecutar
            # Limpiar terminal antes de ejecutar
            terminalej.config(state="normal")
            terminalej.delete("1.0", tk.END)
            terminalej.insert(tk.END, "=== EJECUTANDO CÓDIGO ===\n\n")
            terminalej.config(state="disabled")
            
            # Guardar la ruta del archivo CI para usarla en la ejecución
            ejecutar_maquina_virtual_debug(code, archivo_ci)  
    except Exception as e:
        terminalej.config(state="normal")
        terminalej.insert(tk.END, f"\n❌ Error durante la generación: {str(e)}\n")
        terminalej.config(state="disabled")
        mensaje.set(f"Error: {str(e)}")
        print(f"Error completo: {e}")
        import traceback
        traceback.print_exc()


# También agrega esta versión de debug de la máquina virtual
def ejecutar_maquina_virtual_debug(code, archivo_ci="codigo_intermedio.ci"):
    """Ejecuta la máquina virtual con DEBUG completo usando el archivo de código intermedio"""
    global vm_running, vm_instance
    
    def gui_output(text):
        """Maneja salida a la terminal de ejecución"""
        try:
            terminalej.config(state="normal")
            terminalej.insert(tk.END, text)
            terminalej.see(tk.END)
            terminalej.config(state="disabled")
            root.update_idletasks()
        except Exception as e:
            print(f"Error en output: {e}")
    
    def gui_input(prompt):
        """Maneja entrada de usuario desde GUI"""
        try:
            gui_output(prompt + " ")
            
            input_dialog = tk.Toplevel(root)
            input_dialog.title("Entrada de datos")
            input_dialog.geometry("400x150")
            input_dialog.transient(root)
            input_dialog.grab_set()
            
            input_dialog.update_idletasks()
            x = (root.winfo_screenwidth() // 2) - (400 // 2)
            y = (root.winfo_screenheight() // 2) - (150 // 2)
            input_dialog.geometry(f"+{x}+{y}")
            
            label = tk.Label(input_dialog, text=prompt, font=("Arial", 11))
            label.pack(pady=10)
            
            entry_var = tk.StringVar()
            entry = tk.Entry(input_dialog, textvariable=entry_var, font=("Arial", 12), width=30)
            entry.pack(pady=10)
            entry.focus_set()
            
            result = {"value": None, "submitted": False}
            
            def on_submit():
                result["value"] = entry_var.get()
                result["submitted"] = True
                input_dialog.destroy()
            
            def on_cancel():
                result["submitted"] = False
                input_dialog.destroy()
            
            button_frame = tk.Frame(input_dialog)
            button_frame.pack(pady=10)
            
            ok_button = tk.Button(button_frame, text="Aceptar", command=on_submit, 
                                 width=10, bg="#4CAF50", fg="white")
            ok_button.pack(side="left", padx=5)
            
            cancel_button = tk.Button(button_frame, text="Cancelar", command=on_cancel,
                                     width=10, bg="#f44336", fg="white")
            cancel_button.pack(side="left", padx=5)
            
            entry.bind("<Return>", lambda e: on_submit())
            entry.bind("<Escape>", lambda e: on_cancel())
            
            input_dialog.wait_window()
            
            if not result["submitted"]:
                raise Exception("Entrada cancelada por el usuario.")
            
            gui_output(result["value"] + "\n")
            return result["value"]
            
        except Exception as e:
            gui_output(f"\n❌ Error en entrada: {str(e)}\n")
            raise e
    
    try:
        vm_instance = VirtualMachine.VirtualMachine(
            input_handler=gui_input,
            output_handler=gui_output
        )
        
        vm_running = True
        
        # Usar el método run() que hace pre-escaneo de etiquetas antes de ejecutar
        vm_instance.run(code)
        
        # terminalej.config(state="normal")
        # terminalej.insert(tk.END, "\n=== EJECUCIÓN COMPLETADA ===\n")
        # terminalej.insert(tk.END, f"\nEstado final de memoria: {vm_instance.memory}\n")
        # terminalej.config(state="disabled")
        
        mensaje.set("Ejecución completada exitosamente")
        vm_running = False
        
    except Exception as e:
        terminalej.config(state="normal")
        terminalej.insert(tk.END, f"\n\n❌ Error en tiempo de ejecución: {str(e)}\n")
        terminalej.config(state="disabled")
        mensaje.set(f"Error en ejecución: {str(e)}")
        vm_running = False
        print(f"Error completo: {e}")

def thread_ejecutar():
    """
    Función que simula la ejecución del código ingresado.
    Verifica el modo de ejecución y actúa en consecuencia.
    """
    modo = CONF.getModo()
    
    # Si el modo es solo "ejecutar", verificar que exista compilación previa
    if modo == 'ejecutar':
        # Determinar la ruta del archivo compilado
        ruta_archivo = FILER.getRuta()
        
        if ruta_archivo and ruta_archivo != "":
            # Si hay un archivo abierto, buscar en la misma carpeta con el mismo nombre
            carpeta = os.path.dirname(ruta_archivo)
            nombre_archivo = os.path.splitext(os.path.basename(ruta_archivo))[0]
            archivo_ci = os.path.join(carpeta, f"{nombre_archivo}.ci")
        else:
            # Si no hay archivo abierto, usar la ruta por defecto
            archivo_ci = "codigo_intermedio.ci"
        
        if not os.path.exists(archivo_ci):
            terminalej.config(state="normal")
            terminalej.delete("1.0", END)
            terminalej.insert(END, "❌ ERROR: No hay código compilado.\n")
            terminalej.insert(END, "\nDebes compilar primero usando:\n")
            terminalej.insert(END, "  • Botón 'Compilar' (Ctrl+Shift+C)\n")
            terminalej.insert(END, "  • Botón 'Compilar y Ejecutar' (Ctrl+R)\n")
            terminalej.insert(END, "  • Menú 'Ejecutar' > 'Compilar y Ejecutar'\n")
            terminalej.config(state="disabled")
            mensaje.set("Error: Se requiere compilar el código primero")
            return
        # Si existe el archivo compilado, ejecutar directamente sin compilar
        else:
            terminalej.config(state="normal")
            terminalej.delete("1.0", END)
            terminalej.insert(END, "Ejecutando código compilado...\n")
            terminalej.config(state="disabled")
            mensaje.set("Ejecutando código compilado...")
            
            try:
                with open(archivo_ci, "r", encoding="utf-8") as f:
                    code = f.readlines()
                # Ejecutar la máquina virtual
                ejecutar_maquina_virtual_debug(code, archivo_ci)
            except Exception as e:
                terminalej.config(state="normal")
                terminalej.insert(tk.END, f"\n❌ Error al ejecutar: {str(e)}\n")
                terminalej.config(state="disabled")
                mensaje.set(f"Error: {str(e)}")
            return
    
    # Si el modo es "compilar" o "compilar_ejecutar", hacer la compilación completa
    contenido = texto.get("1.0", 'end-1c')  # Obtiene el contenido del editor
    if contenido.strip() == "":
        mensaje.set("No hay código para ejecutar")
        return  
    else:
        # guardar el codigo 
        guardar()

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
        terminalej.insert(END, "Analizando código...\n")
        terminalej.config(state="disabled")

        mensaje.set("Analizando código...")
        
        DFA.process(contenido)  # Establece el texto en el analizador léxico
        DFA.genarcherrores("errores.tk")  # Generar archivo de errores
        DFA.deleteCommentandError()  # Elimina los comentarios del texto

        for token in DFA.tokens:
            terminalex.config(state="normal")
            terminalex.insert(END, f"{token[1]:<20} {token[0]:<18} (línea {token[2]}, columna {token[3]})\n")

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

def on_key_press(event):
    """Maneja la pulsación de teclas especiales como Tab."""
    if event.keysym == 'Tab':
        # Insertar 4 espacios en lugar de un tabulador
        texto.insert(INSERT, "    ")
        return 'break'  # Evitar que se procese el Tab por defecto

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

# Menú de Ejecución
ejemenu = Menu(menubar, tearoff=0)
ejemenu.add_command(label="Compilar (Ctrl+Shift+C)", command=lambda: ejecutar_codigo('compilar'))
ejemenu.add_command(label="Ejecutar - Requiere compilar primero (Ctrl+E)", command=lambda: ejecutar_codigo('ejecutar'))
ejemenu.add_separator()
ejemenu.add_command(label="Compilar y Ejecutar (Ctrl+R)", command=lambda: ejecutar_codigo('compilar_ejecutar'))
menubar.add_cascade(menu=ejemenu, label="Ejecutar")

Configmenu= Menu(menubar, tearoff=0)
Configmenu.add_command(label="Color texto", command=colortexto)
Configmenu.add_command(label="Ejecución", command=confex)
menubar.add_cascade(menu=Configmenu, label="Configuración")

# Menú superior
menubar.config(bg="#2d2d2d", fg="#d4d4d4")
filemenu.config(bg="#2d2d2d", fg="#d4d4d4", activebackground="#3c3c3c", activeforeground="#d4d4d4")
ejemenu.config(bg="#2d2d2d", fg="#d4d4d4", activebackground="#3c3c3c", activeforeground="#d4d4d4")
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
ToolTip(nuevo_btn, "Crear nuevo archivo (Ctrl+N)")

abrir_icon = PhotoImage(file="icons/abrir.png")
abrir_icon = abrir_icon.subsample(20, 20)
abrir_btn = Button(iconbar, image=abrir_icon, command=abrir, bg="#999999", activebackground="#3c3c3c")
abrir_btn.pack(side="left", padx=5, pady=5)
ToolTip(abrir_btn, "Abrir archivo (Ctrl+O)")

guardar_icon = PhotoImage(file="icons/guardar.png")
guardar_icon = guardar_icon.subsample(20, 20)
guardar_btn = Button(iconbar, image=guardar_icon, command=guardar, bg="#999999", activebackground="#3c3c3c")
guardar_btn.pack(side="left", padx=5, pady=5)
ToolTip(guardar_btn, "Guardar archivo (Ctrl+S)")

guardar_como_icon = PhotoImage(file="icons/guardar_como.png")
guardar_como_icon = guardar_como_icon.subsample(20, 20)
guardar_como_btn = Button(iconbar, image=guardar_como_icon, command=guardar_como, bg="#999999", activebackground="#3c3c3c")
guardar_como_btn.pack(side="left", padx=5, pady=5)
ToolTip(guardar_como_btn, "Guardar como... (Ctrl+G)")

compilar_icon = PhotoImage(file="icons/compile.png")
compilar_icon = compilar_icon.subsample(20, 20)
compilar_btn = Button(iconbar, image=compilar_icon, command=lambda: ejecutar_codigo('compilar'), bg="#999999", activebackground="#3c3c3c")
compilar_btn.pack(side="left", padx=5, pady=5)
ToolTip(compilar_btn, "Compilar código (Ctrl+Shift+C)")

ejecutar_icon = PhotoImage(file="icons/run.png")
ejecutar_icon = ejecutar_icon.subsample(20, 20)
ejecutar_btn = Button(iconbar, image=ejecutar_icon, command=lambda: ejecutar_codigo('ejecutar'), bg="#999999", activebackground="#3c3c3c")
ejecutar_btn.pack(side="left", padx=5, pady=5)
ToolTip(ejecutar_btn, "Ejecutar código compilado (Ctrl+E)\n⚠️ Requiere compilar primero")

ejecom_icon = PhotoImage(file="icons/eje_comp.png")
ejecom_icon = ejecom_icon.subsample(20, 20)
ejecom_btn = Button(iconbar, image=ejecom_icon, command=lambda: ejecutar_codigo('compilar_ejecutar'), bg="#999999", activebackground="#3c3c3c")
ejecom_btn.pack(side="left", padx=5, pady=5)
ToolTip(ejecom_btn, "Compilar y ejecutar código (Ctrl+R)")


# divicion
mainpanel = ttk.PanedWindow(root, orient=tk.VERTICAL)
mainpanel.pack(fill="both", expand=True)

#superior horizontal
toppanel = ttk.PanedWindow(mainpanel, orient=tk.HORIZONTAL)
mainpanel.add(toppanel, weight=1)

# Crear estilo para la tabla
style = ttk.Style()
style.theme_use('default')

# Configurar colores y altura de filas para Treeview
style.configure("Treeview",
                background="#2e2e2e",
                foreground="white",
                fieldbackground="#2e2e2e",
                rowheight=30,  # Aumentar la altura de las filas
                font=('Arial', 10))  # Fuente para el contenido

# Configurar los encabezados
style.configure("Treeview.Heading",
                background="#3e3e3e",
                foreground="white",
                font=('Arial', 11, 'bold'))

# Cambiar color de la fila seleccionada
style.map('Treeview', background=[('selected', '#4e4e4e')])

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
texto = Text(frame, bd=0, padx=6, pady=4, font=("Consolas", 12), undo=True, wrap="none", tabs=("4c",))
# Colores para el área de texto principal
texto.config(bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4")
# Configurar el espaciado de tabuladores (4 espacios)
texto.config(highlightthickness=0)  # Eliminar borde de enfoque
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

# Tabla para símbolos
frame_simbtable = Frame(notebook_terminal, bg="#1e1e1e")
terminaltab = ttk.Treeview(frame_simbtable, columns=("Tipo","Valor","Usada","Linea"), show="tree headings")

# Encabezados
terminaltab.heading("#0", text="Variable")
terminaltab.heading("Tipo", text="Tipo")
terminaltab.heading("Valor", text="Valor")
terminaltab.heading("Usada", text="Usada")
terminaltab.heading("Linea", text="Linea")

# Ajustes de columnas
terminaltab.column("#0", width=100, anchor="center")
terminaltab.column("Tipo", width=100, anchor="center")
terminaltab.column("Valor", width=100, anchor="center")
terminaltab.column("Usada", width=50, anchor="center")
terminaltab.column("Linea", width=300, anchor="w")

# Scroll
scrollbar_tab = ttk.Scrollbar(frame_simbtable, orient="vertical", command=terminaltab.yview)
terminaltab.configure(yscrollcommand=scrollbar_tab.set)

terminaltab.grid(row=0, column=0, sticky="nsew")
scrollbar_tab.grid(row=0, column=1, sticky="ns")

frame_simbtable.grid_rowconfigure(0, weight=1)
frame_simbtable.grid_columnconfigure(0, weight=1)

notebook_terminal.add(frame_simbtable, text="Tabla de simbolos")

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
texto.bind("<KeyPress>", on_key_press)  # Manejar Tab como 4 espacios

#combinaciones de teclas
root.bind("<Control-n>", lambda e: nuevo())
root.bind("<Control-o>", lambda e: abrir())
root.bind("<Control-s>", lambda e: guardar())
root.bind("<Control-g>", lambda e: guardar_como())
root.bind("<Control-w>", lambda e: exit())

# Tecla rápida para compilar y ejecutar el código
root.bind("<Control-e>", lambda e: ejecutar_codigo('compilar_ejecutar'))

# Tecla rápida para solo compilar
root.bind("<Control-Shift-C>", lambda e: ejecutar_codigo('compilar'))

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

# verificar si hay un archivo abierto previamente
if FILER.load_state():
    ruta_anterior = FILER.get_previous_file()
    if ruta_anterior and os.path.exists(ruta_anterior):
        FILER.setRuta(ruta_anterior)
        leer_archivo(ruta_anterior)

# Iniciar el bucle principal en un hilo separado
tread_main=threading.Thread(target=root.mainloop())  # Bucle principal