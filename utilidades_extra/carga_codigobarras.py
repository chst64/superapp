#!/usr/bin/env python3

# *** carga_codigobarras.py ***

""" 
Lee los codigos de barras de un archivo de texto y guarda el producto 
correspondiente en la base de datos

"""
import math
from os import close
import requests
import shutil
import sys
import logging
import pathlib

import openfoodfacts

from utilidades_extra import tools_sqlite3 as tool

BBDD_FILE = "./basedatos.db"
__version__ = "18-marzo-2023"
logger = logging.getLogger("carga_codigobarras.py")

# Imprimir en color rojo
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))

def chequeo_EAN13(barcode):
    """Comprobacion de que el codigo de barras de tipo EAN13 es correcto con el digito de control
    Codigo ejemplo: 8 4 1 2 5 8 4 5 1 2 5 4 1
    1- Sumamos todos los dígitos que ocupan las posiciones pares: 8+1+5+4+1+5 = 24 (pares)
    2- Sumamos todos los digitos que ocupan las posiciones impares: 4+2+8+5+2+4 = 25 (impares)
    3- Multiplicamos por 3 el valor obtenido en la suma de los dígitos impares: 25*3 = 75
    4- Sumamos al valor obtenido anteriormente,  la suma de los numeros pares: 24+ 75 = 99
    5- Redondeamos el valor obtenido a la decena inmediatamante superior, en este caso 100
    6- El dígito de control es el valor obtenido del redondeo de decenas menos la suma total del punto 4: 100 – 99 = 1

    :barcode: codigo barras a comprobar
    :returns: True si esta bien, False si esta mal
    """
    print(">> Chequeo EAN13")
    if len(barcode)==13:
        numeros = str(barcode) 

        # Separamos cada codigo barras en una lista de digitos
        lista_numeros=[int(numeros[n]) for n in range(len(numeros))]

        # Sumo los pares
        suma_pares = 0
        for x in range(0,len(lista_numeros)-1,2):
            suma_pares = suma_pares + lista_numeros[x] 

        # Sumo los impares
        suma_impares = 0
        for x in range(1,len(lista_numeros),2):
            suma_impares = suma_impares + lista_numeros[x] 

        paso4 = (suma_impares*3)+suma_pares
        redondeo_decena = (math.ceil(paso4/10))*10 # Falta hacer este paso 
        digito_control = redondeo_decena - paso4  

        print(f"{barcode}: Impares:{suma_impares} Pares:{suma_pares} Paso4:{paso4} Redondeo:{redondeo_decena} DC:{digito_control}")

        if digito_control == lista_numeros[-1]:
          return True
        else:
          return False

    else:
      print("El codigo de barras",barcode," no es EAN13")

def lee_codigos(fichero_codigos):
    """
    Guarda en una lista los codigos de barras que tiene un fichero de texto

    fichero_codigos: fichero de texto donde estan los codigos de barras. 1 codigo de barras en cada linea
    return: lista con los codigos de barras 
    """

    logger.info("Hola desde lee_codigos")
    lista_codigos_barras = []
    with open(fichero_codigos) as fichero:
        for line in fichero.readlines():
            line = line.strip()
            if line=='':
                pass
            else:
                lista_codigos_barras.append(line)

    return(lista_codigos_barras)

def existe_codebar(codigo_barras,bbdd_file):
    """
    Comprueba si el producto con "codigo_barras" esta en la base de datos

    Parametros:
    codigo_barras: Codigo de barras del producto a comprobar
    bbdd_file: Base de datos donde mirar si existe el codigo de barras
    return: True si existe, False si no existe
    """

    logger.info("Hola desde existe_codebar")
    logger.info(f"Recibido {codigo_barras}")
     
    with tool.basedatos(bbdd_file) as bbdd:
        datos = bbdd.tbl_producto.get_producto(codigo_barras,columna="codigoBarras")

        logger.debug(f"Recibido de bbdd: {datos}")

        # La lista 'datos' tiene algo
        if datos:
            logger.info(f">>>> datos de bbdd: { datos[0]['name'] } - {datos[0]['marca']} ")
            return True
        # La lista 'datos' esta vacia
        else:
            logger.warning(f">>> No existe el codigo de barras {codigo_barras} en la bbdd")
            return False


