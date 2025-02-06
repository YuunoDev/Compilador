import tkinter as tk
from tkinter import ttk

# Crear la ventana principal
root = tk.Tk()
root.title("Ejemplo de pestañas en Tkinter")

# Crear un Notebook (contenedor de pestañas)
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill='both', expand=True)

# Crear frames para cada pestaña
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)

# Agregar los frames al Notebook
notebook.add(tab1, text="Pestaña 1")
notebook.add(tab2, text="Pestaña 2")
notebook.add(tab3, text="Pestaña 3")

# Contenido para las pestañas
ttk.Label(tab1, text="Contenido de la Pestaña 1").pack(pady=20)
ttk.Label(tab2, text="Contenido de la Pestaña 2").pack(pady=20)
ttk.Label(tab3, text="Contenido de la Pestaña 3").pack(pady=20)

# Ejecutar la aplicación
root.mainloop()
