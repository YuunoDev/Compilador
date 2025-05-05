from tkinter import *
from tkinter import filedialog as FileDialog
from tkinter import ttk
import threading
import re
from Comp import *
from Comp_Lex import *

class ModernIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern PyC IDE")
        #cambiar color solo de la barra de titulo
        

        self.ruta = ""
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure('Custom.TNotebook', background='#1e1e1e')
        self.style.configure('Custom.TNotebook.Tab', padding=[12, 4], background='#2d2d2d', foreground='#d4d4d4')
        self.style.configure('Custom.Menubar', background=[('selected', '#3c3c3c')], foreground=[('selected', '#ffffff')])
        self.style.map('Custom.TNotebook.Tab',
                      background=[('selected', '#3c3c3c')],
                      foreground=[('selected', '#ffffff')])
        
        # Configure root window
        self.root.configure(bg='#1e1e1e')
        self.setup_menu()
        self.setup_main_area()
        self.setup_terminals()
        self.setup_status_bar()
        self.bind_shortcuts()
        
        # Initialize line numbers
        #self.actualizar_numeros_linea()
        
    def setup_menu(self):
        self.menubar = Menu(self.root, bg='#2d2d2d', fg='#d4d4d4', activebackground='#3c3c3c', relief=FLAT)
        
        # # File menu
        self.file_menu = Menu(self.menubar, tearoff=0, bg='#2d2d2d', fg='#d4d4d4',
                              activebackground='#3c3c3c', activeforeground='white')
        self.file_menu.add_command(label="New File    Ctrl+N")
        # self.file_menu.add_command(label="Open        Ctrl+O", command=self.abrir)
        # self.file_menu.add_command(label="Save        Ctrl+S", command=self.guardar)
        # self.file_menu.add_command(label="Save As     Ctrl+Shift+S", command=self.guardar_como)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit        Ctrl+Q", command=self.root.quit)
        
        # Run menu
        self.run_menu = Menu(self.menubar, tearoff=0, bg='#2d2d2d', fg='#d4d4d4',
                            activebackground='#3c3c3c', activeforeground='white')
        #self.run_menu.add_command(label="Run Script   F5", command=self.ejecutar_codigo)
        
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Run", menu=self.run_menu)
        
        self.root.config(menu=self.menubar)
        
    def setup_main_area(self):
        # Main container
        self.main_frame = Frame(self.root, bg='#1e1e1e')
        self.main_frame.pack(fill=BOTH, expand=True, padx=2, pady=2)
        
        # Editor frame with line numbers
        self.editor_frame = Frame(self.main_frame, bg='#1e1e1e')
        self.editor_frame.pack(fill=BOTH, expand=True)
        
        # Line numbers
        self.lineas = Text(self.editor_frame, width=4, padx=4, takefocus=0, border=0,
                          bg='#2d2d2d', fg='#6e7681', font=('Consolas', 12),
                          state='disabled')
        self.lineas.pack(side=LEFT, fill=Y)
        
        # Main text editor
        self.texto = Text(self.editor_frame, bd=0, padx=6, pady=4,
                         bg='#1e1e1e', fg='#d4d4d4', insertbackground='#d4d4d4',
                         font=('Consolas', 12), undo=True)
        self.texto.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.editor_frame, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        # Configure scrolling
        self.scrollbar.config(command=self.multiple_yview)
        self.texto.config(yscrollcommand=self.sync_scroll)
        self.lineas.config(yscrollcommand=self.scrollbar.set)
        
    def setup_terminals(self):
        # Terminal notebook
        self.notebook = ttk.Notebook(self.main_frame, style='Custom.TNotebook')
        self.notebook.pack(fill=BOTH, expand=False, pady=(2, 0))
        
        # Lexical terminal
        self.frame_terminalex = Frame(self.notebook, bg='#1e1e1e')
        self.terminalex = Text(self.frame_terminalex, height=8,
                              bg='#1e1e1e', fg='#d4d4d4',
                              font=('Consolas', 11))
        self.terminalex.pack(fill=BOTH, expand=True)
        
        # Syntactic terminal
        self.frame_terminal = Frame(self.notebook, bg='#1e1e1e')
        self.terminalsy = Text(self.frame_terminal, height=8,
                              bg='#1e1e1e', fg='#d4d4d4',
                              font=('Consolas', 11))
        self.terminalsy.pack(fill=BOTH, expand=True)
        
        self.notebook.add(self.frame_terminalex, text='Lexical Output')
        self.notebook.add(self.frame_terminal, text='Syntactic Output')
        
    def setup_status_bar(self):
        # Status bar
        self.status_frame = Frame(self.root, bg='#2d2d2d', height=25)
        self.status_frame.pack(fill=X, side=BOTTOM)
        
        # Left status message
        self.mensaje = StringVar(value="Ready")
        self.status_left = Label(self.status_frame, textvariable=self.mensaje,
                               bg='#2d2d2d', fg='#d4d4d4', padx=5, pady=2)
        self.status_left.pack(side=LEFT)
        
        # Right status message (cursor position)
        self.mensaje2 = StringVar(value="Ln 1, Col 0")
        self.status_right = Label(self.status_frame, textvariable=self.mensaje2,
                                bg='#2d2d2d', fg='#d4d4d4', padx=5, pady=2)
        self.status_right.pack(side=RIGHT)
        
    def bind_shortcuts(self):
        pass
        #self.texto.bind('<<Modified>>', self.on_text_change)
        #self.texto.bind('<KeyRelease>', self.show_cursor_position)
        
        # self.root.bind('<Control-n>', lambda e: self.nuevo())
        # self.root.bind('<Control-o>', lambda e: self.abrir())
        # self.root.bind('<Control-s>', lambda e: self.guardar())
        # self.root.bind('<Control-S>', lambda e: self.guardar_como())
        # self.root.bind('<Control-q>', lambda e: self.root.quit())
        # self.root.bind('<F5>', lambda e: self.ejecutar_codigo())

    # [Existing methods like nuevo(), abrir(), guardar(), etc. remain the same]
    
    # def show_cursor_position(self, event):
    #     cursor_pos = self.texto.index(INSERT)
    #     line, col = cursor_pos.split('.')
    #     self.mensaje2.set(f"Ln {line}, Col {col}")
    #     self.colorTexto(None)
        
    



root = Tk()
app = ModernIDE(root)
root.mainloop()