#!/usr/bin/python3

""" 

Pagina web dinamica con flask que muestra una base de datos de productos de
supermercado. Se pueden borrar, editar y añadir nuevos productos


#######################################################################
#                                TODO                                 #
#######################################################################
- Mejorar la pagina index.html, meter un foto de un bodegon o algo  
- En nuevo producto, mejorar el ancho de los campos
- En nueva compra, mejorar la disposicion de los campos
- Posibilidad de crear nuevos supermercados
- Coger datos de es.openfoodfacts.org
- Que hagas una lista de compra virtual y te diga los productos que han subido de precio y los que han bajado. Por ejemplo para saber si las ofertas del 3x2 del Carrefour son reales o te estan timando
- Cuando haces una compra volver a pagina productos
- en lista_compras.html y lista_productos.html añadir boton para volver al principio de la pagina
- Boton subir para ir al inicio de pagina
- Boton de editar compra en la pagina de producto
- Ordenar lista_productos en modo descendente por id, de modo que los productos recien añadidos a la bbdd salgan primero

"""
import os
import logging
from datetime import date,datetime

from flask import Flask, render_template, request, url_for, flash, redirect
# from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import Form, StringField, IntegerField, DecimalField, SelectField,SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from utilidades_extra import tools_sqlite3 as tool
from utilidades_extra import carga_codigobarras as carga_codebar

from logging.config import dictConfig

app = Flask(__name__)
app.config['SECRET_KEY']='abcde'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basedatos.db'

DB_FILE = os.path.join(app.root_path,"basedatos.db")
UPLOAD_FOLDER = os.path.join(app.root_path,"static/images/")
LOG_FILE = os.path.join(app.root_path,"logs/superapp.log")
ALLOWED_EXTENSIONS = {'jpg','txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

supermercado_defecto = 2
#db = SQLAlchemy(app)
__version__ = "12-abril-2023"

app = Flask(__name__)
app.config['SECRET_KEY']='abcde'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basedatos.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


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
    logger.info(f"Hola desde index. Directorio app: {app.root_path}")
    return render_template('index.html',version=__version__) 
# Ver la lista de productos
# TODO: Pasar tambien el precio del producto:  <24-02-23, yourname> #
@app.route('/lista_productos',methods=['GET','POST'])
def bd():
    logger.info("Hola desde bd")
    with tool.basedatos(DB_FILE) as bbdd:

        # Se ha hecho una busqueda de un producto 
        if request.method == 'POST': 
            name = request.form['name'] 
            name = "%"+name+"%"
            dato2 = bbdd.tbl_producto.get_producto(name,"name")
            if dato2: # Aparecen resultados en la busqueda
                for prod in dato2:
                    ultimo_precio = 0
                    dato_compra = bbdd.tbl_compra.get_producto(prod["id"],"producto_id")
                    if dato_compra:
                        ultimo_precio = dato_compra[-1]["precio"]
                    prod.update({"ultimo_precio":ultimo_precio})
                return render_template('lista_productos.html',datos=dato2) 

             # La busqueda no da resultados
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

        # Se dan la vuelta a los datos para que se imprima primero los ultimos productos 
        dato_reverse = dato[::-1]
        
        for prod in dato:
            ultimo_precio = 0
            dato_compra = bbdd.tbl_compra.get_producto(prod["id"],"producto_id")
            if dato_compra:
                ultimo_precio = dato_compra[-1]["precio"]
            prod.update({"ultimo_precio":ultimo_precio})

        return render_template('lista_productos.html',datos=dato_reverse) 


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
            datos2 = bbdd.vista_compra.get_producto(name,"producto")
            if datos2:
                return render_template('lista_compras.html',datos=datos2) 
            else:
                print("NO HAY DATOS")

                #dato = db.session.query(Compra).all()
                dato = bbdd.vista_compra.saca_todo()
                return render_template('lista_compras.html',datos=dato)

        #dato = db.session.query(Compra).order_by("fecha").all()
        dato = bbdd.vista_compra.saca_todo()
        return render_template('lista_compras.html',datos=dato)
        
# Pagina del producto
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

# Subir archivo
@app.route('/<int:id>/upload_product_photo', methods=['GET', 'POST'])
def upload_file(id):
    logger.info("Hola desde upload_file")
    print(">>> Recibido id:",id)
    if request.method == 'POST':
        print(">>> id:",id)
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(">>> filename:",filename)
            nombre_fichero = str(id)+'.jpg'
            print(">>> ",nombre_fichero)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_fichero ))
            return redirect(url_for('producto',producto_id=id))
    return '''
<!doctype html>
    <title>Subir nuevo archivo</title>
    <h1>Subir nuevo archivo</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Subir>
    </form>
    '''


# Subir lista de codigos de barras
@app.route('/upload_codebars', methods=['GET', 'POST'])
def sube_codigosbarras():
    logger.info("Hola desde sube_codigosbarras")
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):

            nombre_fichero = 'lista_codigos_barras.txt'
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_fichero ))

            logger.debug(f">>> filename:{filename}")
            logger.debug(f">>> nombre_fichero:{nombre_fichero}")
            ruta_fichero = "./static/images/"+nombre_fichero
            lista_codigos = carga_codebar.lee_codigos(ruta_fichero)
            for codigo in lista_codigos:
                logger.debug(f"Comprobando codigo:{codigo}")
                if carga_codebar.existe_codebar(codigo,bbdd_file=DB_FILE):
                    logger.debug(f"El codigo -{codigo}- si existe en la bbdd")
                else:
                    logger.debug(f"El codigo -{codigo}- no existe en la bbdd. Cojo info de foodfacts")
                    datos = carga_codebar.get_foodfacts(codigo)

                    logger.debug(f"Info de foodfacts: {datos}")
                    if datos!=None:
                        carga_codebar.inserta_producto(carga_codebar.get_foodfacts(codigo),DB_FILE)


            return redirect(url_for('bd'))
    return '''
<!doctype html>
    <title>Subir nuevo archivo</title>
    <h1>Subir nuevo archivo</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Subir>
    </form>
    '''

# Para hacer pruebas
@app.route('/about',methods=['GET','POST'])
def about():
    """
    Pagina para pruebas
    """
    logger.info("Hola desde about")
    with tool.basedatos(DB_FILE) as bbdd:

        num_productos = len(bbdd.tbl_producto.saca_todo())
        info={"num_productos":num_productos}

        return render_template('about.html',info=info)



if __name__=='__main__':
    logging.basicConfig(filename=LOG_FILE,
            filemode='w',
            format='%(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

    # dictConfig({
    #     'version': 1,
    #     'formatters': {'default': { 'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s', }},
    #     'handlers': { "console": { "class": "logging.StreamHandler", "stream": "ext://sys.stdout", "formatter": "default", },
    #              "file": { "class": "logging.FileHandler", "filename": "./logs/superapp.log", "formatter": "default", },
    #                 },
    #     'root': { 'level': 'WARNING', 'handlers': ['console','file'] }
    #     })
    logger = logging.getLogger("main.py")
    app.run(host='0.0.0.0',port=5000, debug=True) # Con autorefresco
    # app.run(host='0.0.0.0',port=5000)

    logger.debug("""
    *** SUPERAPP ***
    *** Ejecutando main.py ***
    """)
    logger.debug(f"** {__version__} **")