def get_foodfacts(codigoBarras):
    """
    Coje datos de openfoodfacts
    https://github.com/openfoodfacts/openfoodfacts-python

    -- Parametros --
    codigoBarras: codigo de barras del producto a buscar
    return: diccionario con la informacion. Keys: codigobarras, marca, nombre, cantidad, imagen
    """

    logger.info("Hola desde get_foodfacts")
    product = openfoodfacts.products.get_product(codigoBarras)

    # Claves de los diccionarios de los productos
    # print(">>>> product",product.keys())
    # print(">>>> product['product']",product['product'].keys())

    info={'code':'0','marca':'sinmarca','nombre':'sin nombre','cantidad':1,'imagen':None}
    if product['status_verbose']=='product found':
        if "status_verbose" in product:
            logger.info("Status-verbose:",product['status_verbose'])
        if "code" in product:
            info.update({'codigobarras':product['code']})
        if "brands" in product['product']:
            info.update({'marca':product['product']['brands']})
        if "product_name_es" in product['product']:
            info.update({'nombre':product['product']['product_name_es']})
        if "quantity" in product['product']:
            info.update({'cantidad':product['product']['quantity']})
        if "image_front_small_url" in product['product']:
            info.update({'imagen':product['product']['image_front_small_url']})

        return(info)
    else:
        logger.warning(">>> ",codigoBarras, " no existe en openfoodfacts")
        return None

def inserta_producto(info_producto, bbdd_file):
    """Inserta los datos de producto en la bbdd. 

    -- Parametros --
    info_producto: Datos del producto
    bbdd_file: Base de datos donde guardar los datos

    """

    logger.info("Hola desde inserta_producto")
    datos_columnas=("codigoBarras","name","marca","cantidad","unidad","puntuacion","observaciones")
    datos=(
            info_producto['codigobarras'],
            info_producto['nombre'],
            info_producto['marca'],
            1,
            "unidad",
            5,
            info_producto['cantidad'])

    with tool.basedatos(bbdd_file) as bbdd:
        id = bbdd.tbl_producto.crea_fila(datos_columnas,datos)
        bbdd.conn.commit()
        logger.info(f"Añadido producto {datos} en id:{id}")

        # Descarga la foto del producto si existe y lo nombra con su id 
        if info_producto['imagen'] != None:
            foto_producto = requests.get(info_producto['imagen'],allow_redirects=True)
            nombre_foto = str(id) +'.jpg'
            with open(nombre_foto,'wb') as fichero:
                print(f"Grabando fichero {nombre_foto}")
                fichero.write(foto_producto.content)

            # Movemos la foto al directorio de fotos
            try:
                print("Ruta actual:",pathlib.Path.cwd())
                # shutil.move(nombre_foto,"../static/images/")
                shutil.move(nombre_foto,"./static/images/")
            except:
                logger.warning(f"Hay un error al mover la foto {nombre_foto}")

def carga_codigobarras(fichero_codigos,bbdd_file):
    # Hace todo el trabajo de cargar los codigos, buscar en la bbdd, coger los 
    # datos de openfoodfacts y añadir a la bbdd

    lista_codigos = lee_codigos(fichero_codigos)
    for codigo in lista_codigos:

            logger.info("==========================")
            logger.info(f"Buscando codigo {codigo}")
            if existe_codebar(codigo, bbdd_file=bbdd_file):
                logger.info(f"el codigo -{codigo}- SI existe en la bbdd {bbdd_file}")
            else:
                logger.info(f"el codigo -{codigo}- NO existe en la bbdd {bbdd_file}. Cojo informacion de openfoodfacts")
                datos = get_foodfacts(codigo)
                logger.info(f"Info de get_foodfacts: {datos}")

                if datos!=None:
                    inserta_producto(get_foodfacts(codigo), bbdd_file)


# *********************************
# *   MAIN 
# *********************************

if __name__ == "__main__":
    
    # LOGGER
    logging.basicConfig(
            filename='carga_codigobarras.log',
            filemode='w',
            format='%(asctime)s:%(levelname)s - %(message)s',
            level=logging.INFO)

    logger.info("**************** \n Ejecutando carga_codigobarras.py")
    logger.info(f"** {__version__} **")


    if len(sys.argv)>1:
        lista_codigos = lee_codigos(sys.argv[1])

        for codigo in lista_codigos:

            logger.info("==========================")
            logger.info(f"Buscando codigo {codigo}")
            if existe_codebar(codigo, BBDD_FILE):
                logger.info(f"el codigo -{codigo}- SI existe en la bbdd")
            else:
                logger.info(f"el codigo -{codigo}- NO existe en la bbdd. Cojo informacion de openfoodfacts")
                datos = get_foodfacts(codigo)

                if datos!=None:
                    inserta_producto(get_foodfacts(codigo), BBDD_FILE)

    else:
        logger.critical("No has pasado un fichero con codigos de barras")
        prRed("** Tienes que pasar un fichero con codigo de barras")









    

