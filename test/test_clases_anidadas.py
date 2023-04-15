#!/usr/bin/env python3

""" 
Programa para testear el modulo "tools_sqlite3.py"

"""

from ..utilidades_extra import tools_sqlite3 as tool
from datetime import date,datetime



bbdd_file = "bbdd_piezas.db"

with tool.basedatos(bbdd_file) as bbdd:
    print(">>>> Tablas de la bbdd:",bbdd.tablas)
    print(">>>> Vistas de la bbdd:",bbdd.vistas)
    print(">>>> Nombre de tbl_piezas:",bbdd.tbl_piezas.nombre)
    print(">>>> Nombre de tbl_proveedores:",bbdd.tbl_proveedores.nombre)
    print(">>>> Nombre de tbl_rel_pieza_proveedor:",bbdd.tbl_rel_pieza_proveedor.nombre)
    

    # print(">>>> Nombre de tbl_producto:",bbdd.tbl_producto.nombre)
    # print(">>>> Saca_todo de tbl_producto: ",bbdd.tbl_producto.saca_todo()[0:5])
    # print(">>>> Columnas de tbl_producto:",bbdd.tbl_producto.columnas)
    # bbdd.tbl_compra.columnas
    # print(">>>> Todos los productos con '*patata*': ",bbdd.tbl_producto.get_producto("%patata%","name"))

    # print(">>>>> Producto con id=3: ",bbdd.tbl_producto.get_producto("3","id"))
    # print("La marca del producto id:10",bbdd.tbl_producto.get_producto("10","id")[0]["marca"])
    # print("El nombre del producto id:10",bbdd.tbl_producto.get_producto("10","id")[0]["name"])

    # print("======== vista_compra ============")
    # print(f""" >>>>>> Columnas vista_compra: {bbdd.vista_compra.columnas} """)
    # print(">>> Saca todo compras:",bbdd.vista_compra.saca_todo()[0:5])


# *** Crear entrada ***

    #nuevo_producto = input("Nombre del nuevo producto:")
    #datos_columnas=("codigoBarras","name","marca","envase","cantidad","unidad","puntuacion")
    #datos=("123456",nuevo_producto,"sinmarca","","2","cosas","5")
    #bbdd.tbl_producto.crea_fila(datos_columnas,datos)
    #bbdd.conn.commit()

# *** Actualiza entrada ***

    #id = bbdd.tbl_producto.get_producto("%altavox%","name")[-1]["id"]
    #print(">> id:",id)
    #bbdd.tbl_producto.actualiza_fila(id,columna="name",dato="Altavoz")
    #print(bbdd.conn.commit())

# *** Borra entrada ***

    #id = bbdd.tbl_producto.get_producto("UUUU","name")[0]["id"]
    #bbdd.tbl_producto.borra_fila(id)
    #bbdd.conn.commit()

# *** Crea compra ***
    #print("Columnas tbl_compras:",bbdd.tbl_compra.columnas)
    #id_producto = bbdd.tbl_producto.get_producto("%ratón%","name")[-1]["id"]
    #datos_columnas=("producto_id","supermercado_id","fecha","precio")
    #datos=(id_producto,1,"1/1/2023",50)
    #bbdd.tbl_compra.crea_fila(datos_columnas,datos)
    #bbdd.conn.commit()

# *** Supermercado **
    #print("======== supermercado ============")
    #print(f""" >>>>>> Columnas tbl_supermercado: {bbdd.tbl_supermercado.columnas} """)
    #lista_supers = bbdd.tbl_supermercado.saca_todo()
    #print(lista_supers)

    #h = [(s["id"],s["nombre"]) for s in bbdd.tbl_supermercado.saca_todo() ]
    #print(h)
    

# *** Actualiza compra ***
    #print("==== Actualiza compra ====")

    #id = 157 
    #producto_id = 153
    #fecha = date(2023, 2, 17)
    #fecha_formateada = f"{fecha.year}-{fecha.month}-{fecha.day}" 
    #supermercado_id = 1
    #precio = 49 


    #print(">>> Fecha_formateada",fecha_formateada)
    #datos_columnas=("producto_id","supermercado_id","fecha_formateada","precio")
    #datos=(producto_id,supermercado_id,fecha_formateada,precio)

    #bbdd.tbl_compra.actualiza_fila(id,datos_columnas,datos)
    #bbdd.conn.commit()

# *** Devuelve productos con su precio

    # todos_productos = bbdd.tbl_producto.saca_todo()

    # for prod in todos_productos:
    #     ultimo_precio = 0
    #     dato = bbdd.tbl_compra.get_producto(prod["id"],"producto_id")
    #     print(f"De compras:",dato)
    #     if dato:
    #         ultimo_precio = dato[-1]["precio"]

    #     prod.update({"ultimo_precio":ultimo_precio})
    #     print(f"""
    #     id: {prod["id"]}
    #     codigoBarras: {prod["codigoBarras"]}
    #     name: {prod["name"]}
    #     marca: {prod["marca"]}
    #     ultimo_precio: {prod["ultimo_precio"]}
    #     """)
