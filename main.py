#!/usr/bin/python3

""" 
**********************************************************************
!!!!!!!!!!!! VERSION SIN SQLALCHEMY   !!!!!!!!!!!!!!
**********************************************************************
================================================================================

Pagina web dinamica con flask que muestra una base de datos de productos de
supermercado. Se pueden borrar, editar y añadir nuevos productos

Para iniciar la base de datos:
    desde la consola python:
    from app.py import db
    db.create_all()

V2: Modificada para usar SQLAlchemy
V3: Modificada para tener bbdd de productos, de compras, ...
V4: Modificada para NO usar SQLAlchemy

#######################################################################
#                                TODO                                 #
#######################################################################
- Mejorar la pagina index.html, meter un foto de un bodegon o algo  
- En nuevo producto, mejorar el ancho de los campos
- En nueva compra, mejorar la disposicion de los campos
- Posibilidad de crear nuevos supermercados
- No funciona "editar compra" y no sale la lista de supermercados
- Coger datos de es.openfoodfacts.org
- Que hagas una lista de compra virtual y te diga los productos que han subido de precio y los que han bajado. Por ejemplo para saber si las ofertas del 3x2 del Carrefour son reales o te estan timando
- Cuando haces una compra volver a pagina productos
- en lista_compras.html y lista_productos.html añadir boton para volver al principio de la pagina
- Editar la compra desde la pagina de producto
- Boton subir para ir al inicio de pagina
- Lector de codigo de barras
- Boton de editar compra en la pagina de producto

"""

from datetime import date,datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, DecimalField, SelectField,SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.exceptions import abort

import tools_sqlite3 as tool

app = Flask(__name__)
app.config['SECRET_KEY']='abcde'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basedatos.db'
DB_FILE = "./basedatos.db"
supermercado_defecto = 2
#db = SQLAlchemy(app)
__version__ = "3-marzo-2023"


#def get_producto(producto_id):
#    
#    producto = db.session.query(Producto).filter_by(id=producto_id).first()
#    print("En get_producto el producto es",producto.name)
#    return producto
#
#def get_compra(compra_id):
#    compra = db.session.query(Compra).filter_by(id=compra_id).first()
#    print(f"En get_compra la compra es {compra.id}:{compra.producto.name}-{compra.supermercado.nombre} - {compra.precio}")
#    return compra
#
#def compras_producto(producto_id):
#    compras_del_producto = db.session.query(Compra).filter_by

# Formularios de FlaskForm

class Producto_Form(FlaskForm):
    name = StringField("Nombre", validators=[
        DataRequired(message="El campo es obligatorio")
        ])
    codigoBarras = DecimalField("codigoBarras")
    marca = StringField("Marca", validators=[
        DataRequired(message="Tienes que poner una marca")])
    #supermercado = StringField("Supermercado")
    envase = StringField("Envase") # Tetra-brik, lata,...
    cantidad = DecimalField("Cantidad") # Antes era medida
    categoria = StringField("Categoria")
    unidad = StringField("Unidad")
    precio = DecimalField("Precio")
    #puntuacion = DecimalField("Puntuacion")
    puntuacion = DecimalField("Puntuacion",default=5)
    observaciones = StringField("Observaciones")
    submit = SubmitField("Enviar")

class Compra_Form(FlaskForm):
    #supermercado = StringField("Supermercado")
    supermercado = SelectField("Supermercado", coerce=int)
    fecha = DateField("Fecha compra",
                      format='%Y-%m-%d',
                      default = datetime.today())
    empaquetado = StringField("Empaquetado")
    observaciones = StringField("Observaciones")
    precio = DecimalField("Precio")

    submit = SubmitField("Enviar")

class Edit_Compra_Form(FlaskForm):
    #supermercado = StringField("Supermercado")
    supermercado = SelectField("Supermercado", coerce=int)
    fecha = DateField("Fecha compra", format='%Y-%m-%d')
    empaquetado = StringField("Empaquetado")
    observaciones = StringField("Observaciones")
    precio = DecimalField("Precio")

    submit = SubmitField("Enviar")


# ******************
# Rutas
# ******************

