-- ==========================================
-- TABLA: productos
-- ==========================================
CREATE TABLE productos (
    id  SERIAL PRIMARY KEY,
    codigo_barra    VARCHAR(50) UNIQUE,
    nombre  VARCHAR(100) NOT NULL,
    categoria   VARCHAR(50) NOT NULL,
    unidad_medida   VARCHAR(10) NOT NULL CHECK(unidad_medida IN ('un','kg')),
    precio_venta    DECIMAL(10,2) NOT NULL,
    precio_costo    DECIMAL(10,2) NOT NULL,
    activo  BOOLEAN DEFAULT TRUE
);

-- ==========================================
-- TABLA: clientes
-- ==========================================
CREATE TABLE clientes (
    id  SERIAL PRIMARY KEY,
    nombre  VARCHAR(50) NOT NULL,
    activo  BOOLEAN DEFAULT TRUE
);

-- ==========================================
-- TABLA: inventario
-- ==========================================
CREATE TABLE inventario (
    id                SERIAL PRIMARY KEY,
    producto_id       INTEGER NOT NULL REFERENCES productos(id),
    cantidad          DECIMAL(10,3) NOT NULL DEFAULT 0,
    fecha_caducidad   DATE,
    fecha_ingreso     DATE NOT NULL DEFAULT CURRENT_DATE
);

-- ==========================================
-- TABLA: ventas
-- ==========================================
CREATE TABLE ventas (
    id          SERIAL PRIMARY KEY,
    fecha       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total       DECIMAL(10,2) NOT NULL DEFAULT 0,
    estado      VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'completada', 'cancelada')),
    cliente_id  INTEGER REFERENCES clientes(id)
);

-- ==========================================
-- TABLA: detalle_ventas
-- ==========================================
CREATE TABLE detalle_ventas (
    id                SERIAL PRIMARY KEY,
    venta_id          INTEGER NOT NULL REFERENCES ventas(id),
    producto_id       INTEGER NOT NULL REFERENCES productos(id),
    cantidad          DECIMAL(10,3) NOT NULL,
    precio_unitario   DECIMAL(10,2) NOT NULL,
    subtotal          DECIMAL(10,2) NOT NULL
);

-- ==========================================
-- TABLA: pagos_venta
-- ==========================================
CREATE TABLE pagos_venta (
    id          SERIAL PRIMARY KEY,
    venta_id    INTEGER NOT NULL REFERENCES ventas(id),
    metodo      VARCHAR(20) NOT NULL CHECK (metodo IN ('efectivo', 'tarjeta', 'credito')),
    monto       DECIMAL(10,2) NOT NULL
);

-- ==========================================
-- TABLA: cuentas_cobrar
-- ==========================================
CREATE TABLE cuentas_cobrar (
    id              SERIAL PRIMARY KEY,
    cliente_id      INTEGER NOT NULL REFERENCES clientes(id),
    venta_id        INTEGER NOT NULL REFERENCES ventas(id),
    monto_total     DECIMAL(10,2) NOT NULL,
    saldo           DECIMAL(10,2) NOT NULL,
    fecha           DATE NOT NULL DEFAULT CURRENT_DATE,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'pagada'))
);

-- ==========================================
-- TABLA: abonos
-- ==========================================
CREATE TABLE abonos (
    id                  SERIAL PRIMARY KEY,
    cuenta_cobrar_id    INTEGER NOT NULL REFERENCES cuentas_cobrar(id),
    monto               DECIMAL(10,2) NOT NULL,
    fecha               DATE NOT NULL DEFAULT CURRENT_DATE
);

-- ==========================================
-- TABLA: compras
-- ==========================================
CREATE TABLE compras (
    id          SERIAL PRIMARY KEY,
    proveedor   VARCHAR(100) NOT NULL,
    fecha       DATE NOT NULL DEFAULT CURRENT_DATE,
    total       DECIMAL(10,2) NOT NULL DEFAULT 0
);

-- ==========================================
-- TABLA: detalle_compras
-- ==========================================
CREATE TABLE detalle_compras (
    id              SERIAL PRIMARY KEY,
    compra_id       INTEGER NOT NULL REFERENCES compras(id),
    producto_id     INTEGER NOT NULL REFERENCES productos(id),
    cantidad        DECIMAL(10,3) NOT NULL,
    precio_costo    DECIMAL(10,2) NOT NULL,
    subtotal        DECIMAL(10,2) NOT NULL
);