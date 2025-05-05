import re
#abrir el archivo TextIDE.txt
with open("TestIDE.txt", "r", encoding="utf-8", errors="ignore") as file:
    code = file.read()

chart=''

print(code)