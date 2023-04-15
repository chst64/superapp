#!/usr/bin/env python3

""" 
Test de carga_codigobarras.py

TODO: Que pasa si la bbdd que pasamos no existe??
"""



import unittest
import carga_codigobarras


class TestNombreDescriptivo(unittest.TestCase):
    def test_lee_codigos(self):
        lista_codigos_test = carga_codigobarras.lee_codigos("./test_codigos.txt")
        lista_codigos = ['2970792001890',
                         '8008970054346',
                         '8431876281040',
                         '8413164005002']

        self.assertEqual(lista_codigos_test,lista_codigos,"No lee bien los codigos")

    def test_existe_codebar(self):

        CODIGO_DE_PRUEBAS = '8410066128273'
        BBDD_FILE = "bbdd_test.bd"

        self.assertTrue(carga_codigobarras.existe_codebar(CODIGO_DE_PRUEBAS, BBDD_FILE))

    def test_get_foodfacts(self):

        CODIGO_DE_PRUEBAS = '8410066128273'

        producto_test = carga_codigobarras.get_foodfacts(CODIGO_DE_PRUEBAS)
        print(producto_test)

        self.assertIsInstance(producto_test,dict)

    def test_inserta_producto(self):
        BBDD_FILE = "bbdd_test.bd"
        CODIGO_DE_PRUEBAS = '8410066128273'
        PRODUCTO_TEST = {'code': '0', 'marca': 'ACME', 'nombre': 'Producto de pruebas', 'cantidad': '350g', 'imagen': 'https://images.openfoodfacts.org/images/products/841/006/612/8273/front_es.8.200.jpg', 'codigobarras': '1234567890123'}

        producto_test =carga_codigobarras.get_foodfacts(CODIGO_DE_PRUEBAS)
        carga_codigobarras.inserta_producto(producto_test, BBDD_FILE)



    

if __name__ == "__main__":
    unittest.main()
