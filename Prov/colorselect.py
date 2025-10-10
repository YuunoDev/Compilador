import tkinter as tk
from tkinter import colorchooser

# Lista de colores con IDs
colores = {
    'Primario': '#f92672',
    'Secundario': '#66d9ef',
    'Terciario': '#a6e22e',
}

def cambiar_color(id_label, color_label):
    # Abre el selector de color
    color = colorchooser.askcolor(title=f"Selecciona un color para {id_label}")
    if color[1]:  # color[1] contiene el valor hexadecimal del color
        color_label.config(bg=color[1])  # Cambia el color de la muestra
        colores[id_label] = color[1]  # Actualiza el color en el diccionario

# Crear la ventana
root = tk.Tk()
root.title("Lista de Colores")

# Crear una fila para cada color
for id_label, color_hex in colores.items():
    frame = tk.Frame(root)
    frame.pack(pady=5, padx=10, anchor="w")
    
    # Texto con el ID
    label_texto = tk.Label(frame, text=id_label, width=15, anchor="w")
    label_texto.pack(side="left")
    
    # Muestra del color
    color_label = tk.Label(frame, bg=color_hex, width=10, height=1)
    color_label.pack(side="left", padx=10)
    
    # Botón para cambiar el color
    boton_cambiar = tk.Button(frame, text="Cambiar", 
                               command=lambda id_label=id_label, color_label=color_label: cambiar_color(id_label, color_label))
    boton_cambiar.pack(side="left")

root.mainloop()