#bbdd = herramientas.basedatos(DB_FILE)
#cursor = bbdd.cursor
#tbl_producto = herramientas.tabla(bbdd,bbdd.tablas[0])
#tbl_producto = herramientas.tabla(cursor,bbdd.tablas[0])
#tbl_supermercado = herramientas.tabla(bbdd,bbdd.tablas[1])
#tbl_compra = herramientas.tabla(bbdd,bbdd.tablas[2])
#vista_compra = herramientas.tabla(bbdd,bbdd.vistas[0])

@app.route('/')
def index():
    print(">>>>>>>>>> Estoy en indice")
    return render_template('index.html',version=__version__) 

# Ver la lista de productos
# TODO: Pasar tambien el precio del producto:  <24-02-23, yourname> #
@app.route('/lista_productos',methods=['GET','POST'])
def bd():
    print("*** Estoy en bd ***")
    with tool.basedatos(DB_FILE) as bbdd:
        if request.method == 'POST':
            name = request.form['name'] 
            name = "%"+name+"%"
            dato2 = bbdd.tbl_producto.get_producto(name,"name")
            if dato2:
                for prod in dato2:
                    ultimo_precio = 0
                    dato_compra = bbdd.tbl_compra.get_producto(prod["id"],"producto_id")
                    if dato_compra:
                        ultimo_precio = dato_compra[-1]["precio"]
                    prod.update({"ultimo_precio":ultimo_precio})
                return render_template('lista_productos.html',datos=dato2) 
            else:
                print("NO HAY DATOS")
                
                dato = bbdd.tbl_producto.saca_todo()
                for prod in dato:
                    print(">>> Tengo",prod)
                    ultimo_precio = 0
                    dato_compra = bbdd.tbl_compra.get_producto(prod["id"],"producto_id")
                    if dato_compra:
                        ultimo_precio = dato_compra[-1]["precio"]
                    prod.update({"ultimo_precio":ultimo_precio})
                return render_template('lista_productos.html',datos=dato) 

        dato = bbdd.tbl_producto.saca_todo()
        
        for prod in dato:
            ultimo_precio = 0
            dato_compra = bbdd.tbl_compra.get_producto(prod["id"],"producto_id")
            if dato_compra:
                ultimo_precio = dato_compra[-1]["precio"]
            prod.update({"ultimo_precio":ultimo_precio})

        print(">>> Primeros 10 datos:",dato[0:10])
        return render_template('lista_productos.html',datos=dato) 


# Ver la lista de compras 
@app.route('/lista_compras',methods=['GET','POST'])
def compras():
    """ 
    Ver la lista de compras
    """
    print("*** Estoy en compras ***")
    with tool.basedatos(DB_FILE) as bbdd:
        if request.method == 'POST':
            name = request.form['name']
            name = "%" + name + "%"
            print("Tengo",name)
            #dato2 = Compra.query.join(Producto).filter(Producto.name.like(name)).all()
            datos2 = bbdd.tbl_compra.get_producto(name,"name")
            if dato2:
                return render_template('lista_compras.html',datos=dato2) 
            else:
                print("NO HAY DATOS")

                #dato = db.session.query(Compra).all()
                dato = bbdd.vista_compra.saca_todo()
                return render_template('lista_compras.html',datos=dato)

        #dato = db.session.query(Compra).order_by("fecha").all()
        dato = bbdd.vista_compra.saca_todo()
        return render_template('lista_compras.html',datos=dato)
        
@app.route('/<int:producto_id>')
def producto(producto_id):
    """
    Informacion de un producto
    """
    with tool.basedatos(DB_FILE) as bbdd:
        producto = bbdd.tbl_producto.get_producto(producto_id,"id")
        if producto!=None:
             #compras = db.session.query(Compra).filter_by(producto_id = producto.id).all()
             compras = bbdd.vista_compra.get_producto(producto_id,"producto_id")


        print(">>>> Quiero devolver ",producto,compras)
        return render_template('producto.html',producto=producto[0], compras=compras)

