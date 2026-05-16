-- ════════════════════════════════════════════════════════
-- SCHEMA SUPABASE - MEDISTOCK
-- Ejecuta este script en el editor SQL de Supabase
-- ════════════════════════════════════════════════════════

-- ─── TABLA: ORDENES ───
-- Registro de pedidos/compras de usuarios y empresas
CREATE TABLE IF NOT EXISTS ordenes (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    usuario_id BIGINT,
    empresa_id BIGINT,
    estado TEXT DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente', 'pagada', 'enviada', 'completada', 'cancelada')),
    items JSONB NOT NULL,
    total_items INT DEFAULT 0,
    subtotal NUMERIC(10, 2) DEFAULT 0,
    iva NUMERIC(10, 2) DEFAULT 0,
    total NUMERIC(10, 2) DEFAULT 0,
    tipo_orden TEXT DEFAULT 'personal'
        CHECK (tipo_orden IN ('personal', 'empresa', 'usuario')),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_pago TIMESTAMP,
    metodo_pago TEXT DEFAULT 'transbank',

    -- Datos de envío
    direccion_envio TEXT,
    ciudad TEXT,
    region TEXT,
    telefono TEXT,
    codigo_postal TEXT,

    -- Transbank tracking
    transbank_token TEXT,
    transbank_order_id TEXT,
    transbank_authorization_code TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_ordenes_usuario_id ON ordenes(usuario_id);
CREATE INDEX IF NOT EXISTS idx_ordenes_empresa_id ON ordenes(empresa_id);
CREATE INDEX IF NOT EXISTS idx_ordenes_estado ON ordenes(estado);
CREATE INDEX IF NOT EXISTS idx_ordenes_fecha ON ordenes(fecha_creacion DESC);


-- ─── TABLA: COTIZACIONES ───
-- Cotizaciones generadas por empresas
CREATE TABLE IF NOT EXISTS cotizaciones (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    empresa_id BIGINT NOT NULL,
    estado TEXT DEFAULT 'solicitada'
        CHECK (estado IN ('solicitada', 'enviada', 'aceptada', 'rechazada', 'convertida')),
    items JSONB NOT NULL,
    total NUMERIC(10, 2) DEFAULT 0,
    subtotal NUMERIC(10, 2) DEFAULT 0,
    iva NUMERIC(10, 2) DEFAULT 0,
    fecha_solicitud TIMESTAMP DEFAULT NOW(),
    fecha_vencimiento TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days'),
    pdf_url TEXT,
    notas TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_cotizaciones_empresa ON cotizaciones(empresa_id);
CREATE INDEX IF NOT EXISTS idx_cotizaciones_estado ON cotizaciones(estado);


-- ─── TABLA: PRODUCTOS (verificar campos requeridos) ───
-- Si ya existe la tabla, agregar campos faltantes:
ALTER TABLE productos
    ADD COLUMN IF NOT EXISTS tipo_venta TEXT DEFAULT 'ambos'
        CHECK (tipo_venta IN ('personal', 'empresa', 'ambos', 'libre', 'receta'));

ALTER TABLE productos
    ADD COLUMN IF NOT EXISTS etiqueta_precio TEXT;

ALTER TABLE productos
    ADD COLUMN IF NOT EXISTS cantidad INT DEFAULT 0;


-- ─── POLÍTICAS RLS (Row Level Security) ───
-- Activar RLS en las tablas
ALTER TABLE ordenes ENABLE ROW LEVEL SECURITY;
ALTER TABLE cotizaciones ENABLE ROW LEVEL SECURITY;

-- Política: permitir lectura/escritura desde el cliente
-- NOTA: Para producción, ajustar políticas para mayor seguridad
CREATE POLICY "Lectura pública de ordenes" ON ordenes FOR SELECT USING (true);
CREATE POLICY "Insert público de ordenes" ON ordenes FOR INSERT WITH CHECK (true);

CREATE POLICY "Lectura pública de cotizaciones" ON cotizaciones FOR SELECT USING (true);
CREATE POLICY "Insert público de cotizaciones" ON cotizaciones FOR INSERT WITH CHECK (true);


-- ─── DATOS DE EJEMPLO (Opcional) ───
-- Descomentar para insertar productos de prueba:
/*
INSERT INTO productos (nombre, descripcion, precio, imagen_url, categoria, tipo_venta, etiqueta_precio, cantidad)
VALUES
    ('Silla de ruedas estándar', 'Silla de ruedas plegable de aluminio', 150000, 'https://via.placeholder.com/300', 'movilidad', 'ambos', 'OFERTA', 10),
    ('Mascarilla quirúrgica x100', 'Pack de 100 mascarillas triple capa', 8000, 'https://via.placeholder.com/300', 'insumos', 'ambos', 'POPULAR', 50),
    ('Tensiómetro digital', 'Tensiómetro automático de brazo', 35000, 'https://via.placeholder.com/300', 'equipos', 'personal', 'NUEVO', 15),
    ('Set quirúrgico básico', 'Set completo para cirugías menores', 250000, 'https://via.placeholder.com/300', 'equipos', 'empresa', 'PROFESIONAL', 5),
    ('Termómetro infrarrojo', 'Termómetro sin contacto', 25000, 'https://via.placeholder.com/300', 'equipos', 'ambos', NULL, 30);
*/
