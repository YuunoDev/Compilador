import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Paneles Redimensionables")
root.geometry("800x600")

# PanedWindow principal (vertical) - divide arriba y abajo
main_paned = ttk.PanedWindow(root, orient=tk.VERTICAL)
main_paned.pack(fill=tk.BOTH, expand=True)

# PanedWindow superior (horizontal) - divide los 2 paneles de arriba
top_paned = ttk.PanedWindow(main_paned, orient=tk.HORIZONTAL)
main_paned.add(top_paned, weight=1)

# Frame 1 (arriba izquierda)
frame1 = ttk.Frame(top_paned, relief=tk.RAISED, borderwidth=2)
label1 = ttk.Label(frame1, text="Panel 1\n(Arriba Izquierda)", 
                   font=("Arial", 12), background="lightblue")
label1.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
top_paned.add(frame1, weight=1)

# Frame 2 (arriba derecha)
frame2 = ttk.Frame(top_paned, relief=tk.RAISED, borderwidth=2)
label2 = ttk.Label(frame2, text="Panel 2\n(Arriba Derecha)", 
                   font=("Arial", 12), background="lightgreen")
label2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
top_paned.add(frame2, weight=1)

# Frame 3 (abajo - más grande)
frame3 = ttk.Frame(main_paned, relief=tk.RAISED, borderwidth=2)
label3 = ttk.Label(frame3, text="Panel 3\n(Abajo - Panel Grande)", 
                   font=("Arial", 14), background="lightyellow")
label3.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
main_paned.add(frame3, weight=2)  # weight=2 lo hace más grande

root.mainloop()