# Crear producto nuevo
@app.route('/create',methods=['GET','POST'])
def create2():
    """
    Crea un producto nuevo

    return: pagina_web create.html
    """
    with tool.basedatos(DB_FILE) as bbdd:
        form = Producto_Form()

        if form.validate_on_submit():
            codigoBarras = request.form['codigoBarras']
            name = request.form['name']
            marca = request.form['marca']
            #supermercado = request.form['supermercado']
            envase = request.form['envase']
            cantidad = request.form['cantidad']
            unidad = request.form['unidad']
            #precio = request.form['precio']
            puntuacion = request.form['puntuacion']
            observaciones = request.form['observaciones']

            datos_columnas=("codigoBarras","name","marca","envase","cantidad","unidad","puntuacion","observaciones")
            datos = (codigoBarras,name,marca,envase,cantidad,unidad,puntuacion,observaciones)
            bbdd.tbl_producto.crea_fila(datos_columnas,datos)
            bbdd.conn.commit()


            return redirect(url_for('bd'))
            

        return render_template('create.html',form=form)

# Editar producto
@app.route('/<int:id>/edit', methods=['GET','POST'])
def edit(id):
    """
    Edita un producto existente

    Parametros:
    id: id del producto a editar
    """
    with tool.basedatos(DB_FILE) as bbdd:
        producto = bbdd.tbl_producto.get_producto(id,"id")[0]
     
        if request.method == 'POST':
            codigoBarras = request.form['codigoBarras']
            name = request.form['name']
            marca = request.form['marca']
            #supermercado = request.form['supermercado']
            envase = request.form['envase']
            cantidad = request.form['cantidad']
            unidad = request.form['unidad']
            #precio = request.form['precio']
            puntuacion = request.form['puntuacion']
            observaciones = request.form['observaciones']

            if not name:
                flash('Se necesita nombre')
            else:
                bbdd.tbl_producto.actualiza_fila(id,columna="codigoBarras",dato=codigoBarras)
                bbdd.tbl_producto.actualiza_fila(id,columna="name",dato=name)
                bbdd.tbl_producto.actualiza_fila(id,columna="marca",dato=marca)
                #producto.supermercado = supermercado
                bbdd.tbl_producto.actualiza_fila(id,columna="envase",dato=envase)
                bbdd.tbl_producto.actualiza_fila(id,columna="cantidad",dato=cantidad)
                bbdd.tbl_producto.actualiza_fila(id,columna="unidad",dato=unidad)
                #producto.precio = precio
                bbdd.tbl_producto.actualiza_fila(id,columna="puntuacion",dato=puntuacion)
                bbdd.tbl_producto.actualiza_fila(id,columna="observaciones",dato=observaciones)
                bbdd.conn.commit()

                return redirect(url_for('bd'))

        return render_template('edit.html', producto=producto)

# Editar compra
@app.route('/compra/<int:id>', methods=['GET','POST'])
def editar_compra(id):
    """
    Edita una compra

    Parametros:
    id: id de la compra a editar
    """

    with tool.basedatos(DB_FILE) as bbdd:

        compra = bbdd.vista_compra.get_producto(id,"id")[0]

        print(f">>>>>>>>>> compra: {compra} ")
        form = Edit_Compra_Form()

        # Relleno la lista desplegable con los supermercados de la base de datos

        #form.supermercado.choices=[(g.id,g.nombre) for g in Supermercado.query.order_by('nombre')]
        form.supermercado.choices = [(s["id"],s["nombre"]) for s in bbdd.tbl_supermercado.saca_todo() ]
        #form.precio = compra["precio"]

        if form.validate_on_submit():
            fecha = request.form['fecha']
            supermercado = request.form['supermercado']
            empaquetado = request.form['empaquetado']
            observaciones = request.form['observaciones']
            precio = request.form['precio']

            # Separo la fecha tipo "2021-12-01" en año,mes y dia
            año,mes,dia = fecha.split("-")
            fecha_formateada = date(int(año),int(mes),int(dia))
            
            datos_columnas=("producto_id","supermercado_id","fecha","precio")
            datos=(int(compra["producto_id"]),supermercado,fecha_formateada,precio)
            print(">>>> datos_columnas:",datos_columnas)
            print(">>>> datos:",datos)

            bbdd.tbl_compra.actualiza_fila(id,columna="supermercado_id",dato=supermercado)
            bbdd.tbl_compra.actualiza_fila(id,columna="fecha",dato=fecha_formateada)
            bbdd.tbl_compra.actualiza_fila(id,columna="empaquetado",dato=empaquetado)
            bbdd.tbl_compra.actualiza_fila(id,columna="observaciones",dato=observaciones)
            bbdd.tbl_compra.actualiza_fila(id,columna="precio",dato=precio)


            bbdd.conn.commit()
            return redirect(url_for('compras'))
        return render_template('editar_compra.html',form=form, compra=compra)


