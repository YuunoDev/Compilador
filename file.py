import tkinter as tk
from tkinter import ttk
import os

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorador de Archivos")
        
        # Crear frame principal
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Crear listbox para mostrar archivos
        self.file_listbox = tk.Listbox(self.main_frame, width=50, height=20)
        self.file_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Añadir scrollbar
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=self.scrollbar.set)
        
        # Campo de entrada para la ruta
        self.path_var = tk.StringVar(value=os.getcwd())
        self.path_entry = ttk.Entry(self.main_frame, textvariable=self.path_var, width=50)
        self.path_entry.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Botón para actualizar
        self.update_button = ttk.Button(self.main_frame, text="Actualizar", command=self.update_files)
        self.update_button.grid(row=0, column=1, pady=5)
        
        # Mostrar archivos iniciales
        self.update_files()
    
    def update_files(self):
        try:
            # Limpiar listbox
            self.file_listbox.delete(0, tk.END)
            
            # Obtener y mostrar archivos
            path = self.path_var.get()
            files = os.listdir(path)
            
            for file in sorted(files):
                full_path = os.path.join(path, file)
                if os.path.isdir(full_path):
                    self.file_listbox.insert(tk.END, f"📁 {file}")
                else:
                    self.file_listbox.insert(tk.END, f"📄 {file}")
                    
        except Exception as e:
            self.file_listbox.insert(tk.END, f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()