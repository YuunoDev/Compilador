import re
import os

# Tamaño reservado para Tokens
TOKEN_SIZE = 999999

class Automata:
    # Constructor de la clase
    def __init__(self):
        self.state = 0
        self.tokens = []
        self.token = ""
        self.position = 0
        self.line = 1
        self.column = 0
        self.reserved = ["print","if", "else", "while", "end", "do", "switch","case", "int", "float","main", "cin", "cout", "char", "string", "bool", "True", "False", "return", "void", "break", "continue", "for", "foreach", "new", "delete", "this", "class", "public", "private", "protected", "static", "until"]
        self.errors = []
        self.columncomment = 0
        self.linecomment = 0

    #Función para reiniciar el estado y el token
    def stateReset(self):
        self.state = 0
        self.token = ""

    #funcion para obtener tipo de token
    def stareName(self):
        #nombre del estado
        if self.state == 0:
            return "ERROR"
        elif self.state == 1:
            return "NUMERO ENTERO" #numero entero
        elif self.state == 2:
            return self.reservedWords(self.token)
        elif self.state == 3:
            return "OPERADOR"
        elif self.state == 4:
            return "OPERADOR"
        elif self.state == 5:
            return "ASIGNACION"
        elif self.state == 6:
            return "COMPARACION"
        elif self.state == 7:
            return "SIMBOLO"
        elif self.state == 8:
            return "PUNTO"
        elif self.state == 9:
            return "NUMERO REAL" #numero real
        elif self.state == 11:
            return "COMENTARIO"
        elif self.state == 12:
            return "COMENTARIO"
        elif self.state == 13: # comentario multilínea
            return "COMENTARIO"
        elif self.state == 14:
            return "LOGICO"
        elif self.state == 16:
            return "DESCONOCIDO"
        elif self.state == 18:
            return "CADENA"
        elif self.state == 20: # << o >> para entrada/salida
            return "SIMBOLO"
        else:
            return "DEFECTO"

    # funcion para obtener el tipo de palabra reservada
    def reservedWords(self, word):
        #si la palarabra reservada es igual a la palabra reservada retornar la palabra reservada
        if word in self.reserved:
            return "RESERVADA" #Si se requiere directamente la palabra solo cambiar a "WORD"
        else:
            return "IDENTIFICADOR" #si no es una palabra reservada retornar ID

    # funcion para agregar el caracter al token
    def andChar(self,char):
        if len(self.token) < TOKEN_SIZE:
            self.token += char
        else:
            self.errors.append("Error: Token size exceeded.")

    # funcion para agregar el token a la lista de errores
    def error(self, error):
        #agregar el error a la lista de errores
        if error == 1:
            self.errors.append("Error: Token no valido '"+ self.token +"'  linea: " + str(self.line) + " columna: " + str(self.column))

        elif error == 11:
            self.errors.append("Error: Comentario no cerrado")
        elif error == 12:
            self.errors.append("Error: Comentario no cerrado")
        elif error == 14:
            self.errors.append("Error: Operador logico no valido")
        else:
            self.errors.append("Error: Token no valido")

    def calcposcomment(self):
        #calcular la posicion del comentario
        lines = self.line
        line= lines - self.token.count("\n")
        #tomar la primera linea del comentario y ver cual es la columna donde inicia
        lineofcomment = self.token.split("\n")[0]
        #calcular la columna del comentario
        column = len(lineofcomment) - len(lineofcomment.lstrip())

        self.tokens.append((self.token, "COMENTARIO", line, column))
        

    #añadir el token a la lista de tokens y su tipo
    def addTokens(self):
        #self.tokens.append((self.stareName(), self.token))
        if self.state == 13:
            self.calcposcomment()
        if self.state == 12:
            self.tokens.append((self.token, "COMENTARIO", self.linecomment, self.columncomment))
        else:
            self.tokens.append((self.token, self.stareName(), self.line, self.column-len(self.token)))
        #añadir el token a la lista de tokens y su tipo
        self.token = ""
        self.state = 0

    def printToken(self):
        print("Token: ",self.token)
        print("Estado: ",self.state)
        print("Posicion: ",self.position)

    def statetok(self):
        print("Estado: ",self.state)
        print("token: ",self.token)

    def eracer(self):
        #eliminar los tokens
        self.tokens = []
        self.errors = []
        self.line = 1
        self.column = 0
        self.position = 0


    def process(self, input):
        self.stateReset()
        self.eracer()
        i = 0
        while i < len(input):
            char = input[i]
            #print(char, "Estado:", self.state)
            if self.state == 0:
                if char.isdigit():
                    self.state = 1
                    self.andChar(char)
                elif re.match(r"[a-zA-Z]", char):
                    self.state = 2
                    self.andChar(char)
                elif char == "+":
                    self.state = 3
                    self.andChar(char)
                elif char == "-":
                    self.state = 4
                    self.andChar(char)
                elif char in ["<", ">", "=", "!"]:
                    self.state = 5
                    self.andChar(char)
                elif char in ["(", ")", "{", "}", "[", "]", ";", ","]:
                    self.state = 7
                    self.andChar(char)
                elif char == "/":
                    self.state = 10
                    self.linecomment = self.line
                    self.columncomment = self.column
                    self.andChar(char)
                elif char in ["&", "|"]:
                    self.state = 14
                    self.andChar(char)
                elif char in ["*", "%", "^"]:
                    self.state = 15
                    self.andChar(char)
                elif char == "\"":
                    self.state = 18
                    self.andChar(char)
                else:
                    if char not in [" ", "\n", "\0"]:
                        self.andChar(char)
                        self.error(1)
                        self.state = 16
                        

            elif self.state == 1:  # número entero
                if char.isdigit():
                    self.andChar(char)
                elif char == ".":
                    self.state = 8
                    self.andChar(char)
                else:
                    self.addTokens()               
                    continue  # << Volver a procesar el mismo caracter

            elif self.state == 2:  # identificador
                if re.match(r"[a-zA-Z]", char) or char.isdigit():
                    self.andChar(char)
                else:
                    self.addTokens()
                    continue

            elif self.state == 3:  # signo positivo
                #si el anterior token es en tokens es un numero pasar solo el signo
                if char == "+":
                    if self.token == "+":
                        self.state = 17
                        self.andChar(char)
                elif self.tokens[len(self.tokens)-1][1] in ["NUMERO ENTERO", "NUMERO REAL", "IDENTIFICADOR"]:
                    self.state = 3
                    self.addTokens()
                    continue
                elif char.isdigit():
                    self.state = 1
                    self.andChar(char)
                else:
                    self.addTokens()
                    continue


            elif self.state == 4:  # signo negativo
                if char == "-":
                    if self.token == "-":
                        self.state = 17
                        self.andChar(char)
                elif self.tokens[len(self.tokens)-1][1] in ["NUMERO ENTERO", "NUMERO REAL", "IDENTIFICADOR"]:
                    self.state = 3
                    self.addTokens()
                    continue
                elif char == "-":
                    if self.token == "-":
                        self.state = 4
                        self.andChar(char)
                    else:
                        self.error(1)
                elif char.isdigit():
                    self.state = 1
                    self.andChar(char)
                else:
                    self.addTokens()
                    continue

            elif self.state == 5:
                # operadores de comparacion
                if self.token == "=":
                    if char == "=":
                        self.andChar(char)
                        self.state = 6
                    else:
                        self.addTokens()
                        continue
                elif self.token == "<":
                    if char == "<":
                        self.andChar(char)
                        self.state = 20
                    elif char == "=":
                        self.andChar(char)
                        self.state = 6
                    else:
                        self.state = 6
                        self.addTokens()
                        continue
                elif self.token == ">":
                    if char == ">":
                        self.andChar(char)
                        self.state = 20
                    elif char == "=":
                        self.andChar(char)
                        self.state = 6
                    else:
                        self.state = 6
                        self.addTokens()
                        continue
                elif self.token == "!":
                    if char == "=":
                        self.andChar(char)
                        self.state = 6
                    else:
                        self.addTokens()
                        continue
                else:
                    self.state = 6
                    self.addTokens()
                    continue  # << Volver a procesar el mismo caracter
            
            elif self.state == 6:
                self.addTokens()
                continue

            elif self.state == 7:
                # símbolos individuales, ya procesado
                self.addTokens()
                continue

            elif self.state == 8:
                if char.isdigit():
                    self.state = 9
                    self.andChar(char)
                else:
                    self.error(1)
                    self.state = 16
                    continue

            elif self.state == 9:
                if char.isdigit():
                    self.andChar(char)
                elif char in [" ", "\n", "\0"] or not char.isdigit():
                    self.addTokens()
                    self.state = 0
                    continue

            # Comentarios
            elif self.state == 10:
                if char == "*":
                    self.state = 11     # Comentario varias lineas
                    self.andChar(char)
                elif char == "/":
                    self.state = 12    # Comentario de una sola linea
                    self.andChar(char)
                else:
                    self.state = 3
                    self.addTokens()
                    continue  # << Volver a procesar el mismo caracter

            # Comentario varias lineas
            elif self.state == 11:
                if char == "*":
                    self.state = 13
                    self.andChar(char)
                else:
                    self.andChar(char)
                

            elif self.state == 12:
                #cualquier caracter que no sea salto de linea
                if char == "\n":
                    self.state = 121
                    self.andChar(" ")
                else:
                    self.andChar(char)
                    
            elif self.state == 121:
                self.state = 12
                self.addTokens()
                continue  # << Volver a procesar el mismo caracter

            # Comentario varias lineas
            elif self.state == 13:
                if char == "/":
                    self.state = 131
                    self.andChar(char)
                else:
                    self.andChar(char)

            elif self.state == 131:
                self.state = 13
                self.addTokens()
                continue
                

            elif self.state == 14:
                if char == "&":
                    if self.token == "&":
                        self.andChar(char)
                elif char == "|":
                    if self.token == "|":
                        self.andChar(char)
                elif self.token == "&&" or self.token == "||":
                    self.addTokens()
                    continue
                else:
                    self.state = 0
                    self.addTokens()
                    continue

            elif self.state == 15:
                self.state = 3
                self.addTokens()
                continue

            elif self.state == 16:
                self.addTokens()
                continue

            elif self.state == 17:
                self.state = 3
                self.addTokens()
                continue

            elif self.state == 18: #cadenas
                if char == "\"":
                    self.state = 19
                    self.andChar(char)
                elif char in [" ","\n"]:
                    self.andChar(char)
                elif re.match(r"[a-zA-Z]", char) or char.isdigit():
                    self.andChar(char)
                
            elif self.state == 19:
                self.state = 18
                self.addTokens()
                continue

            elif self.state == 20:
                self.addTokens()
                continue

            else:
                self.stateReset()

            i += 1
            self.position += 1
            if char == "\n":
                self.line += 1
                self.column = 0
            else:   
                self.column += 1

        if self.state not in [0, 13]:
            self.addTokens()
        return False
    
    def genarcherrores(self,arch):
        # Luego lo creamos desde cero y escribimos los tokens
        with open(arch, "w", encoding="utf-8") as file:
            for error in self.errors:
                file.write(error + "\n")

    def deleteCommentandError(self):
        # Eliminar los tokens que sean comentarios o errores
        for i in range(len(self.tokens) - 1, -1, -1):
            if self.tokens[i][1] in ["COMENTARIO", "ERROR", "DESCONOCIDO"]:
                # Eliminar el token
                del self.tokens[i]

    def genarch(self,arch):
        # Luego lo creamos desde cero y escribimos los tokens
        with open(arch, "w", encoding="utf-8") as file:
            for token in self.tokens:                         #linea            Columna
                #file.write(f"lexema: {token[0]} tipo: {token[1]} linea: {token[2]} columna: {token[3]}\n")
                #print(f"{t.tipo:<20} {t.lexema:<18} (línea {t.linea}, columna {t.columna})")
                file.write(f"{token[1]:<20} {token[0]:<18} (línea {token[2]}, columna {token[3]})\n")

    def mostrarTokens(self):
        # Mostrar los tokens
        for token in self.tokens:
            print(f"{token[1]:<20} {token[0]:<18} (línea {token[2]}, columna {token[3]})")

# DFA = Automata()

# #lectura de archivo
# with open("provS.txt", "r", encoding="utf-8", errors="ignore") as file:
#    code = file.read()

# DFA.process(code)

# DFA.mostrarTokens()
