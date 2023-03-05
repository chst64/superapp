#!/usr/bin/env python3

""" 
Lee los codigos de barras de un archivo de texto y guarda el producto 
correspondiente en la base de datos

"""
import tools_sqlite3 as tool
import math
import openfoodfacts
import requests
import shutil

bbdd_file = "./basedatos.db"


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

    lista_codigos_barras = []
    with open(fichero_codigos) as fichero:
        for line in fichero.readlines():
            line = line.strip()
            if line=='':
                pass
            else:
                lista_codigos_barras.append(line)

    return(lista_codigos_barras)

def existe_codebar(codigo_barras):
    """
    Comprueba si el producto con "codigo_barras" esta en la base de datos

    Parametros:
    codigo_barras: Codigo de barras del producto a comprobar
    return: True si existe, False si no existe
    """
    print("Recibido",codigo_barras)
    with tool.basedatos(bbdd_file) as bbdd:
        datos = bbdd.tbl_producto.get_producto(codigo_barras,"codigoBarras")
        print(">>>> datos de bbdd",datos)

        # La lista 'datos' tiene algo
        if datos:
            return True
        # La lista 'datos' esta vacia
        else:
            return False

def info_producto(codigoBarras):
    """Coje la informacion del producto de openfoodfacts

    :codigoBarras: Codigo de barras del producto a buscar
    :returns: Diccionario con los datos del producto

    """
    pass

def get_foodfacts(codigoBarras):
    """
    Pruebas de webscrapping para coger informacion de un producto
    de la pagina 

    https://github.com/openfoodfacts/openfoodfacts-python
    """

    product = openfoodfacts.products.get_product(codigoBarras)

    # Claves de los diccionarios de los productos
    # print(">>>> product",product.keys())
    # print(">>>> product['product']",product['product'].keys())

    info={'code':'0','marca':'sinmarca','nombre':'sin nombre','cantidad':1,'imagen':None}
    if product['status_verbose']=='product found':
        if "status_verbose" in product:
            print("Status-verbose:",product['status_verbose'])
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
        print(">>> ",codigoBarras, " no existe en openfoodfacts")
        return None

def inserta_producto(info_producto):
    """Inserta los datos de producto en la bbdd. 

    :info_producto: Datos del producto

    """

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
        print("Añadido producto",datos, " en id:",id)

        # Descarga la foto del producto si existe y lo nombra con su id 
        if info_producto['imagen'] != None:
            foto_producto = requests.get(info_producto['imagen'],allow_redirects=True)
            nombre_foto = str(id) +'.jpg'
            open(nombre_foto,'wb').write(foto_producto.content)

            # Movemos la foto al directorio de fotos
            try:
                shutil.move(nombre_foto,"./static/images/")
            except:
                print("Hay un error al mover la foto")



# *********************************
# *   MAIN 
# *********************************

if __name__ == "__main__":
    lista_codigos = lee_codigos("EAN.txt")

    for codigo in lista_codigos:
        print("********************")
        if existe_codebar(codigo):
            print(f"el codigo -{codigo}- SII existe")
        else:
            print(f"el codigo -{codigo}- NO existe en la bbdd. Cojo informacion de openfoodfacts")
            datos = get_foodfacts(codigo)

            if datos!=None:
                inserta_producto(get_foodfacts(codigo))








    

