#!/usr/bin/env python3
import PIL
from PIL import Image
import os

""" 
Comprueba las medidas de todas las imagnenes. 
Si son grandes las redimensiona 

"""
ALT_MAX = 120
print ("Hola mundo")

img = Image.open("./1.jpg")
print(img.size)

"""
########################
#  Para redimensionar  #
########################
img_resize = img.resize((256,256))
img_resize.save("./imagen_pequeña.jpg")

"""

ruta = os.getcwd()

imagenes = os.scandir(ruta)
for imagen in imagenes:
    print("*****************")
    if imagen.is_file and imagen.path.endswith(".jpg"):
        print("Nombre:",imagen.path)
        img = Image.open(imagen.path)
        sizex,sizey=img.size
        escala = sizey / ALT_MAX
        sizey_new = ALT_MAX

        sizex_new = int(sizex / escala)

        nombre,ext = os.path.splitext(imagen.path)
        nombre_nuevo = nombre+"_modificada"+ext

        print("Tamaño antiguo:", sizex,sizey)
        print("Tamaño nuevo:", sizex_new, sizey_new) 
        print("Nombre nuevo:",nombre_nuevo)

        img_resize = img.resize((sizex_new, sizey_new))
        #img_resize.save(nombre_nuevo)

        img_resize.save(imagen.path)
       
       
print("FIN")
