import io
import os
import tempfile
import json

class Fileamin:
    
    def __init__(self):
        self.file = ""
        self.edit = False
        self.ruta = ""
        self.prevfile = ""
        self.state_file = os.path.join(tempfile.gettempdir(), "ide_state.json")
        self.load_state()  # Cargar estado anterior al iniciar

    def setEdit(self, bol):
        self.edit = bol
        self.save_state()  # Guardar cuando cambie el estado

    def getEdit(self):
        return self.edit

    def setRuta(self, name):
        self.ruta = name
        self.save_state()  # Guardar cuando cambie la ruta

    def getRuta(self):
        return str(self.ruta)
    
    def Dfile(self):
        self.ruta = ""
        self.save_state()

    def save_state(self):
        """Guarda el estado actual en un archivo temporal"""
        state = {
            "ruta": self.ruta,
            "edit": self.edit,
            "prevfile": self.prevfile
        }
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error guardando estado: {e}")

    def load_state(self):
        """Carga el estado anterior desde el archivo temporal"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.ruta = state.get("ruta", "")
                    self.edit = state.get("edit", False)
                    self.prevfile = state.get("prevfile", "")
                    return True
        except Exception as e:
            print(f"Error cargando estado: {e}")
        return False

    def get_previous_file(self):
        """Retorna la ruta del archivo anterior si existe"""
        return self.prevfile if self.prevfile and os.path.exists(self.prevfile) else None