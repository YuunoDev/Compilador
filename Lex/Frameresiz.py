import tkinter as tk

class ResizableFrame(tk.Frame):
    def __init__(self, master, min_width=100, min_height=100, **kwargs):
        super().__init__(master, **kwargs)

        self.min_width = min_width
        self.min_height = min_height
        self.config(borderwidth=2, relief="solid")

        # Para redimensionar con el mouse desde la esquina inferior derecha
        self.grip = tk.Frame(self, cursor="bottom_right_corner", bg="gray")
        self.grip.place(relx=1.0, rely=1.0, anchor="se", width=10, height=10)

        self.grip.bind("<B1-Motion>", self.resize)

    def resize(self, event):
        # Obtener la posición del mouse relativa a la ventana
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()

        new_width = max(self.min_width, x)
        new_height = max(self.min_height, y)

        self.config(width=new_width, height=new_height)
        self.place_configure(width=new_width, height=new_height)  # si usas .place()

# Ventana principal
root = tk.Tk()
root.geometry("800x600")

# Frame redimensionable
frame = ResizableFrame(root, bg="lightblue")
frame.place(x=50, y=50, width=300, height=200)  # Se necesita usar `.place()` para tamaño dinámico

# Otro frame normal
tk.Label(root, text="Otro contenido aquí").pack(pady=10)

root.mainloop()
