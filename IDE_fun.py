#funciones del IDE

import os
import sys
import json

files_opened = []

def reedopenfiles():
    global files_opened
    try:
        with open('files_opened.json', 'r') as file:
            files_opened = json.load(file)
    except:
        files_opened = []

def reedfiles(files_opened):
    for file in files_opened:
        os.system(f'notepad {file}')

def openfile(file):
    os.system(f'notepad {file}')
    files_opened.append(file)
    with open('files_opened.json', 'w') as file:
        json.dump(files_opened, file)

def closefile(file):
    files_opened.remove(file)
    with open('files_opened.json', 'w') as file:
        json.dump(files_opened, file)

reedopenfiles()
reedfiles(files_opened)