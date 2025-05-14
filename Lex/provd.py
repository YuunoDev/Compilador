import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x300")

sidebar = ctk.CTkFrame(app, width=60, corner_radius=0)
sidebar.pack(side="left", fill="y")

# Cargar imagen con tkinter.PhotoImage
home_icon = tk.PhotoImage(file="icons/nuevo.png")
home_img = ctk.CTkImage(light_image=home_icon, dark_image=home_icon)

btn_home = ctk.CTkButton(sidebar, image=home_img, text="", width=50, command=lambda: print("Home"))
btn_home.pack(pady=10)

app.mainloop()
