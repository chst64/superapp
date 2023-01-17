#!/usr/bin/env python3

import os

""" 
Esto es un programa python que hace cosas

"""
print ("Programa de pruebas")

ruta = os.getcwd()
elementos = os.scandir(ruta)

for elemento in elementos:
    if elemento.is_file and elemento.path.endswith(".jpg"):
        print("Elemento:",elemento.path)
        file,exten = os.path.splitext(elemento.path)
        print("Fichero:",file)
        print("Extens:",exten)
