#!/usr/bin/env python3

""" 
modulo herramientas en proyecto superapp
Modulo con funciones utiles para gestionar la bbdd

Version: 20-enero-2023
"""
import os
import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except:
        print("Error al crear la conexion con la base de datos. ")

    return conn


def existe_bbdd(archivo_bbdd):
    """Comprueba que existe el fichero de la bbdd y si no doy instrucciones de como crearlo
    RETURN: 1 si existe el fichero y 0 si no existe

    """
    if os.path.exists(archivo_bbdd):
        print("El fichero ",archivo_bbdd,"existe")
        return(1)
    else:
        print("El fichero ",archivo_bbdd,"no existe")
        print(" Para crearlo ejecutar inicia_bbdd.sh")
        return(0)


def existe_entrada(conn,entrada,columna,tabla):
    """Comprueba que exista una entrada en una colunmna de una tabla. Si existe devuelve el id 

    :conn: El enlace a la base de datos
    :entrada: Entrada que hay que comprobar que exista 
    :tabla: Tabla donde hay que comprobar que exista esa entrada
    :columna: Columna donde hay que buscar esa entrada 
    :returns: la fila completa donde aparece esa entrada, None si no existe

    """
    
    SQL_BUSCA_ENTRADA = f" SELECT * FROM {tabla} WHERE {columna}=? "

    cur = conn.cursor()
    cur.execute(SQL_BUSCA_ENTRADA, (entrada,))
    row = cur.fetchone() 

    return None if row == None else row



def lista_tablas(conn):
    """Lista las tablas que tiene la base de datos
    :conn: El enlace con la base de datos
    :returns: lista de los nombres de las tablas

    """
    sql_query = "SELECT name FROM sqlite_master WHERE type='table'"
    cur = conn.cursor()
    tablas = cur.execute(sql_query)
    return([tabla for tabla in tablas])

def lista_columnas(conn,tabla):
    """Lista los nombres de las columnas de una tabla concreta
    :conn: El enlace con la base de datos
    :tabla: Tabla de la que queremos saber los nombres de las columnas
    :returns: lista con los nombres de las columnas"""
    cur = conn.cursor()
    columnas = cur.execute(f"select * from {tabla}")
    for col in columnas.description:
        print(col[0])
    return( [col[0] for col in columnas.description] )
    




