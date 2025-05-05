import re

# Tamaño reservado para Tokens
TOKEN_SIZE = 264


class Automata:
    # Constructor de la clase
    def __init__(self):
        self.state = 0
        self.tokens = []
        self.token = ""
        self.char = ""
        self.errors = []
        self.position = 0
        self.input_text = ""
        self.statefinal = 0

    #Función para reiniciar el estado y el token
    def stateReset(self):
        self.state = 0
        self.token = ""

    #Función de errores de estado
    def error(self, error):
        #error de estado
        if error == 1:
            self.errors.append("Error: Invalid character in state 1.")
        elif error == 2:
            self.errors.append("Error: Invalid character in state 2.")
        elif error == 3:
            self.errors.append("Error: Invalid character in state 3.")
        elif error == 4:
            self.errors.append("Error: Invalid character in state 4.")
        elif error == 5:
            self.errors.append("Error: Invalid character in state 5.")
        elif error == 6:
            self.errors.append("Error: Invalid character in state 6.")
        elif error == 7:
            self.errors.append("Error: Invalid character in state 7.")
        elif error == 8:
            self.errors.append("Error: Invalid character in state 8.")
        elif error == 9:
            self.errors.append("Error: Invalid character in state 9.")
        elif error == 10:
            self.errors.append("Error: Invalid character in state 10.")
        elif error == 11:
            self.errors.append("Error: Invalid character in state 11.")
        elif error == 12:
            self.errors.append("Error: Invalid character in state 12.")

    #funcion para obtener tipo de token
    def stareName(self):
        #nombre del estado
        if self.state == 0:
            return "OTRO"
        elif self.state == 1:
            return "NUMERO" #numero entero
        elif self.state == 2:
            return self.reservedWords(self.token)
        elif self.state == 3:
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
            return "NUMERO" #numero real
        elif self.state == 11:
            return "COMENTARIO"
        elif self.state == 12:
            return "COMENTARIO"
        elif self.state == 13:
            return "COMENTARIO"
        elif self.state == 14:
            return "LOGICO"
        else: 
            return "ERROR"
        
    # funcion para obtener el tipo de palabra reservada
    def reservedWords(self, word):
        #palabras reservadas
        reserved = ["if", "else", "while", "end", "do", "switch","case", "int", "float","main", "cin", "char", "string", "bool", "True", "False", "return", "void", "break", "continue", "for", "foreach", "in", "new", "delete", "this", "class", "public", "private", "protected", "static"]
        #si la palarabra reservada es igual a la palabra reservada retornar la palabra reservada
        if word in reserved:
            return "RESERVADA" #Si se requiere directamente la palabra solo cambiar a "WORD"
        else:
            return "IDENTIFICADOR" #si no es una palabra reservada retornar ID
        

    def andChar(self,char):
        if len(self.token) < TOKEN_SIZE:
            self.token += char
        else:
            self.errors.append("Error: Token size exceeded.")

    def addTokens(self):
        #añadir el token a la lista de tokens y su tipo
        #self.tokens.append((self.stareName(), self.token))
        self.tokens.append((self.token, self.stareName()))
        #añadir el token a la lista de tokens y su tipo
        self.token = ""
        self.state = 0


    def printToken(self):
        print("Token: ",self.token)
        print("Estado: ",self.state)
        print("Caracter: ",self.char)
        print("Posicion: ",self.position)
        print("Texto de entrada: ",self.input_text)
        print("Estado final: ",self.statefinal)

    def statetok(self, char):
        print("Estado: ",self.state)
        print("token: ",self.token)
        print("Caracter: ",char)


    def process(self, input):
        self.stateReset()
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
                    self.addTokens()
                elif char == "/":
                    self.state = 10
                    self.andChar(char)
                elif char in ["&", "|"]:
                    self.state = 14
                    self.andChar(char)
                
                elif char in ["*", "%", "^"]:
                    self.state = 3
                    self.andChar(char)
                    self.addTokens()
                
                else:
                    if char not in [" ", "\n", "\0"]:
                        self.andChar(char)
                        self.addTokens()



            elif self.state == 1:  # número entero
                if char.isdigit():
                    self.andChar(char)
                elif char == ".":
                    self.state = 8
                    self.andChar(char)
                else:
                    self.addTokens()
                    self.state = 0
                    continue  # << Volver a procesar el mismo caracter

            elif self.state == 2:  # identificador
                if re.match(r"[a-zA-Z]", char) or char.isdigit():
                    self.andChar(char)
                else:
                    self.addTokens()
                    self.state = 0
                    continue

            elif self.state == 3:  # signo positivo
                if char.isdigit():
                    self.state = 1
                    self.andChar(char)
                elif char == "+":
                    if self.token == "+":
                        self.andChar(char)
                        self.state = 3
                        self.addTokens()
                    else:
                        self.error(1)
                else:
                    self.addTokens()
                    continue
                

            elif self.state == 4:  # signo negativo
                if char.isdigit():
                    self.state = 1
                    self.andChar(char)
                elif char == "-":
                    if self.token == "-":
                        self.andChar(char)
                        self.state = 3
                        self.addTokens()
                    else:
                        self.error(1)
                else:
                    self.addTokens()
                    continue

            elif self.state == 5:
                if char in ["<", ">", "!"]:
                    if self.token in ["<", ">"]:
                        self.andChar(char)
                    else:
                        self.error(1)
                elif char == "=":
                    self.andChar(char)
                    self.state = 6
                    self.addTokens()
                    self.state = 0
                else:
                    self.addTokens()
                    self.state = 0
                    continue

            elif self.state == 7:
                # símbolos individuales, ya procesado
                self.state = 0

            elif self.state == 8:
                if char.isdigit():
                    self.state = 9
                    self.andChar(char)
                else:
                    self.state = 9
                    self.addTokens()
                    continue

            elif self.state == 9:
                if char.isdigit():
                    self.andChar(char)
                elif char in [" ", "\n", "\0"] or not char.isdigit():
                    self.addTokens()
                    self.state = 0
                    continue

            elif self.state == 10:
                if char == "*":
                    self.state = 11
                    self.andChar(char)
                elif char == "/":
                    self.state = 12
                    self.andChar(char)
                else:
                    self.state = 3
                    self.addTokens()
                    self.state = 0
                    continue

            elif self.state == 11:
                if char == "/":
                    self.state = 12
                    self.andChar(char)
                elif char in [" ", "\n"]:
                    self.andChar(char)
                elif re.match(r"[a-zA-Z]", char):
                    self.andChar(char)
                elif char == "*":
                    self.state = 13
                    self.andChar(char)
                else:
                    self.error(11)

            elif self.state == 12:
                if char == "\n":
                    self.andChar(char)
                    self.addTokens()
                elif re.match(r"[a-zA-Z]", char):
                    self.state = 12
                    self.andChar(char)
                else:
                    self.error(12)
                

            elif self.state == 13:
                if char == "*":
                    self.state = 13
                    self.andChar(char)
                elif char == "/":
                    self.state = 13
                    self.andChar(char)
                    self.addTokens()
                elif char == "\n":
                    self.andChar(char)
                elif re.match(r"[a-zA-Z]", char):
                    self.state = 11
                    self.andChar(char)
                else:
                    self.error(11)

            elif self.state == 14:
                if char == "&":
                    if self.token == "&":
                        self.andChar(char)
                        self.addTokens()
                    else:
                        self.addTokens()
                elif char == "|":
                    if self.token == "|":
                        self.andChar(char)
                        self.addTokens()
                    else:
                        self.addTokens()
                else:
                    self.error(14)

            else:
                self.stateReset()

            i += 1

        if self.state not in [0, 13]:
            self.addTokens()
        return False

    def deleteComment(self):
        # Eliminar los tokens que sean comentarios
        for i in range(len(self.tokens) - 1, -1, -1):
            if self.tokens[i][1] == "COMENTARIO":
                del self.tokens[i]
        
        
        
                    
#DFA = Automata()

# Simulación de lectura de archivo
#code = "12h3 1.23 -456h 789.0\n 12.34 56.78 90.12\n //hola if == >= != <=\n int main(){\n cin >> x;\n }"

#lectura de archivo
# with open("prov2.txt", "r", encoding="utf-8", errors="ignore") as file:
#     code = file.read()

#print("Texto de entrada: ", code)

# DFA.process(code)

# print("Tokens:")
# for token in DFA.tokens:
#     print(token[0], ":", token[1])

# print("sin comentarios: ")
# print("Tokens:")
# DFA.deleteComment()
# for token in DFA.tokens:
#     print(token[0], ":", token[1])

