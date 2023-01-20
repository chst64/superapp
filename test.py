#!/usr/bin/env python3

""" 
Programa para testear el modulo de herramientas

"""

import herramientas

bbdd_file = "./basedatos.db"


print ("*** Inicio test ***")

print("== Existe_bbdd ==")

if herramientas.existe_bbdd(bbdd_file):
    print("La base de datos existe")

conn = herramientas.create_connection(bbdd_file)

print("== lista_tablas() ==")
print(herramientas.lista_tablas(conn))

print("== lista_columnas() ==")
print(herramientas.lista_columnas(conn,"producto"))

print("== existe_entrada() ==")
entrada = herramientas.existe_entrada(conn,"leche semidesnatada","name","producto")
if entrada == "None":
    print("!!!! La entrada no existe")
else:
    print(entrada)



