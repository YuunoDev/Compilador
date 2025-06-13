import customtkinter as ctk
from Anlex import *
from customtkinter import *
import tkinter as tk

class IDE:
    def __init__(self):
        # Partes de la vista del IDE
        self.root = None        #Ventana principal
        self.windows = None     #Frame encargado de particionar ventanas
        self.wintext = None     #Ventana de editor de texto
        self.winresul = None    #Ventana de resultados
        self.winterminal = None #Ventana de terminales
        self.text_area = None  
        
        # menu bar and menus
        self.menu_bar = None
        self.file_menu = None
        self.run_menu = None
        self.icon_bar = None

        #iconos
        self.newfile_icon = None
        self.openfile_icon = None
        self.savefile_icon = None
        self.savewith_icon = None

        #icons buttons
        self.newfile_button = None
        self.openfile_button = None
        self.savefile_button = None
        self.savewith_button = None
        self.icon_font = ("Arial", 16)
        
        # Botones con emojis
        self.buttons = [
            ("🆕", "Nuevo"),
            ("📂", "Abrir"),
            ("💾", "Guardar"),
            ("📝", "Guardar como"),
            ("▶️", "Ejecutar"),
            ("🧹", "Limpiar")
        ]
        self.hbuttons = 32
        self.wbuttons = 36

        # Frames del editor de texto
        self.text_frame_1 = None
        self.text_line = None
        self.text_editor = None

        # pestañas de resultados
        self.notebook_results = None
        self.termresultlex = None
        self.termresultsin = None

        # Variables para funcionalidad básica
        self.ruta = ""
        self.edit = False
        self.Automat = Automata()
        self.current_tab = None
        self.termsem = None  # Nueva variable para la pestaña semántica

        # Definir colores para cada tipo de token - Material palenight inspired
        self.colores = {
            "COMENTARIO": "#676E95",      # Gris azulado para comentarios
            "IDENTIFICADOR": "#C792EA",   # Lavanda/púrpura para identificadores
            "RESERVADA": "#82AAFF",       # Azul claro para palabras clave
            "OTRO": "#A6ACCD",            # Gris claro, para texto neutro
            "OPERADOR": "#89DDFF",        # Azul verdoso claro para operadores
            "NUMERO ENTERO": "#F78C6C",   # Naranja para números
            "ASIGNACION": "#FFCB6B",      # Amarillo dorado para asignaciones
            "CADENA": "#C3E88D",          # Verde claro para cadenas
            "COMPARACION": "#89DDFF",     # Mismo que operador por coherencia
            "SIMBOLO": "#82AAFF",         # Azul claro para símbolos
            "LOGICO": "#FF5370",          # Rojo para operadores lógicos
            "ERRORES": "#FF5370",         # Rojo para errores
            "NUMERO REAL": "#F78C6C",     # Naranja para números reales
            "DESCONOCIDO": "#BFC7D5",     # Gris claro para desconocidos
        }

        # Colores de la interfaz
        self.colors = {
            "bg_main": "#292D3E",        # Background principal (Material Palenight)
            "bg_editor": "#292D3E",       # Fondo del editor
            "bg_line_numbers": "#1B1E2B", # Fondo de números de línea
            "bg_results": "#1B1E2B",      # Fondo de resultados
            "fg_text": "#A6ACCD",         # Color de texto principal
            "accent": "#82AAFF",          # Color de acento
            "selection": "#3A3F58",       # Color de selección
            "cursor": "#FFCB6B",          # Color del cursor
            "line_highlight": "#2C3149",  # Resaltado de línea actual
            "terminal_bg": "#1B1E2B",     # Fondo del terminal
        }

        self.init_window()

    def new_file(self):
        pass

    def open_file(self):
        pass

    def save_file(self):
        pass

    def compile(self):
        pass

    def execute(self):
        pass
        
    def init_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Crear la ventana con mejor aspecto
        self.root = ctk.CTk()
        self.root.geometry("1200x800")
        self.root.title("CodeStudio IDE")
        self.root.configure(fg_color=self.colors["bg_main"])
        
        # Crear barra de menú con mejor aspecto
        self.menu_bar = tk.Menu(self.root, bg=self.colors["bg_main"], fg=self.colors["fg_text"], 
                               activebackground=self.colors["selection"], activeforeground="white")
        self.root.config(menu=self.menu_bar)

        # Menú de Archivo con mejor aspecto
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors["bg_main"], 
                                fg=self.colors["fg_text"], 
                                activebackground=self.colors["selection"], 
                                activeforeground="white")
        self.file_menu.add_command(label="Nuevo", command=self.new_file)
        self.file_menu.add_command(label="Abrir", command=self.open_file)
        self.file_menu.add_command(label="Guardar", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.root.quit)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)

        # Menú de Ejecución con mejor aspecto
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.colors["bg_main"], 
                               fg=self.colors["fg_text"], 
                               activebackground=self.colors["selection"], 
                               activeforeground="white")
        self.run_menu.add_command(label="Ejecutar", command=self.compile)
        self.menu_bar.add_cascade(label="Ejecutar", menu=self.run_menu)
        
        # Barra de herramientas mejorada
        self.icon_bar = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color=self.colors["bg_line_numbers"]
        )
        self.icon_bar.pack(side="top", fill="x", pady=0)

        # Crear botones con mejor aspecto
        button_color = self.colors["bg_line_numbers"]
        hover_color = self.colors["selection"]
        
        self.newfile_button = ctk.CTkButton(
            self.icon_bar, text=self.buttons[0][0], 
            text_color=self.colors["fg_text"],
            command=self.new_file, 
            font=self.icon_font,
            width=self.wbuttons, 
            height=self.hbuttons,
            fg_color=button_color,
            hover_color=hover_color,
            corner_radius=6
        )
        self.newfile_button.pack(side="left", padx=5, pady=5)
        
        self.openfile_button = ctk.CTkButton(
            self.icon_bar, text=self.buttons[1][0], 
            text_color=self.colors["fg_text"],
            command=self.open_file, 
            font=self.icon_font, 
            width=self.wbuttons, 
            height=self.hbuttons,
            fg_color=button_color,
            hover_color=hover_color,
            corner_radius=6
        )
        self.openfile_button.pack(side="left", padx=5, pady=5)
        
        self.savefile_button = ctk.CTkButton(
            self.icon_bar, text=self.buttons[2][0], 
            text_color=self.colors["fg_text"],
            command=self.save_file, 
            font=self.icon_font, 
            width=self.wbuttons, 
            height=self.hbuttons,
            fg_color=button_color,
            hover_color=hover_color,
            corner_radius=6
        )
        self.savefile_button.pack(side="left", padx=5, pady=5)
        
        self.savewith_button = ctk.CTkButton(
            self.icon_bar, text=self.buttons[3][0], 
            text_color=self.colors["fg_text"],
            command=self.save_file, 
            font=self.icon_font, 
            width=self.wbuttons, 
            height=self.hbuttons,
            fg_color=button_color,
            hover_color=hover_color,
            corner_radius=6
        )
        self.savewith_button.pack(side="left", padx=5, pady=5)
        
        self.run_button = ctk.CTkButton(
            self.icon_bar, text=self.buttons[4][0], 
            text_color="#C3E88D",  # Color verde para el botón de ejecución
            command=self.compile, 
            font=self.icon_font, 
            width=self.wbuttons, 
            height=self.hbuttons,
            fg_color=button_color,
            hover_color=hover_color,
            corner_radius=6
        )
        self.run_button.pack(side="left", padx=5, pady=5)

        # Separador visual
        separator = ctk.CTkFrame(self.icon_bar, height=20, width=1, fg_color=self.colors["selection"])
        separator.pack(side="left", padx=10, pady=5)
        
        # PanedWindow mejorado con colores personalizados
        self.windows = tk.PanedWindow(
            self.root, 
            orient=tk.VERTICAL,
            bg=self.colors["bg_main"], 
            sashrelief=tk.FLAT, 
            sashwidth=4,
            sashpad=3
        )
        self.windows.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        self.wintext = tk.PanedWindow(
            self.windows, 
            orient=tk.HORIZONTAL,
            bg=self.colors["bg_main"], 
            sashrelief=tk.FLAT, 
            sashwidth=4,
            sashpad=3
        )
        self.wintext.pack(fill="both", expand=True)

        # Crear frame para texto y lineas con bordes redondeados
        self.text_frame_1 = ctk.CTkFrame(self.wintext, corner_radius=8, fg_color=self.colors["bg_editor"])
        self.text_frame_1.pack(expand=True, fill="both", padx=8, pady=8)

        # Crear el área de líneas mejorada
        self.text_line = ctk.CTkTextbox(
            self.text_frame_1, 
            width=40, 
            corner_radius=0, 
            fg_color=self.colors["bg_line_numbers"], 
            text_color="#676E95",  # Color gris para números de línea
            font=("JetBrains Mono", 12),
            border_width=0
        )
        self.text_line.configure(
            padx=8, 
            pady=8,
            takefocus=0,
            state="disabled", 
            cursor="arrow"
        )
        self.text_line.pack(side="left", fill="y")

        # Crear el área de texto mejorada
        self.text_editor = ctk.CTkTextbox(
            self.text_frame_1, 
            fg_color=self.colors["bg_editor"],
            text_color=self.colors["fg_text"],
            font=("JetBrains Mono", 12), 
            undo=True, 
            wrap="none",
            padx=8, 
            pady=8,
            border_width=0,
            corner_radius=0,
            scrollbar_button_color=self.colors["selection"],
            scrollbar_button_hover_color=self.colors["accent"]
        )
        self.text_editor.pack(expand=True, fill="both", side="left")
        
        # Agregar un poco de texto de ejemplo para mostrar cómo se ve
        self.text_editor.insert("1.0", "def hello_world():\n    print('Hello, World!')\n\n# Este es un comentario\nif __name__ == '__main__':\n    hello_world()\n")

        self.wintext.add(self.text_frame_1)

        # Crear frame de Resultados mejorado
        self.winresul = ctk.CTkFrame(self.wintext, corner_radius=8, fg_color=self.colors["bg_results"])
        self.winresul.pack(fill="both", expand=True, side="right", padx=8, pady=8)
        
        # Crear un frame para botones de pestañas simplificados
        tab_buttons_frame = ctk.CTkFrame(
            self.winresul,
            fg_color=self.colors["bg_results"],
            corner_radius=0
        )
        tab_buttons_frame.pack(fill="x", padx=5, pady=0)
        
        # Variables para manejar pestañas
        self.current_tab = tk.StringVar(value="Léxico")
        
        # Función para cambiar pestaña
        def change_tab(tab_name):
            self.current_tab.set(tab_name)
            # Ocultar todos los paneles
            self.termresultlex.pack_forget()
            self.termresultsin.pack_forget()
            self.termsem.pack_forget()
            
            # Mostrar el panel seleccionado
            if tab_name == "Léxico":
                self.termresultlex.pack(fill="both", expand=True, padx=5, pady=5)
            elif tab_name == "Sintáctico":
                self.termresultsin.pack(fill="both", expand=True, padx=5, pady=5)
            elif tab_name == "Semántico":
                self.termsem.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Actualizar apariencia de botones
            lex_btn.configure(fg_color=self.colors["selection"] if tab_name == "Léxico" else "transparent")
            sin_btn.configure(fg_color=self.colors["selection"] if tab_name == "Sintáctico" else "transparent")
            sem_btn.configure(fg_color=self.colors["selection"] if tab_name == "Semántico" else "transparent")
        
        # Crear botones de pestañas
        lex_btn = ctk.CTkButton(
            tab_buttons_frame, 
            text="Léxico",
            fg_color=self.colors["selection"],  # Activo por defecto
            text_color=self.colors["fg_text"],
            hover_color=self.colors["selection"],
            corner_radius=4,
            height=28,
            command=lambda: change_tab("Léxico")
        )
        lex_btn.pack(side="left", padx=(5,1), pady=5)
        
        sin_btn = ctk.CTkButton(
            tab_buttons_frame, 
            text="Sintáctico",
            fg_color="transparent",
            text_color=self.colors["fg_text"],
            hover_color=self.colors["selection"],
            corner_radius=4,
            height=28,
            command=lambda: change_tab("Sintáctico")
        )
        sin_btn.pack(side="left", padx=1, pady=5)
        
        sem_btn = ctk.CTkButton(
            tab_buttons_frame, 
            text="Semántico",
            fg_color="transparent",
            text_color=self.colors["fg_text"],
            hover_color=self.colors["selection"],
            corner_radius=4,
            height=28,
            command=lambda: change_tab("Semántico")
        )
        sem_btn.pack(side="left", padx=(1,5), pady=5)
        
        # Crear un frame para el contenido
        content_frame = ctk.CTkFrame(
            self.winresul,
            fg_color=self.colors["bg_results"],
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=5, pady=0)
        
        # Crear los contenidos de las pestañas
        self.termresultlex = ctk.CTkTextbox(
            content_frame,
            fg_color=self.colors["terminal_bg"],
            text_color=self.colors["fg_text"],
            font=("JetBrains Mono", 11),
            wrap="none",
            corner_radius=6
        )
        
        self.termresultsin = ctk.CTkTextbox(
            content_frame,
            fg_color=self.colors["terminal_bg"],
            text_color=self.colors["fg_text"],
            font=("JetBrains Mono", 11),
            wrap="none",
            corner_radius=6
        )
        
        self.termsem = ctk.CTkTextbox(
            content_frame,
            fg_color=self.colors["terminal_bg"],
            text_color=self.colors["fg_text"],
            font=("JetBrains Mono", 11),
            wrap="none",
            corner_radius=6
        )
        
        # Mostrar la pestaña inicial (Léxico)
        self.termresultlex.pack(fill="both", expand=True, padx=5, pady=5)

        self.wintext.add(self.winresul)

        # Crear frame de terminales mejorado
        self.winterminal = ctk.CTkFrame(self.windows, corner_radius=8, fg_color=self.colors["terminal_bg"])
        self.winterminal.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Añadir terminal
        terminal_label = ctk.CTkLabel(
            self.winterminal,
            text="Terminal",
            font=("JetBrains Mono", 12, "bold"),
            text_color=self.colors["fg_text"]
        )
        terminal_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        terminal = ctk.CTkTextbox(
            self.winterminal,
            fg_color=self.colors["terminal_bg"],
            text_color="#A6ACCD",
            font=("JetBrains Mono", 11),
            wrap="word",
            corner_radius=6
        )
        terminal.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Insertar algunos resultados de ejemplo
        self.termresultlex.insert("1.0", "Token: RESERVADA\tLexema: 'def'\tLínea: 1\nToken: IDENTIFICADOR\tLexema: 'hello_world'\tLínea: 1\n")
        self.termresultsin.insert("1.0", "Análisis sintáctico completado con éxito.\n")
        self.termsem.insert("1.0", "Análisis semántico completado.\nNo se encontraron errores de tipo.\n")
        terminal.insert("1.0", "$ python main.py\nHello, World!\n$")

        # Ajustar las proporciones de los paneles
        self.windows.add(self.wintext, height=550)
        self.windows.add(self.winterminal, height=250)
        self.wintext.add(self.text_frame_1, width=750)
        self.wintext.add(self.winresul, width=450)

# Iniciar la aplicación
Windo = IDE()
Windo.root.mainloop()