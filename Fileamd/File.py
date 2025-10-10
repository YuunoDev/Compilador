import io 

class Fileamin:
    
    def __init__(self):
        self.file = ""
        self.edit = False
        self.rute = ""

    def setEdit(self, bol):
        self.edit = bol

    def getEdit(self):
        return self.edit

    def setRuta(self, name):
        self.ruta = name

    def getRuta(self):
        return str(self.ruta)
    
    def Dfile(self):
        self.ruta = ""
