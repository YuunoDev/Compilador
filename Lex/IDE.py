import customtkinter as ctk
from Anlex import *
from customtkinter import *
from tkinter import filedialog
import tkinter as tk


class IDE:
    def __init__(self):
        # Partes de la vista del IDE
        self.window = None
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

        
        # text areas
        self.text_frame_1 = None
        self.text_line = None
        self.text_editor = None


        # varliables y clase usada para funcionalidades del IDE
        self.ruta = ""
        self.edit = False
        self.Automat = Automata()

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
        self.window = ctk.CTk()
        self.window.geometry("800x600")
        self.window.title("IDE")

        
        # Crear barra de menú con tkinter.Menu
        self.menu_bar = tk.Menu(self.window, bg="#2e2e2e", fg="white", activebackground="#444", activeforeground="white")
        self.window.config(menu=self.menu_bar)

        # Menú de Archivo
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#2e2e2e", fg="white", activebackground="#444", activeforeground="white")
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.window.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Menú de Ejecución
        self.run_menu = tk.Menu(self.menu_bar, tearoff=0, bg="#2e2e2e", fg="white", activebackground="#444", activeforeground="white")
        self.run_menu.add_command(label="Ejecutar", command=self.compile)
        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)
        self.window.config(menu=self.menu_bar)

        #iconbar
        # Crear la barra de iconos pegada arriba
        self.icon_bar = ctk.CTkFrame(
            self.window,
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

        # Crear frame para texto y lineas
        self.text_frame_1 = ctk.CTkFrame(self.window)
        self.text_frame_1.pack(expand=True, fill="both")

        # Crear el área de lineas
        self.text_line = ctk.CTkTextbox(self.text_frame_1, width=40, corner_radius=0, bg_color="#2d2d2d", text_color="white",font=("Consolas", 12))
        self.text_line.configure(padx=0, pady=0,takefocus=0,state="disabled", cursor="arrow")
        self.text_line.pack(side="left", fill="y")

        # Crear el área de texto
        self.text_editor = ctk.CTkTextbox(self.text_frame_1, fg_color="#1e1e1e",font=("Consolas", 12), undo=True, wrap="none",padx=6, pady=4)
        self.text_editor.pack(expand=True, fill="both", side="left")

Windo = IDE()
Windo.window.mainloop()
# This code creates a simple IDE with a text area and a menu bar. The menu bar includes options to create a new file, open an existing file, save the current file, and exit the application. The text area is where the user can write code. The IDE is initialized and run at the end of the script.