# Crear la compra de un producto
@app.route('/<int:id>/compras', methods=['GET','POST'])
def comprar_producto(id):
    """
    Crea la compra de un producto

    Parametros:
    id: id del producto que vamos a comprar
    """
    print(">>>> Estoy en comprar_producto()")

    with tool.basedatos(DB_FILE) as bbdd:
        global supermercado_defecto
        producto = bbdd.tbl_producto.get_producto(id,"id")
        form = Compra_Form()
        # Relleno la lista desplegable con los supermercados de la base de datos
        form.supermercado.choices=[(g["id"],g["nombre"]) for g in bbdd.tbl_supermercado.saca_todo()]
        # Como opcion predeterminada ponemos un supermercado por defecto
        form.supermercado.default = supermercado_defecto
        #form.process()

        if form.validate_on_submit():
            print("Estoy en comprar_producto - form.validate_on_submit")
            supermercado = request.form['supermercado']
            fecha = request.form['fecha']
            empaquetado = request.form['empaquetado']
            observaciones = request.form['observaciones']
            precio = request.form['precio']
            print(f"Del formulario tengo {supermercado},{fecha} y {precio}")
            print(f"La fecha que has puesto es {fecha}")

            if supermercado != supermercado_defecto:
                supermercado_defecto=supermercado
                print(">>>>>>>>>>>>>>>> Cambiado supermercado por defecto a ",supermercado)

            # Separo la fecha tipo "2021-12-01" en año,mes y dia
            año,mes,dia = fecha.split("-")
            fecha_formateada = f"{año}-{mes}-{dia}"
            
            datos_columnas=("producto_id","supermercado_id","fecha","empaquetado","observaciones","precio")
            datos = (id,supermercado,fecha_formateada,empaquetado,observaciones,precio)

            print("***>>>> datos_columnas:",datos_columnas)
            print("***>>>> Datos:",datos)
            bbdd.tbl_compra.crea_fila(datos_columnas,datos)
            bbdd.conn.commit()

            return redirect(url_for('bd'))
     
        return render_template('comprar_producto.html', form=form, producto=producto)

# Borrar producto
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    """
    Borra un producto

    Parametros:
    id: Id del producto a borrar
    """
    
    with tool.basedatos(DB_FILE) as bbdd:
        bbdd.tbl_producto.borra_fila(id)
        bbdd.conn.commit()
        #flash('"{}" was succesfully deleted!'.format(producto["name"]))
        return redirect(url_for('index'))

# Borrar compra
@app.route('/<int:id>/borra_compra', methods=('POST','GET'))
def borra_compra(id):
    """
    Borra una compra

    Parametros:
    id: Id de la compra que vamos a borrar
    """

    print(f"Estoy en borra compra con id {id}")

    with tool.basedatos(DB_FILE) as bbdd:
        bbdd.tbl_compra.borra_fila(id)
        bbdd.conn.commit()
        #flash("La compra fue borrada")
        return redirect(url_for('index'))
 
# Para hacer pruebas
@app.route('/about',methods=['GET','POST'])
def about():
    """
    Pagina para pruebas
    """
    with tool.basedatos(DB_FILE) as bbdd:

        num_productos = len(bbdd.tbl_producto.saca_todo())
        info={"num_productos":num_productos}

        return render_template('about.html',info=info)



if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
    #app.run(host='0.0.0.0',port=5000)
