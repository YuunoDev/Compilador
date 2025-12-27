import tkinter as tk
from tkinter import ttk

class TablaSimbolos:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabla de Símbolos")
        self.root.geometry("800x400")
        
        # Colores del tema oscuro
        self.bg_dark = "#1e1e1e"
        self.bg_secondary = "#252526"
        self.bg_hover = "#2d2d30"
        self.fg_primary = "#FFF3F3"
        self.fg_secondary = "#000000"
        self.accent = "#007acc"
        self.border = "#3e3e42"
        
        # Configurar el fondo de la ventana
        self.root.configure(bg=self.bg_dark)
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10", style="Dark.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="=== TABLA DE SÍMBOLOS ===", 
                                font=("Consolas", 12, "bold"),
                                style="Title.TLabel")
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # Subtítulo
        scope_label = ttk.Label(main_frame, text="Ámbito: global", 
                               font=("Consolas", 10),
                               style="Subtitle.TLabel")
        scope_label.grid(row=1, column=0, pady=(0, 10))
        
        # Frame para el Treeview y scrollbar
        tree_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, style="Dark.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("nombre", "tipo", "valor", "usada", "linea")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=scrollbar.set, height=10,
                                 style="")
        
        # Configurar scrollbar
        scrollbar.config(command=self.tree.yview)
        
        # Definir encabezados
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("usada", text="Usada")
        self.tree.heading("linea", text="Línea")
        
        # Definir ancho de columnas
        self.tree.column("nombre", width=120, anchor=tk.W)
        self.tree.column("tipo", width=100, anchor=tk.CENTER)
        self.tree.column("valor", width=100, anchor=tk.CENTER)
        self.tree.column("usada", width=80, anchor=tk.CENTER)
        self.tree.column("linea", width=200, anchor=tk.W)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Estilo para filas alternadas
        self.tree.tag_configure('oddrow', background=self.bg_secondary, 
                               foreground=self.fg_primary)
        self.tree.tag_configure('evenrow', background=self.bg_dark, 
                               foreground=self.fg_primary)
        
        # Datos de ejemplo
        self.cargar_datos()
        
        # Configurar grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def configurar_estilo(self):
        """Configura el tema oscuro para todos los widgets"""
        style = ttk.Style()

        # Forzamos un tema base que sí permite personalización completa
        style.theme_use("clam")

        # === FRAME Y LABELS ===
        style.configure("Dark.TFrame", background=self.bg_dark)

        style.configure("Title.TLabel",
                    background=self.bg_dark,
                    foreground=self.accent,
                    font=("Consolas", 12, "bold"))

        style.configure("Subtitle.TLabel",
                    background=self.bg_dark,
                    foreground=self.fg_secondary,
                    font=("Consolas", 10))

        # === TREEVIEW ===
        style.configure("Dark.Treeview",
                    background=self.bg_dark,
                    foreground=self.fg_primary,
                    fieldbackground=self.bg_dark,  # Fondo interno
                    bordercolor=self.border,
                    borderwidth=0,
                    font=("Consolas", 10))

        style.map("Dark.Treeview",
                background=[("selected", self.accent)],
                foreground=[("selected", "white")])

        # === ENCABEZADOS DEL TREEVIEW ===
        style.configure("Dark.Treeview.Heading",
                    background=self.bg_secondary,
                    foreground=self.fg_primary,
                    font=("Consolas", 10, "bold"),
                    borderwidth=1,
                    relief="flat")

        style.map("Dark.Treeview.Heading",
                background=[("active", self.bg_hover)],
                foreground=[("active", "white")])

        # === SCROLLBAR OSCURA ===
        style.configure("Dark.Vertical.TScrollbar",
                    background=self.bg_secondary,
                    troughcolor=self.bg_dark,
                    bordercolor=self.border,
                    arrowcolor=self.fg_primary)

    
    def cargar_datos(self):
        """Carga los datos en el Treeview"""
        datos = [
            ("z", "int", "0", "Sí", "[2]"),
            ("a", "float", "2.0", "Sí", "[3, 9, 23, 27]"),
            ("b", "float", "5.0", "Sí", "[3, 17, 19]"),
            ("c", "float", "0.0", "Sí", "[3, 4, 29]"),
            ("g", "bool", "false", "Sí", "[5]"),
            ("n", "int", "1", "Sí", "[6]")
        ]
        
        for i, row in enumerate(datos):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=row, tags=(tag,))
    
    def agregar_simbolo(self, nombre, tipo, valor, usada, linea):
        """Método para agregar nuevos símbolos"""
        idx = len(self.tree.get_children())
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        self.tree.insert("", tk.END, values=(nombre, tipo, valor, usada, linea), 
                        tags=(tag,))
    
    def limpiar_tabla(self):
        """Limpia todos los elementos de la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)

# Crear ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = TablaSimbolos(root)
    root.mainloop()