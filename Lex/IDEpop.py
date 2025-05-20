import customtkinter as ctk
from customtkinter import *
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Asumimos que la clase Automata está definida en Anlex.py
try:
    from Anlex import Automata
except ImportError:
    # Clase temporal para pruebas si no existe Anlex
    class Automata:
        def __init__(self):
            pass

class IDE:
    def __init__(self):
        # Partes de la vista del IDE
        self.window = None
        
        # Menu bar y menus
        self.menu_bar = None
        self.file_menu = None
        self.run_menu = None
        self.config_menu = None
        self.icon_bar = None

        # Botones con iconos
        self.buttons = [
            ("🆕", "Nuevo", self.new_file),
            ("📂", "Abrir", self.open_file),
            ("💾", "Guardar", self.save_file),
            ("📝", "Guardar como", self.save_file_as),
            ("▶️", "Ejecutar", self.execute)
        ]
        self.hbuttons = 30
        self.wbuttons = 30

        # Paneles de texto
        self.main_paned = None
        self.editor_frame = None
        self.terminal_frame = None
        self.line_numbers = None
        self.text_editor = None
        
        # Notebook para terminales
        self.terminal_notebook = None
        self.execution_terminal = None
        self.lexical_terminal = None 
        self.syntax_terminal = None
        self.semantic_terminal = None
        
        # Notebook para errores
        self.error_notebook = None
        self.lexical_errors = None
        self.syntax_errors = None
        self.semantic_errors = None

        # Barra de estado
        self.status_bar = None
        self.status_label = None
        self.line_col_label = None

        # Variables y clase usada para funcionalidades del IDE
        self.file_path = ""
        self.modified = False
        self.automata = Automata()

        # Iniciar ventana
        self.init_window()
        
        # Configurar eventos
        self.setup_events()

    def init_window(self):
        # Configurar apariencia
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Crear la ventana
        self.window = ctk.CTk()
        self.window.geometry("1200x800")
        self.window.title("IDE PyC")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Crear barra de menú con tkinter.Menu
        self.menu_bar = tk.Menu(self.window, bg="#2e2e2e", fg="white", 
                                activebackground="#444", activeforeground="white")
        self.window.config(menu=self.menu_bar)

        # Menú Archivo
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#2e2e2e", fg="white", 
                                activebackground="#444", activeforeground="white")
        self.file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Guardar como", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.on_close)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)

        # Menú Ejecutar
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#2e2e2e", fg="white", 
                               activebackground="#444", activeforeground="white")
        self.run_menu.add_command(label="Ejecutar", command=self.execute, accelerator="F5")
        self.run_menu.add_command(label="Compilar", command=self.compile, accelerator="F6")
        self.run_menu.add_command(label="Limpiar Terminales", command=self.clear_terminals)
        self.menu_bar.add_cascade(label="Ejecutar", menu=self.run_menu)
        
        # Menú Configuración
        self.config_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#2e2e2e", fg="white", 
                                  activebackground="#444", activeforeground="white")
        self.config_menu.add_command(label="Preferencias", command=self.open_preferences)
        self.menu_bar.add_cascade(label="Configuración", menu=self.config_menu)

        # Barra de iconos
        self.icon_bar = ctk.CTkFrame(self.window, corner_radius=0, fg_color="#333333", height=40)
        self.icon_bar.pack(side="top", fill="x", pady=0)
        
        # Crear los botones de la barra de iconos
        for icon, tooltip, command in self.buttons:
            btn = ctk.CTkButton(
                self.icon_bar, 
                text=icon, 
                text_color="white", 
                command=command, 
                font=("Arial", 18), 
                width=self.wbuttons, 
                height=self.hbuttons,
                fg_color="#444444",
                hover_color="#555555"
            )
            btn.pack(side="left", padx=3, pady=5)
            
            # Crear tooltip
            self.create_tooltip(btn, tooltip)

        # Crear un panel principal que se pueda redimensionar
        self.main_paned = tk.PanedWindow(self.window, orient=tk.VERTICAL, bg="#333333", sashwidth=5)
        self.main_paned.pack(fill="both", expand=True)
        
        # Panel superior para el editor
        self.editor_frame = ctk.CTkFrame(self.main_paned, corner_radius=0)
        self.main_paned.add(self.editor_frame, height=400)  # Peso inicial
        
        # Panel inferior para las terminales
        self.terminal_frame = ctk.CTkFrame(self.main_paned, corner_radius=0)
        self.main_paned.add(self.terminal_frame, height=200)  # Peso inicial

        # Configurar el área del editor
        self.setup_editor()
        
        # Configurar las terminales
        self.setup_terminals()
        
        # Configurar barra de estado
        self.setup_status_bar()
        
        # Asegurar que el editor recibe el foco inicial
        self.text_editor.focus_set()
        
        # Actualizar números de línea
        self.update_line_numbers()
        
    def setup_editor(self):
        # Crear un frame para el editor y los números de línea
        editor_content = ctk.CTkFrame(self.editor_frame, corner_radius=0)
        editor_content.pack(fill="both", expand=True)
        
        # Área de números de línea
        self.line_numbers = ctk.CTkTextbox(
            editor_content, 
            width=40, 
            corner_radius=0, 
            fg_color="#2d2d2d", 
            text_color="#888888",
            font=("Consolas", 12)
        )
        self.line_numbers.configure(padx=5, pady=5, takefocus=0, state="disabled", cursor="arrow")
        self.line_numbers.pack(side="left", fill="y")
        
        # Editor de código
        self.text_editor = ctk.CTkTextbox(
            editor_content, 
            fg_color="#1E1E1E",  # Color más oscuro como VSCode
            text_color="#CCCCCC",  # Texto claro
            font=("Consolas", 12), 
            undo=True, 
            wrap="none",
            padx=10, 
            pady=5,
            corner_radius=0
        )
        self.text_editor.pack(fill="both", expand=True, side="left")
        
        # Agregar scrollbar horizontal
        h_scrollbar = ctk.CTkScrollbar(
            editor_content,
            orientation="horizontal",
            command=self.text_editor.xview
        )
        h_scrollbar.pack(side="bottom", fill="x")
        self.text_editor.configure(xscrollcommand=h_scrollbar.set)
        
    def setup_terminals(self):
        # Crear notebook para las terminales
        self.terminal_notebook = ctk.CTkTabview(self.terminal_frame, corner_radius=0)
        self.terminal_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Agregar pestañas
        self.terminal_notebook.add("Terminal de Ejecución")
        self.terminal_notebook.add("Terminal Léxica")
        self.terminal_notebook.add("Terminal Sintáctica")
        self.terminal_notebook.add("Terminal Semántica")
        
        # Configurar terminales
        self.execution_terminal = self.create_terminal(self.terminal_notebook.tab("Terminal de Ejecución"))
        self.lexical_terminal = self.create_terminal(self.terminal_notebook.tab("Terminal Léxica"))
        self.syntax_terminal = self.create_terminal(self.terminal_notebook.tab("Terminal Sintáctica"))
        self.semantic_terminal = self.create_terminal(self.terminal_notebook.tab("Terminal Semántica"))
        
        # Crear notebook para errores
        self.error_notebook = ctk.CTkTabview(self.terminal_frame, corner_radius=0, height=100)
        self.error_notebook.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Agregar pestañas de errores
        self.error_notebook.add("Errores Léxicos")
        self.error_notebook.add("Errores Sintácticos")
        self.error_notebook.add("Errores Semánticos")
        
        # Configurar terminales de errores
        self.lexical_errors = self.create_terminal(self.error_notebook.tab("Errores Léxicos"), height=100)
        self.syntax_errors = self.create_terminal(self.error_notebook.tab("Errores Sintácticos"), height=100)
        self.semantic_errors = self.create_terminal(self.error_notebook.tab("Errores Semánticos"), height=100)
    
    def create_terminal(self, parent, height=None):
        terminal = ctk.CTkTextbox(
            parent,
            fg_color="#1A1A1A",
            text_color="#AAAAAA",
            font=("Consolas", 11),
            wrap="none",
            padx=5,
            pady=5,
            corner_radius=0
        )
        if height:
            terminal.configure(height=height)
        terminal.pack(fill="both", expand=True)
        terminal.configure(state="disabled")
        return terminal
    
    def setup_status_bar(self):
        self.status_bar = ctk.CTkFrame(self.window, height=25, corner_radius=0, fg_color="#333333")
        self.status_bar.pack(side="bottom", fill="x")
        
        # Etiqueta de estado (izquierda)
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", text_color="#AAAAAA")
        self.status_label.pack(side="left", padx=10)
        
        # Etiqueta de línea y columna (derecha)
        self.line_col_label = ctk.CTkLabel(self.status_bar, text="Ln 1, Col 0", text_color="#AAAAAA")
        self.line_col_label.pack(side="right", padx=10)

    def setup_events(self):
        # Vincular eventos de teclado
        self.window.bind("<Control-n>", lambda e: self.new_file())
        self.window.bind("<Control-o>", lambda e: self.open_file())
        self.window.bind("<Control-s>", lambda e: self.save_file())
        self.window.bind("<Control-Shift-S>", lambda e: self.save_file_as())
        self.window.bind("<F5>", lambda e: self.execute())
        self.window.bind("<F6>", lambda e: self.compile())
        
        # Vincular eventos para actualizar números de línea
        self.text_editor.bind("<KeyPress>", self.on_key_press)
        self.text_editor.bind("<KeyRelease>", self.on_key_release)
        self.text_editor.bind("<ButtonRelease-1>", self.update_cursor_position)
        self.text_editor.bind("<<Modified>>", self.on_modified)
        
        # Vincular eventos de scroll del editor
        self.text_editor.bind("<Configure>", self.update_line_numbers)
        
    def create_tooltip(self, widget, text):
        # Función para crear tooltips
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Crear ventana de tooltip
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tooltip, text=text, bg="#333333", fg="white",
                           relief="solid", borderwidth=1, padx=5, pady=2)
            label.pack()
            
        def leave(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def update_line_numbers(self, event=None):
        # Actualizar números de línea
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        
        # Obtener número de líneas en el editor
        line_count = self.text_editor.get("1.0", "end").count('\n')
        
        # Generar números de línea
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", line_numbers_text)
        
        # Alinear el scroll del editor y los números de línea
        self.line_numbers.yview_moveto(self.text_editor.yview()[0])
        
        self.line_numbers.configure(state="disabled")
    
    def on_key_press(self, event):
        # Marcar como modificado
        if event.keysym not in ('F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'):
            self.modified = True
            self.update_title()
    
    def on_key_release(self, event):
        # Actualizar números de línea y posición del cursor
        self.update_line_numbers()
        self.update_cursor_position()
    
    def on_modified(self, event=None):
        # Reset el flag modified del widget de texto
        self.text_editor.edit_modified(False)
    
    def update_cursor_position(self, event=None):
        # Actualizar posición del cursor en la barra de estado
        position = self.text_editor.index("insert").split('.')
        line = position[0]
        col = position[1]
        self.line_col_label.configure(text=f"Ln {line}, Col {col}")
    
    def update_title(self):
        # Actualizar título de la ventana con nombre de archivo
        filename = os.path.basename(self.file_path) if self.file_path else "Sin título"
        modified_indicator = "*" if self.modified else ""
        self.window.title(f"{filename}{modified_indicator} - IDE PyC")
    
    def new_file(self):
        # Verificar si hay cambios sin guardar
        if self.modified and messagebox.askyesno("Guardar cambios", 
                                                "¿Desea guardar los cambios antes de crear un nuevo archivo?"):
            self.save_file()
            
        # Limpiar editor
        self.text_editor.delete("1.0", "end")
        self.file_path = ""
        self.modified = False
        self.update_title()
        self.update_line_numbers()
        self.status_label.configure(text="Nuevo archivo creado")
    
    def open_file(self):
        # Verificar si hay cambios sin guardar
        if self.modified and messagebox.askyesno("Guardar cambios", 
                                                "¿Desea guardar los cambios antes de abrir otro archivo?"):
            self.save_file()
            
        # Abrir diálogo de archivo
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", content)
                self.file_path = file_path
                self.modified = False
                self.update_title()
                self.update_line_numbers()
                self.status_label.configure(text=f"Archivo abierto: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir el archivo: {str(e)}")
    
    def save_file(self):
        if not self.file_path:
            return self.save_file_as()
            
        try:
            content = self.text_editor.get("1.0", "end-1c")
            with open(self.file_path, "w") as file:
                file.write(content)
                
            self.modified = False
            self.update_title()
            self.status_label.configure(text=f"Archivo guardado: {os.path.basename(self.file_path)}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")
            return False
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.file_path = file_path
            return self.save_file()
        return False
    
    def compile(self):
        # Implementación de compilación
        if self.modified and messagebox.askyesno("Guardar cambios", 
                                               "¿Desea guardar los cambios antes de compilar?"):
            if not self.save_file():
                return
                
        self.status_label.configure(text="Compilando...")
        
        # Aquí iría la lógica de compilación usando el Automata
        # Por ahora solo un ejemplo
        
        content = self.text_editor.get("1.0", "end-1c")
        
        # Mostrar resultados en las terminales
        self.write_to_terminal(self.lexical_terminal, "Análisis léxico completado")
        self.write_to_terminal(self.syntax_terminal, "Análisis sintáctico completado")
        self.write_to_terminal(self.semantic_terminal, "Análisis semántico completado")
        
        # Ejemplo de errores (para demostración)
        self.write_to_terminal(self.lexical_errors, "Sin errores léxicos")
        self.write_to_terminal(self.syntax_errors, "Error en línea 3: se esperaba ';'")
        self.write_to_terminal(self.semantic_errors, "Sin errores semánticos")
        
        self.status_label.configure(text="Compilación completada")
    
    def execute(self):
        # Primero compilar
        self.compile()
        
        # Luego ejecutar
        self.status_label.configure(text="Ejecutando...")
        
        # Ejemplo de salida de ejecución
        self.write_to_terminal(self.execution_terminal, "Programa ejecutado correctamente\n")
        self.write_to_terminal(self.execution_terminal, "Resultado: Éxito")
        
        self.status_label.configure(text="Ejecución completada")
    
    def write_to_terminal(self, terminal, text):
        terminal.configure(state="normal")
        terminal.delete("1.0", "end")
        terminal.insert("1.0", text)
        terminal.configure(state="disabled")
    
    def clear_terminals(self):
        for terminal in [self.execution_terminal, self.lexical_terminal, 
                         self.syntax_terminal, self.semantic_terminal,
                         self.lexical_errors, self.syntax_errors, self.semantic_errors]:
            terminal.configure(state="normal")
            terminal.delete("1.0", "end")
            terminal.configure(state="disabled")
        
        self.status_label.configure(text="Terminales limpiadas")
    
    def open_preferences(self):
        # Implementación futura para preferencias
        messagebox.showinfo("Preferencias", "Esta funcionalidad está en desarrollo.")
    
    def on_close(self):
        if self.modified and messagebox.askyesno("Guardar cambios", 
                                               "¿Desea guardar los cambios antes de salir?"):
            self.save_file()
            
        self.window.destroy()

if __name__ == "__main__":
    app = IDE()
    app.window.mainloop()