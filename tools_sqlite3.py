#!/usr/bin/env python3

""" 
modulo herramientas en proyecto superapp
Modulo con funciones utiles para gestionar una bbdd sqlite3

Version: 13-febrero
================================================================================
"""
import os
import sqlite3


class basedatos():
    """
    Esta es la docstring de la clase basedatos
    """
    def __init__(self,fichero_basedatos):
        # print("Hola estoy en __init__")
        self.fichero_basedatos = fichero_basedatos
    

    class tabla():

        def __init__(self, cursor, nombre_tabla):
            """
            Una tabla dentro de la base de datos.

            self.columnas: devuelve una lista de tuplas con los datos de las columnas de la tabla
            self.nombre: devuelve nombre de la tabla
            """
            self.nombre = nombre_tabla
            self.cursor = cursor
            
            SQL_QUERY = f"SELECT * from {self.nombre}"
            #self.dame_todo = self.cursor.execute(SQL_QUERY).fetchall() 

            self.columnas = self.cursor.execute(f'select * from {self.nombre}').description


        def get_producto(self,producto,columna):
            """
            Busca un elemento en una columna. Por defecto busca la cadena exacta pero 
            si quieres buscar todo lo que tenga la palabra 'aceituna' hay que pasarle
            la cadena '%aceituna%'

            producto: palabra a buscar. Puedes usar %palabra% como si fuesen *
            columna: columna de la tabla donde buscar
            return: Lista de tuplas con el resultado
            """
            cadena_a_buscar = producto
            SQL_QUERY_PRODUCTO = f"select * from {self.nombre} where {columna} like ? "
            self.cursor.execute(SQL_QUERY_PRODUCTO,(producto,))
            resultado = self.cursor.fetchall()
            lista_res = []
            lista_col = self.columnas

            for res in resultado:
                dicc_tmp={}
                for i in range(len(lista_col)):
                    #print(">> entrada:",res[i],lista_col[i][0])
                    dicc_tmp.update({lista_col[i][0]:res[i]})
                lista_res.append(dicc_tmp)

            return(lista_res)

        def saca_todo(self):
            """
            Devuelve todos los elementos de la tabla
            Parametros:
            return: Lista de diccionarios: [{id,nombre},{id,nombre},...]

            """
            SQL_QUERY_ALL = f"select * from {self.nombre}"

            self.cursor.execute(SQL_QUERY_ALL)
            resultado = self.cursor.fetchall()
            lista_res = []
            lista_col = self.columnas
            for res in resultado:
                dicc_tmp={}
                for i in range(len(lista_col)):
                    #print(">> producto:",res[i],lista_col[i][0])
                    dicc_tmp.update({lista_col[i][0]:res[i]})
                lista_res.append(dicc_tmp)
            return(lista_res)

        def crea_fila(self,columnas,datos):
            """
            Crea una entrada
            """
            sql_insert = f"insert into {self.nombre}{columnas} values {datos} "
            self.cursor.execute(sql_insert)
            return(self.cursor.lastrowid)

        def actualiza_fila(self,id,columna,dato):
            """
            Modifica los datos de una entrada de la bbdd
            Despues de actualiza_fila() hay que hacer un bbdd.commit()

            :id: id de la fila a modificar
            :columna: columna de la fila a modificar
            :dato: nuevo valor
            """
            # print("He recibido:",columna,dato)
            sql_update = f"""update {self.nombre} set '{columna}' = '{dato}' where id={id} """
            # print(">>SQL_UPDATE:",sql_update)
            self.cursor.execute(sql_update)

        def borra_fila(self, id):
            """Borra la entrada de una tabla

            :id: id de la entrada a borrar
            :returns: TODO

            """
            sql_borra = f"""DELETE FROM {self.nombre} WHERE id={id} """
            try:
                self.cursor.execute(sql_borra)
            except Exception as e:
                raise e
            else:
                #self.bbdd.commit()
                #print("Borrada la entrada con id ",id)
                pass

    def __enter__(self):
        """
        Docstring de __enter__
        """

        self.conn = sqlite3.connect(self.fichero_basedatos)
        self.cursor = self.conn.cursor()

        SQL_CONSULTA_TABLAS = "SELECT name FROM sqlite_master WHERE type='table'"
        tablas_tmp = [tabla for tabla in self.conn.execute(SQL_CONSULTA_TABLAS)]

        SQL_CONSULTA_VISTAS = "SELECT name FROM sqlite_master WHERE type='view'"
        vistas_tmp = [vista for vista in self.conn.execute(SQL_CONSULTA_VISTAS)]

        # Lista con el nombre de las tablas
        self.tablas = [tabla[0] for tabla in tablas_tmp] # Como la query te devuelve en modo (valor,) para sacar valor hago tabla[0]

        # Lista con el nombre de las vistas
        self.vistas = [vista[0] for vista in vistas_tmp] # Como la query te devuelve en modo (valor,) para sacar valor hago tabla[0]
        self.tbl_producto = self.tabla(self.cursor,self.tablas[0])
        self.tbl_supermercado = self.tabla(self.cursor,self.tablas[1])
        self.tbl_compra = self.tabla(self.cursor,self.tablas[2])
        self.vista_compra = self.tabla(self.cursor,self.vistas[0])

        return self



    def __exit__(self, exception_type, exception_value, traceback):
        self.conn.close()






