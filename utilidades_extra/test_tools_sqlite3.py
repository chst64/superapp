#!/usr/bin/env python3

""" 
Test para el modulo "tools_sqlite3"

"""
print ("Hola mundo")

import unittest
import utilidades_extra.tools_sqlite3 as tool
import pathlib

# Base de datos para pruebas
BBDD_FILE = "bbdd_test.bd"


class TestSacaTodo(unittest.TestCase):
    def test_existe_bbdd(self):
        ruta_bbdd = pathlib.Path(BBDD_FILE)
        self.assertTrue(ruta_bbdd.is_file(),f"{BBDD_FILE} No es un fichero o no existe")

    def test_vistas_son_lista(self):
        with tool.basedatos(BBDD_FILE) as bbdd:
            self.assertIsInstance(bbdd.vistas,list,f"{bbdd.vistas} deberia ser una lista")

    def test_tablas_son_lista(self):
        with tool.basedatos(BBDD_FILE) as bbdd:
            self.assertIsInstance(bbdd.tablas,list,f"{bbdd.tablas} deberia ser una lista")

    def test_saca_todo(self):
        with tool.basedatos(BBDD_FILE) as bbdd:
            todos_los_datos = bbdd.tbl_producto.saca_todo()
            self.assertIsInstance(todos_los_datos,list,"{todos_los_datos} deberia ser una lista")

    def test_get_producto(self):
        with tool.basedatos(BBDD_FILE) as bbdd:
            producto_buscado = bbdd.tbl_producto.get_producto("3","id")
            self.assertIsInstance(producto_buscado,list)


    def test_crea_fila(self):
        with tool.basedatos(BBDD_FILE) as bbdd:
            datos=("123456","producto_test","ACME","","2","cosas","5")
            datos_columnas=("codigoBarras","name","marca","envase","cantidad","unidad","puntuacion")

            bbdd.tbl_producto.crea_fila(datos_columnas,datos)
            bbdd.conn.commit()

            producto_buscado = bbdd.tbl_producto.get_producto("producto_test","name")

            self.assertEqual(producto_buscado[0]["codigoBarras"], int(datos[0]),\
                    f"""Obtengo {producto_buscado[0]["codigoBarras"]} y deberia ser {datos[0]}""")

            self.assertEqual(producto_buscado[0]["name"], datos[1],\
                    f"""Obtengo {producto_buscado[0]["name"]} y deberia ser {datos[1]}""")

            self.assertEqual(producto_buscado[0]["marca"], datos[2],\
                    f"""Obtengo {producto_buscado[0]["marca"]} y deberia ser {datos[2]}""")

            self.assertEqual(producto_buscado[0]["cantidad"], float(datos[4]),\
                    f"""Obtengo {producto_buscado[0]["cantidad"]} y deberia ser {datos[4]}""")

            self.assertEqual(producto_buscado[0]["unidad"], datos[5],\
                    f"""Obtengo {producto_buscado[0]["cantidad"]} y deberia ser {datos[5]}""")

if __name__ == "__main__":
    unittest.main()
