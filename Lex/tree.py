import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Treeview Jerárquico con columnas")

tree = ttk.Treeview(root, columns=("detalle",))
tree.heading("#0", text="Categoría")
tree.heading("detalle", text="Descripción")

p1 = tree.insert("", "end", text="Frutas", values=("Rojas y tropicales"))
tree.insert(p1, "end", text="Manzana", values=("Rica en fibra"))
tree.insert(p1, "end", text="Plátano", values=("Fuente de potasio"))

p2 = tree.insert("", "end", text="Verduras", values=("Verdes y nutritivas"))
tree.insert(p2, "end", text="Espinaca", values=("Rica en hierro"))
tree.insert(p2, "end", text="Zanahoria", values=("Buena para la vista"))

tree.pack(expand=True, fill='both')
root.mainloop()
