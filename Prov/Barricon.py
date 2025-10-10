from tkinter import *
from tkinter import ttk

def guardar():
    print("Guardando...")  # Aquí irá tu función para guardar

ventana = Tk()
ventana.geometry("400x300")

# Crear barra de menú
barra_menu = Menu(ventana)
ventana.config(menu=barra_menu)

# Crear barra de herramientas
barra_herramientas = ttk.Frame(ventana)
barra_herramientas.pack(side="top", fill="x")

# Crear botón de guardar
boton_guardar = ttk.Button(barra_herramientas, text="💾", command=guardar,)
# Alternativa: boton_guardar = ttk.Button(barra_herramientas, text="Guardar", command=guardar)
boton_guardar.pack(side="left", padx=1, pady=1)

ventana.mainloop()