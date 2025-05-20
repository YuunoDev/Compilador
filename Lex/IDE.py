import customtkinter as ctk
from Anlex import *
from customtkinter import *
import tkinter as tk

class IDE:
    def __init__(self):
        # Partes de la vista del IDE
        self.root = None        #Ventana principal
        self.windows = None     #Frame encanfado de particionar ventanas
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
        self.icon_font = ("Arial", 18)
        
        # Botones con emojis
        self.buttons = [
            ("🆕", "Nuevo"),
            ("📂", "Abrir"),
            ("💾", "Guardar"),
            ("📝", "Guardar como"),
            ("🧪", "Ejecutar"),
            ("🧹", "Limpiar")
        ]
        self.hbuttons= 28
        self.wbuttons= 28

        # Frames del editor de texto
        self.text_frame_1 = None
        self.text_line = None
        self.text_editor = None

        # penstañas de resultados
        self.notebook_results= None
        self.termresultlex = None
        self.termresultsin = None

        # varliables y clase usada para funcionalidades del IDE
        self.ruta = ""
        self.edit = False
        self.Automat = Automata()

        # Definir colores para cada tipo de token
        self.colores = {
            "COMENTARIO": "#407a33",      # Gris azulado apagado, sutil pero visible
            "IDENTIFICADOR": "#C678DD",   # Lavanda suave, usado para variables
            "RESERVADA": "#61AFEF",       # Azul fuerte, común en palabras clave
            "OTRO": "#ABB2BF",            # Gris claro, para texto neutro o no categorizado
            "OPERADOR": "#56B6C2",        # Azul verdoso, bien contrastado
            "NUMERO ENTERO": "#D19A66",   # Naranja suave, típico para números
            "ASIGNACION": "#E5C07B",      # Amarillo dorado, resalta sin molestar
            "CADENA": "#98C379",          # Verde claro, ideal para cadenas
            "COMPARACION": "#56B6C2",     # Igual que operador para coherencia
            "SIMBOLO": "#61AFEF",         # Azul claro, resalta bien en fondos oscuros
            "LOGICO": "#BE5046",          # Rojo ladrillo, da contraste a los operadores lógicos
            "ERRORES": "#FF0000",         # Rojo brillante, para errores
            "NUMERO REAL": "#D19A66",     # Naranja suave, para números reales
            "DESCONOCIDO": "#d4d4d4",     # Rojo brillante, para errores
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
        ctk.set_appearance_mode("dark")         # Opciones: "dark", "light", "system"
        ctk.set_default_color_theme("dark-blue")

        # Crear la ventana
        self.root = ctk.CTk()
        self.root.geometry("800x600")
        self.root.title("IDE")

        # Crear barra de menú con tkinter.Menu
        self.menu_bar = tk.Menu(self.root, bg="#2e2e2e", fg="white", activebackground="#444", activeforeground="white")
        self.root.config(menu=self.menu_bar)

        # Menú de Archivo
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#2e2e2e", fg="white", activebackground="#444", activeforeground="white")
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Menú de Ejecución
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#2e2e2e", fg="white", activebackground="#444", activeforeground="white")
        self.run_menu.add_command(label="Ejecutar", command=self.compile)
        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)
        self.root.config(menu=self.menu_bar)

        #iconbar
        # Crear la barra de iconos pegada arriba
        self.icon_bar = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color="transparent"  # Fondo transparente
        )

        # Empaquetar arriba, sin separación (pegado al top)
        self.icon_bar.pack(side="top", fill="x", pady=0)

        # Crear los iconos
        self.newfile_button = ctk.CTkButton(self.icon_bar, text=self.buttons[0][0], text_color="white", command=self.new_file, font=self.icon_font,width=self.wbuttons, height=self.hbuttons)
        self.newfile_button.pack(side="left", padx=5, pady=5)
        self.openfile_button = ctk.CTkButton(self.icon_bar, text=self.buttons[1][0], text_color="white", command=self.open_file, font=self.icon_font, width=self.wbuttons, height=self.hbuttons)
        self.openfile_button.pack(side="left", padx=5, pady=5)
        self.savefile_button = ctk.CTkButton(self.icon_bar, text=self.buttons[2][0], text_color="white", command=self.save_file, font=self.icon_font, width=self.wbuttons, height=self.hbuttons)
        self.savefile_button.pack(side="left", padx=5, pady=5)
        self.savewith_button = ctk.CTkButton(self.icon_bar, text=self.buttons[3][0], text_color="white", command=self.save_file, font=self.icon_font, width=self.wbuttons, height=self.hbuttons)
        self.savewith_button.pack(side="left", padx=5, pady=5)
        self.run_button = ctk.CTkButton(self.icon_bar, text=self.buttons[4][0], text_color="white", command=self.compile, font=self.icon_font, width=self.wbuttons, height=self.hbuttons)
        self.run_button.pack(side="left", padx=5, pady=5)

        # Ventana de Texto y resultados
        self.windows = tk.PanedWindow(self.root, orient=tk.VERTICAL,bg="#1e1e1e", sashrelief=tk.SUNKEN, sashwidth=5)
        self.windows.pack(fill="both", expand=True)

        self.wintext = tk.PanedWindow(self.windows, orient=tk.HORIZONTAL,bg="#1e1e1e", sashrelief=tk.SUNKEN, sashwidth=5)
        self.wintext.pack(fill="both", expand=True)

        # Crear frame para texto y lineas
        self.text_frame_1 = ctk.CTkFrame(self.wintext)
        self.text_frame_1.pack(expand=True, fill="both")

        # Crear el área de lineas
        self.text_line = ctk.CTkTextbox(self.text_frame_1, width=40, corner_radius=0, bg_color="#2d2d2d", text_color="white",font=("Consolas", 12))
        self.text_line.configure(padx=0, pady=0,takefocus=0,state="disabled", cursor="arrow")
        self.text_line.pack(side="left", fill="y")

        # Crear el área de texto
        self.text_editor = ctk.CTkTextbox(self.text_frame_1, fg_color="#1e1e1e",font=("Consolas", 12), undo=True, wrap="none",padx=6, pady=4)
        self.text_editor.pack(expand=True, fill="both", side="left")

        self.wintext.add(self.text_frame_1)

        # Crear frame de Resultados
        self.winresul = ctk.CTkFrame(self.wintext)
        self.winresul.pack(fill="both",expand=True,side="right")

        self.wintext.add(self.winresul)

        # Crear frame de terminales
        self.winterminal = ctk.CTkFrame(self.windows)
        self.winterminal.pack(fill="both",expand=True)

        self.windows.add(self.wintext)
        self.windows.add(self.winterminal)

Windo = IDE()
Windo.root.mainloop()
