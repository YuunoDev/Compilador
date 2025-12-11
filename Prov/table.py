import tkinter as tk
from tkinter import ttk

def crear_tabla():
    ventana = tk.Tk()
    ventana.title("Tabla en Tkinter")
    ventana.geometry("600x400")
    
    # Crear Treeview (tabla)
    tabla = ttk.Treeview(ventana, columns=("col1", "col2", "col3"))
    
    # Definir encabezados
    tabla.heading("#0", text="ID")
    tabla.heading("col1", text="Nombre")
    tabla.heading("col2", text="Edad")
    tabla.heading("col3", text="Ciudad")
    
    # Configurar ancho de columnas
    tabla.column("#0", width=50)
    tabla.column("col1", width=150)
    tabla.column("col2", width=100)
    tabla.column("col3", width=150)
    
    # Insertar datos de ejemplo
    datos = [
        ("1", "Ana", "25", "Madrid"),
        ("2", "Carlos", "30", "Barcelona"),
        ("3", "María", "22", "Valencia"),
        ("4", "Juan", "35", "Sevilla"),
        ("5", "Laura", "28", "Bilbao")
    ]
    
    for dato in datos:
        tabla.insert("", tk.END, text=dato[0], values=(dato[1], dato[2], dato[3]))
    
    # Agregar scrollbar
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar.set)
    
    # Ubicar elementos en la ventana
    tabla.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    ventana.mainloop()

crear_tabla()