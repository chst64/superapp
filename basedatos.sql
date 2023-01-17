PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE producto (
	id INTEGER NOT NULL, 
	"codigoBarras" INTEGER, 
	name VARCHAR(50), 
	marca VARCHAR(50), 
	envase VARCHAR(50), 
	cantidad FLOAT, 
	categoria INTEGER, 
	unidad VARCHAR(10), 
	puntuacion INTEGER, 
	PRIMARY KEY (id)
);
INSERT INTO producto VALUES(1,12345,'Patatas fritas','Lays','Bolsa de plastico',125.99999999999999999,NULL,'gramos',2);
INSERT INTO producto VALUES(2,1234,'Kit kat','Carrefour','bolsita',50.0,NULL,'gramos',5);
INSERT INTO producto VALUES(3,223344,'Tomate frito con aceite de oliva','Orlando','tetra brik',350.0,NULL,'gramos',4);
INSERT INTO producto VALUES(4,1111,'Patatas fritas onduladas','Carrefour','Bolsa de plastico',125.0,NULL,'gramos',2);
CREATE TABLE supermercado (
	id INTEGER NOT NULL, 
	nombre VARCHAR(50), 
	direccion VARCHAR(50), 
	PRIMARY KEY (id)
);
INSERT INTO supermercado VALUES(1,'Carre','Calle carre');
INSERT INTO supermercado VALUES(2,'Mercadona','Calle Rio Chico');
CREATE TABLE compra (
	id INTEGER NOT NULL, 
	producto_id INTEGER, 
	supermercado_id INTEGER, 
	fecha VARCHAR(15), 
	precio FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(producto_id) REFERENCES producto (id), 
	FOREIGN KEY(supermercado_id) REFERENCES supermercado (id)
);
INSERT INTO compra VALUES(1,1,2,'1/2/21',21.5);
INSERT INTO compra VALUES(2,2,1,'2021-08-07',123.0);
INSERT INTO compra VALUES(3,3,1,'2021-08-07',2.75);
INSERT INTO compra VALUES(4,3,1,'2021-08-08',2.0);
INSERT INTO compra VALUES(5,3,2,'2021-08-08',3.0);
INSERT INTO compra VALUES(6,3,2,'2021-08-08',3.1000000000000000888);
COMMIT;
