#!/usr/bin/python3

""" 
Pagina web dinamica con flask que muestra una base de datos de productos de
supermercado. Se pueden borrar, editar y añadir nuevos productos

Para iniciar la base de datos:
    desde la consola python:
    from app.py import db
    db.create_all()

V2: Modificada para usar SQLAlchemy
V3: Modificada para tener bbdd de productos, de compras, ...

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
"""

from datetime import date,datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, DecimalField, SelectField,SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.exceptions import abort

import herramientas

app = Flask(__name__)
app.config['SECRET_KEY']='abcde'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basedatos.db'
DB_FILE = "./basedatos.db"

db = SQLAlchemy(app)


def get_producto(producto_id):
    
    producto = db.session.query(Producto).filter_by(id=producto_id).first()
    print("En get_producto el producto es",producto.name)
    return producto

def get_compra(compra_id):
    compra = db.session.query(Compra).filter_by(id=compra_id).first()
    print(f"En get_compra la compra es {compra.id}:{compra.producto.name}-{compra.supermercado.nombre} - {compra.precio}")
    return compra

def compras_producto(producto_id):
    compras_del_producto = db.session.query(Compra).filter_by

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
    puntuacion = DecimalField("Puntuacion")
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

# Tabla de productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigoBarras = db.Column(db.Integer)
    name = db.Column(db.String(50))
    marca = db.Column(db.String(50))
    #supermercado = db.Column(db.String(50))
    envase = db.Column(db.String(50))
    cantidad = db.Column(db.Float)
    categoria = db.Column(db.Integer)
    unidad = db.Column(db.String(10))
    #precio = db.Column(db.Float)
    puntuacion = db.Column(db.Integer)
    observaciones = db.Column(db.String(75)) # Campo nuevo
    compras = db.relationship('Compra',backref='producto') 

    def __repr__(self):
        return f'Producto:{self.name} de la marca {self.marca} '

# Tabla de Supermercados
class Supermercado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    direccion = db.Column(db.String(50))
    compras = db.relationship('Compra',backref='supermercado')

    def __repr__(self):
        return f'Super:{self.nombre} en la direccion {self.direccion} '

# *** Tabla de compras ***
class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    supermercado_id = db.Column(db.Integer, db.ForeignKey('supermercado.id'))
    fecha = db.Column(db.Date)
    empaquetado = db.Column(db.String(20)) # Campo nuevo
    observaciones = db.Column(db.String(75)) # Campo nuevo
    precio = db.Column(db.Float)

    def __repr__(self):
        return f'Compras:{self.producto_id} {self.supermercado_id} {self.precio}'

# ******************
# Rutas
# ******************

@app.route('/')
def index():
    return render_template('index.html') 

# Ver la lista de productos
@app.route('/lista_productos',methods=['GET','POST'])
def bd():
    print("*** Estoy en bd ***")
    if request.method == 'POST':
        name = request.form['name'] 
        name = "%"+name+"%"
        dato2 = Producto.query.filter(Producto.name.like(name)).all()
        if dato2:
            return render_template('lista_productos.html',datos=dato2) 
        else:
            print("NO HAY DATOS")
            
            dato = db.session.query(Producto).all()
            return render_template('lista_productos.html',datos=dato) 

    dato = db.session.query(Producto).order_by("name").all()
    return render_template('lista_productos.html',datos=dato) 


# Ver la lista de compras 
@app.route('/lista_compras',methods=['GET','POST'])
def compras():
    print("*** Estoy en compras ***")
    if request.method == 'POST':
        name = request.form['name']
        name = "%" + name + "%"
        print("Tengo",name)
        #dato2 = Compra.query.filter(Compra.producto.name.like(name)).all()
        dato2 = Compra.query.join(Producto).filter(Producto.name.like(name)).all()
        if dato2:
            return render_template('lista_compras.html',datos=dato2) 
        else:
            print("NO HAY DATOS")

            dato = db.session.query(Compra).all()
            return render_template('lista_compras.html',datos=dato)

    dato = db.session.query(Compra).order_by("fecha").all()
    return render_template('lista_compras.html',datos=dato)
        
# Informacion de un producto
@app.route('/<int:producto_id>')
def producto(producto_id):
    producto = get_producto(producto_id)
    if producto!=None:
        compras = db.session.query(Compra).filter_by(producto_id = producto.id).all()

    return render_template('producto.html',producto=producto, compras=compras)

# Crear producto nuevo
@app.route('/create',methods=['GET','POST'])
def create2():
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

        
        item = Producto(codigoBarras=codigoBarras,
                name=name,
                marca=marca,
                envase=envase,
                cantidad=cantidad,
                unidad=unidad,
                #precio=precio,
                puntuacion=puntuacion,
                observaciones= observaciones)

        db.session.add(item)
        db.session.commit()
        return redirect(url_for('bd'))
        

    return render_template('create.html',form=form)

