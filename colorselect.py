from tkinter import *
from tkinter import ttk

class ColorTextEditor:
    def __init__(self):
        self.window = Tk()
        self.window.title("IDE Color Configuration")
        self.window.configure(bg="#1e1e1e")
        self.setup_ui()

    def setup_ui(self):
        # Create main container with proper spacing
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        
        # Configure grid weights for responsive layout
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        
        # Sample text area with modern styling
        self.setup_sample_text()
        
        # Color selection panel
        self.setup_color_panel()
        
        # Add status bar
        self.setup_status_bar()

    def setup_sample_text(self):
        sample_frame = ttk.LabelFrame(self.main_frame, text="Sample Code", padding="5")
        sample_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(N, W, E, S))
        
        self.text_area = Text(
            sample_frame,
            height=12,
            width=50,
            bg="#1e1e1e",
            fg="white",
            font=("Consolas", 12),
            padx=10,
            pady=10
        )
        self.text_area.grid(row=0, column=0, sticky=(N, W, E, S))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(sample_frame, orient="vertical", command=self.text_area.yview)
        scrollbar.grid(row=0, column=1, sticky=(N, S))
        self.text_area["yscrollcommand"] = scrollbar.set
        
        self.insert_sample_code()

    def insert_sample_code(self):
        sample_code = '''def example_function():
    """
    This is a sample function to demonstrate
    syntax highlighting and color schemes.
    """
    message = "Hello, World!"
    print(message)
    
    # This is a comment
    for i in range(5):
        print(f"Count: {i}")'''
        
        self.text_area.insert("1.0", sample_code)

    def setup_color_panel(self):
        color_frame = ttk.LabelFrame(self.main_frame, text="Color Settings", padding="5")
        color_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(N, W, E, S))
        
        # Example color options
        colors = {
            "Text": "#FFFFFF",
            "Keywords": "#569CD6",
            "Strings": "#CE9178",
            "Comments": "#6A9955",
            "Background": "#1E1E1E"
        }
        
        for idx, (name, color) in enumerate(colors.items()):
            self.create_color_row(color_frame, name, color, idx)

    def create_color_row(self, parent, name, color, row):
        ttk.Label(parent, text=name).grid(row=row, column=0, padx=5, pady=2, sticky=W)
        
        color_preview = ttk.Label(parent, background=color, width=8)
        color_preview.grid(row=row, column=1, padx=5, pady=2)
        
        ttk.Button(
            parent,
            text="Change",
            command=lambda: self.change_color(name, color_preview)
        ).grid(row=row, column=2, padx=5, pady=2)

    def setup_status_bar(self):
        status_bar = ttk.Label(
            self.window,
            text="Ready",
            relief=SUNKEN,
            padding=(5, 2)
        )
        status_bar.grid(row=1, column=0, sticky=(W, E))

    def change_color(self, element_name, preview_label):
        # This would be implemented to show a color picker
        pass

    def run(self):
        # Center the window on screen
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
        
        # Start the application
        self.window.mainloop()

if __name__ == "__main__":
    app = ColorTextEditor()
    app.run()