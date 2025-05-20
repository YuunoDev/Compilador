import tkinter as tk

root = tk.Tk()
root.geometry("800x600")
root.configure(bg="#1e1e1e")  # Fondo oscuro

# Usa PanedWindow de tk
paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#1e1e1e", sashrelief=tk.SUNKEN, sashwidth=5)
paned.pack(fill="both", expand=True)

left_frame = tk.Frame(paned, bg="lightblue", width=200)
right_frame = tk.Frame(paned, bg="lightgreen")

paned.add(left_frame)
paned.add(right_frame)

root.mainloop()
