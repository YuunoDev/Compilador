import io
import os
import tempfile
import json
import atexit

class Fileamin:
    
    def __init__(self):
        self.file = ""
        self.edit = False
        self.ruta = ""
        self.prevfile = ""
        self.state_file = os.path.join(tempfile.gettempdir(), "ide_state.json")
        self.folder_file = os.path.join(tempfile.gettempdir(), "ide_folder.json")
        self.load_state()  # Cargar estado anterior al iniciar
        self.load_folder()  # Cargar carpeta anterior al iniciar
        # Registrar función para limpiar al cerrar
        atexit.register(self.cleanup)

    def setEdit(self, bol):
        self.edit = bol
        self.save_state()  # Guardar cuando cambie el estado

    def getEdit(self):
        return self.edit

    def setRuta(self, name):
        # Actualizar prevfile con la ruta anterior si existe
        if self.ruta and self.ruta != name:
            self.prevfile = self.ruta
        self.ruta = name
        self.save_state()  # Guardar cuando cambie la ruta

    def getRuta(self):
        return str(self.ruta)
    
    def Dfile(self):
        # Guardar la ruta actual como anterior antes de limpiar
        if self.ruta:
            self.prevfile = self.ruta
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

    def load_folder(self):
        """Carga la carpeta abierta anterior desde el archivo temporal persistente"""
        try:
            if os.path.exists(self.folder_file):
                with open(self.folder_file, 'r') as f:
                    folder_data = json.load(f)
                    folder_path = folder_data.get("folder", "")
                    # Solo cargar si la carpeta aún existe
                    if folder_path and os.path.exists(folder_path):
                        self.opened_folder = folder_path
                        self.ruta = folder_path  # pasar la ruta de la carpeta 
                        return True
        except Exception as e:
            print(f"Error cargando carpeta: {e}")
        return None

    def save_folder(self, folder_path):
        """Guarda la ruta de la carpeta en el archivo temporal persistente"""
        folder_data = {"folder": folder_path}
        try:
            with open(self.folder_file, 'w') as f:
                json.dump(folder_data, f)
        except Exception as e:
            print(f"Error guardando carpeta: {e}")

    def get_previous_file(self):
        """Retorna la ruta del archivo anterior si existe"""
        return self.prevfile if self.prevfile and os.path.exists(self.prevfile) else None
    
    def cleanup(self):
        """Limpia el archivo temporal de ejecución cuando se cierra el programa"""
        try:
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
                print(f"Archivo temporal de ejecución eliminado: {self.state_file}")
        except Exception as e:
            print(f"Error eliminando archivo temporal: {e}")