# Editar producto
@app.route('/<int:id>/edit', methods=['GET','POST'])
def edit(id):
    producto = get_producto(id)
 
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
            producto.codigoBarras = codigoBarras
            producto.name = name
            producto.marca = marca
            #producto.supermercado = supermercado
            producto.envase = envase
            producto.cantidad = cantidad
            producto.unidad = unidad
            #producto.precio = precio
            producto.puntuacion = puntuacion
            producto.observaciones = observaciones
            db.session.commit()
            return redirect(url_for('bd'))

    return render_template('edit.html', producto=producto)

# Editar compra
@app.route('/compra/<int:id>', methods=['GET','POST'])
def editar_compra(id):
    """print("Estoy en editar_compra y tengo que editar la compra ",id)
    compra = get_compra(id)
 
    if request.method == 'POST':
        supermercado = request.form['supermercado']
        fecha = request.form['fecha']
        precio = request.form['precio']

        # Separo la fecha tipo "2021-12-01" en año,mes y dia
        año,mes,dia = fecha.split("-")

        if not supermercado:
            flash('Se necesita supermercado')

        # Si tengo el valor de supermercado, modifico los datos de "compra"
        else:
            compra.supermercado_id = supermercado

            # Convierto los datos de la fecha en datetime
            compra.fecha = date(int(año),int(mes),int(dia))

            compra.precio = precio
            db.session.commit()
            return redirect(url_for('lista_compras'))

    return render_template('editar_compra.html', compra=compra)
    """
    compra = get_compra(id)

    form = Edit_Compra_Form()

    # Relleno la lista desplegable con los supermercados de la base de datos

    form.supermercado.choices=[(g.id,g.nombre) for g in Supermercado.query.order_by('nombre')]

    if form.validate_on_submit():
        fecha = request.form['fecha']
        supermercado = request.form['supermercado']

        empaquetado = request.form['empaquetado']
        observaciones = request.form['observaciones']
        precio = request.form['precio']

        # Separo la fecha tipo "2021-12-01" en año,mes y dia
        año,mes,dia = fecha.split("-")
        
        compra.supermercado_id=supermercado
                #fecha=datetime.today(),
                # Convierto los datos de la fecha en datetime
        compra.fecha=date(int(año),int(mes),int(dia))
                #fecha=fecha,
        compra.empaquetado=empaquetado
        compra.observaciones=observaciones
        compra.precio=precio

        db.session.commit()
        return redirect(url_for('compras'))
    return render_template('editar_compra.html',form=form, compra=compra)


# Crear la compra de un producto
@app.route('/<int:id>/compras', methods=['GET','POST'])
def comprar_producto(id):
    producto = get_producto(id)
    form = Compra_Form()
    # Relleno la lista desplegable con los supermercados de la base de datos
    form.supermercado.choices=[(g.id,g.nombre) for g in Supermercado.query.order_by('nombre')]

    if form.validate_on_submit():
        print("Estoy en comprar_producto - form.validate_on_submit")
        supermercado = request.form['supermercado']
        fecha = request.form['fecha']
        empaquetado = request.form['empaquetado']
        observaciones = request.form['observaciones']
        precio = request.form['precio']
        print(f"Del formulario tengo {supermercado},{fecha} y {precio}")
        print(f"La fecha que has puesto es {fecha}")

        # Separo la fecha tipo "2021-12-01" en año,mes y dia
        año,mes,dia = fecha.split("-")
        
        item = Compra(producto_id=id,
                supermercado_id=supermercado,
                #fecha=datetime.today(),
                # Convierto los datos de la fecha en datetime
                fecha=date(int(año),int(mes),int(dia)),
                #fecha=fecha,
                empaquetado=empaquetado,
                observaciones=observaciones,
                precio=precio)

        db.session.add(item)
        db.session.commit()
        return redirect(url_for('bd'))
 
    return render_template('comprar_producto.html', form=form, producto=producto)

# Borrar producto
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    producto = get_producto(id)
    db.session.delete(producto)
    db.session.commit()
    flash('"{}" was succesfully deleted!'.format(producto.name))
    return redirect(url_for('index'))

# Borrar compra
@app.route('/<int:id>/borra_compra', methods=('POST','GET'))
def borra_compra(id):
    print(f"Estoy en borra compra con id {id}")
    compra = get_compra(id)
    db.session.delete(compra)
    db.session.commit()
    flash("La compra fue borrada")
    return redirect(url_for('index'))
 
# Para hacer pruebas
@app.route('/about',methods=['GET','POST'])
def about():
    if request.method == 'POST':
        name = request.form['name'] 
        name = "%"+name+"%"
        print("****** \n Pasados ",name)
        dato2 = Producto.query.filter(Producto.name.like(name)).first()
        if dato2:
            print(f"""
            Nombre producto: {dato2.name}
            Marca producto: {dato2.marca}
            """)
        else:
            print("NO HAY DATOS")

    producto = db.session.query(Producto).all()
    compra = db.session.query(Compra).all()
    return render_template('about.html', dato=producto, compra=compra)



if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)
    #app.run(host='0.0.0.0',port=5000)
