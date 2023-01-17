#!/usr/bin/env python3

from app import db,Producto,Supermercado,Compra
import os
from datetime import date


if os.path.exists("./basedatos.db"):
    print("La base datos existe")
    print("Productos:")

    qp = db.session.query(Producto).all()

    if qp:
        pass
        #print(qp)
    else:
        print("No hay productos. Creo un par")
        p1 = Producto(codigoBarras="123",name="Patatas",marca="Lays")
        p2 = Producto(codigoBarras="321",name="Chocolate",marca="Milka")
        db.session.add(p1,p2)
        db.session.commit()
        
    print("Supermercados:")
    qs = db.session.query(Supermercado).all()
    if qs:
        print(qs)
    else:
        print("No hay supermercados. Creo uno")
        s1 = Supermercado(nombre="Carre",direccion="Calle carre")
        db.session.add(s1)
        db.session.commit()

    print("Compras")
    qc = db.session.query(Compra).all()
    if qc:
        print(qc)
    else:
        print("No hay compras. Creo una")
        c1 = Compra(producto_id=1,supermercado_id=1,fecha=date(2021,2,21),precio="20")

        db.session.add(c1)
        db.session.commit()


else:
    print("La base datos NO existe, la creo nueva")
    db.create_all()
    
    
print(f"""
*******
* FIN *
******""")

q = db.session.query(Compra).filter(Compra.producto.name.like('%pat%')).first()
print(q)
print("Id:",q.id)
print("Nombre:",q.producto.name)
print("Marca:",q.producto.marca)
print("Supermercado:",q.supermercado.nombre)
print("Precio:",q.precio)
