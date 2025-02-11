import re

regex = r"[a-zA-Z_][a-zA-Z0-9_]*"


a="fgh"
b="0as"

if re.match(regex, a):
    print("Match")
    print(re.match(regex, a).group())
else:
    print("No match")

if re.match(regex, b):
    print("Match")
    print(re.match(regex, b).group())
else:
    print("No match")
    print(re.match(regex, b).group())