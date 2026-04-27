import psycopg2
import streamlit as st
from datetime import datetime, date
import unicodedata
import re
import hashlib

from psycopg2 import pool

# 🔥 POOL DE CONEXIONES GLOBAL
connection_pool = pool.SimpleConnectionPool(
    1, 10,  # mínimo 1, máximo 10 conexiones
    st.secrets["DATABASE_URL"]
)
   
def conectar():
    return connection_pool.getconn()



def limpiar_cedula(cedula):
    return re.sub(r'\D', '', cedula)

def limpiar_nombre(texto):
    texto = texto.strip().lower()
    texto = re.sub(r'\s+', ' ', texto)  # quitar espacios extra
    return texto.title()

def normalizar_item(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def crear_tablas():

    conn = conectar()
    cursor = conn.cursor()
    
    

    # ======================
    # SEDES
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sedes (
        id SERIAL PRIMARY KEY,
        nombre TEXT,
        ciudad TEXT
    )
    """)

    # ======================
    # TIPOS DE MAQUINA
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipos_maquina (
        id SERIAL PRIMARY KEY,
        nombre TEXT UNIQUE
    )
    """)

    # ======================
    # MAQUINAS (MEJORADA)
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maquinas (
        id SERIAL PRIMARY KEY,
        tipo TEXT,
        activo_fijo TEXT UNIQUE,
        numero_equipo TEXT,
        modelo TEXT,
        fabricante TEXT,
        anio INTEGER,
        estado_operacion TEXT,
        sede_id INTEGER,
        fecha_registro DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (sede_id) REFERENCES sedes(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traslados (
        id SERIAL PRIMARY KEY,
        maquina_id INTEGER,
        sede_origen INTEGER,
        sede_destino INTEGER,
        fecha DATE,
        responsable TEXT,
        observaciones TEXT,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
        FOREIGN KEY (sede_origen) REFERENCES sedes(id),
        FOREIGN KEY (sede_destino) REFERENCES sedes(id)
    )
    """)

    # ======================
    # CHECKLISTS
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklists (
        id SERIAL PRIMARY KEY,
        maquina_id INTEGER,
        fecha DATE,
        origen TEXT,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
    )
    """)
    
    # 🔥 Agregar columna origen si no existe
    #try:
        #cursor.execute("ALTER TABLE checklists ADD COLUMN origen TEXT")
    #except:
        #pass    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklist_items (
        id SERIAL PRIMARY KEY,
        checklist_id INTEGER,
        item TEXT,
        cumple INTEGER,
        observaciones TEXT,
        FOREIGN KEY (checklist_id) REFERENCES checklists(id)
    )
    """)
    
    # ======================
    # CHECKLIST DINÁMICO 🔥
    # ======================

    # 🟦 Categorías
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias_checklist (
        id SERIAL PRIMARY KEY,
        nombre TEXT,
        tipo_maquina TEXT,
        orden INTEGER
    )
    """)

    # 🟩 Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items_checklist (
        id SERIAL PRIMARY KEY,
        categoria_id INTEGER,
        nombre TEXT,
        activo BOOLEAN DEFAULT TRUE,
        orden INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categorias_checklist(id)
    )
    """)

    # 🟨 Relación con histórico (NO rompe nada)
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='checklist_items'
                AND column_name='item_id'
            ) THEN
                ALTER TABLE checklist_items ADD COLUMN item_id INTEGER;
            END IF;
        END
        $$;
    """)

    # ======================
    # SOLICITUDES (MEJORADA)
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitudes_mantenimiento (
        id SERIAL PRIMARY KEY,
        maquina_id INTEGER,
        fecha DATE,
        item_falla TEXT,
        descripcion_falla TEXT,
        origen TEXT,
        estado TEXT,
        prioridad TEXT DEFAULT 'Media',
        veces_detectada INTEGER DEFAULT 1,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
    )
    """)

    # ======================
    # MANTENIMIENTOS (PRO)
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mantenimientos (
        id SERIAL PRIMARY KEY,
        maquina_id INTEGER,
        fecha DATE,
        tipo TEXT,
        tecnico TEXT,
        recibido_por TEXT,
        tiempo_paro REAL,
        observaciones TEXT,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
    )
    """)

    # ======================
    # COSTOS 🔥
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS costos_mantenimiento (
        id SERIAL PRIMARY KEY,
        mantenimiento_id INTEGER,
        tipo_costo TEXT,
        descripcion TEXT,
        cantidad REAL,
        costo_unitario REAL,
        costo_total REAL,
        FOREIGN KEY (mantenimiento_id) REFERENCES mantenimientos(id)
    )
    """)

    # ======================
    # RELACION MANTENIMIENTO - SOLICITUD
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mantenimiento_solicitudes (
        id SERIAL PRIMARY KEY,
        mantenimiento_id INTEGER,
        solicitud_id INTEGER,
        FOREIGN KEY (mantenimiento_id) REFERENCES mantenimientos(id),
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_mantenimiento(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial_estado_maquina (
        id SERIAL PRIMARY KEY,
        maquina_id INTEGER NOT NULL,
        estado TEXT NOT NULL,
        fecha DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
    )
    """)

    conn.commit()
    connection_pool.putconn(conn) 
    
    
#---------------------
#USUARIOS
def crear_tabla_usuarios():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)

    conn.commit()
    connection_pool.putconn(conn)
    
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
  
def crear_usuario(usuario, password, rol):

    conn = conectar()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
    INSERT INTO usuarios (usuario, password, rol)
    VALUES (%s, %s, %s)
    """, (usuario, password_hash, rol))

    conn.commit()
    connection_pool.putconn(conn)  
  
def validar_usuario(usuario, password):

    conn = conectar()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
    SELECT rol FROM usuarios
    WHERE usuario = %s AND password = %s
    """, (usuario, password_hash))

    resultado = cursor.fetchone()

    connection_pool.putconn(conn)

    return resultado[0] if resultado else None  
  
def obtener_usuarios():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id, usuario, rol FROM usuarios")

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos  
  
def eliminar_usuario(usuario_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))

    conn.commit()
    connection_pool.putconn(conn)
    
def actualizar_usuario(usuario_id, nuevo_password=None, nuevo_rol=None):

    conn = conectar()
    cursor = conn.cursor()

    if nuevo_password:
        password_hash = hash_password(nuevo_password)
        cursor.execute("""
        UPDATE usuarios SET password = %s WHERE id = %s
        """, (password_hash, usuario_id))

    if nuevo_rol:
        cursor.execute("""
        UPDATE usuarios SET rol = %s WHERE id = %s
        """, (nuevo_rol, usuario_id))

    conn.commit()
    connection_pool.putconn(conn)  



#---------------------
#MAQUINAS

def insertar_maquina(tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id):

    conn = conectar()
    cursor = conn.cursor()

    activo_fijo = activo_fijo.strip().upper()

    cursor.execute("""
    INSERT INTO maquinas 
    (tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    RETURNING id
    """, (tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id))

    maquina_id = cursor.fetchone()[0]

    conn.commit()
    connection_pool.putconn(conn)

    return maquina_id

def obtener_maquinas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        maquinas.id,
        maquinas.activo_fijo,
        maquinas.tipo,
        maquinas.numero_equipo,
        maquinas.modelo,
        maquinas.fabricante,
        maquinas.estado_operacion,
        sedes.nombre,
        sedes.ciudad
    FROM maquinas
    LEFT JOIN sedes ON maquinas.sede_id = sedes.id
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_maquina_por_id(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        maquinas.id,
        maquinas.tipo,
        maquinas.numero_equipo,
        maquinas.modelo,
        maquinas.fabricante,
        maquinas.estado_operacion,
        maquinas.sede_id,
        sedes.nombre,
        sedes.ciudad
    FROM maquinas
    LEFT JOIN sedes ON maquinas.sede_id = sedes.id
    WHERE maquinas.id = %s
    """, (maquina_id,))

    maquina = cursor.fetchone()

    connection_pool.putconn(conn)

    return maquina

def eliminar_maquina(id_maquina):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM maquinas WHERE id = %s", (id_maquina,))

    conn.commit()
    connection_pool.putconn(conn)

def actualizar_maquina(id, tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id):

    conn = conectar()
    cursor = conn.cursor()

    activo_fijo = activo_fijo.strip().upper()

    cursor.execute("""
    UPDATE maquinas
    SET tipo = %s, activo_fijo = %s, numero_equipo = %s, modelo = %s, fabricante = %s, estado_operacion = %s, sede_id = %s
    WHERE id = %s
    """, (tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id, id))

    conn.commit()
    connection_pool.putconn(conn)

def conteo_maquinas_por_sede():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        sedes.ciudad,
        sedes.nombre,
        COUNT(maquinas.id)
    FROM sedes
    LEFT JOIN maquinas ON maquinas.sede_id = sedes.id
    GROUP BY sedes.id
    ORDER BY sedes.ciudad
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_tipos_maquina():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT tipo FROM maquinas ORDER BY tipo")
    data = [row[0] for row in cursor.fetchall()]

    connection_pool.putconn(conn)
    return data

#---------------------
#SEDES
def insertar_sede(nombre, ciudad):

    conn = conectar()
    cursor = conn.cursor()
    
    # 🔥 LIMPIEZA CLAVE
    nombre = nombre.strip()
    ciudad = ciudad.strip().title()

    cursor.execute("""
    INSERT INTO sedes (nombre, ciudad)
    VALUES (%s, %s)
    """, (nombre, ciudad))

    conn.commit()
    connection_pool.putconn(conn)

def obtener_sedes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sedes")

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_sedes_diff():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT nombre FROM sedes ORDER BY nombre")
    data = [row[0] for row in cursor.fetchall()]

    connection_pool.putconn(conn)
    return data

def sede_tiene_maquinas(sede_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM maquinas
    WHERE sede_id = %s
    """, (sede_id,))

    cantidad = cursor.fetchone()[0]

    connection_pool.putconn(conn)

    return cantidad

def eliminar_sede(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sedes WHERE id = %s", (id,))

    conn.commit()
    connection_pool.putconn(conn)

#---------------------
# TRASLADOS
def insertar_traslado(maquina_id, sede_origen, sede_destino, fecha, responsable, observaciones):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO traslados (maquina_id, sede_origen, sede_destino, fecha, responsable, observaciones)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (maquina_id, sede_origen, sede_destino, fecha, responsable, observaciones))

    # actualizar sede actual de la máquina
    cursor.execute("""
    UPDATE maquinas
    SET sede_id = %s
    WHERE id = %s
    """, (sede_destino, maquina_id))

    conn.commit()
    connection_pool.putconn(conn)

def obtener_traslados():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        traslados.id,
        maquinas.numero_equipo,
        s1.nombre,
        s2.nombre,
        traslados.fecha,
        traslados.responsable,
        traslados.observaciones
    FROM traslados
    LEFT JOIN maquinas ON traslados.maquina_id = maquinas.id
    LEFT JOIN sedes s1 ON traslados.sede_origen = s1.id
    LEFT JOIN sedes s2 ON traslados.sede_destino = s2.id
    ORDER BY traslados.fecha DESC
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_ultimos_traslados(limit=10):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.tipo || ' - ' || m.numero_equipo,
        s1.ciudad,
        s1.nombre,
        s2.ciudad,
        s2.nombre,
        t.fecha,
        t.responsable
    FROM traslados t
    LEFT JOIN maquinas m ON t.maquina_id = m.id
    LEFT JOIN sedes s1 ON t.sede_origen = s1.id
    LEFT JOIN sedes s2 ON t.sede_destino = s2.id
    ORDER BY t.fecha DESC
    LIMIT %s
    """, (limit,))

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos

#---------------------
# REGISTRO DE CHECKLISTS
def insertar_checklist(maquina_id, fecha, origen, operario_id=None):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checklists (maquina_id, fecha, origen, operario_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (maquina_id, fecha, origen, operario_id))

    checklist_id = cursor.fetchone()[0]

    conn.commit()
    connection_pool.putconn(conn)

    return checklist_id

def insertar_item_checklist(checklist_id, item, cumple, observaciones, item_id=None):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checklist_items 
        (checklist_id, item, cumple, observaciones, item_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (checklist_id, item, cumple, observaciones, item_id))

    conn.commit()
    connection_pool.putconn(conn)
    
def obtener_checklists():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.id,
            m.tipo,
            m.activo_fijo,
            m.numero_equipo,
            c.fecha
        FROM checklists c
        JOIN maquinas m ON c.maquina_id = m.id
        ORDER BY c.fecha DESC
    """)

    checklists = cursor.fetchall()

    connection_pool.putconn(conn)

    return checklists

def obtener_ultimos_checklists_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.id,
            m.tipo,
            m.activo_fijo,
            m.numero_equipo,
            c.fecha,
            SUM(CASE WHEN ci.cumple = 0 THEN 1 ELSE 0 END) as fallas
        FROM checklists c
        LEFT JOIN checklist_items ci ON c.id = ci.checklist_id
        LEFT JOIN maquinas m ON c.maquina_id = m.id
        WHERE c.maquina_id = %s
        GROUP BY c.id
        ORDER BY c.fecha DESC, c.id DESC
        LIMIT 5
    """, (maquina_id,))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_items_checklist(checklist_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item, cumple, observaciones
        FROM checklist_items
        WHERE checklist_id = %s
    """, (checklist_id,))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def eliminar_checklist(checklist_id):

    conn = conectar()
    cursor = conn.cursor()

    # Primero eliminar los items de la checklist
    cursor.execute("""
        DELETE FROM checklist_items
        WHERE checklist_id = %s
    """, (checklist_id,))

    # Luego eliminar la checklist
    cursor.execute("""
        DELETE FROM checklists
        WHERE id = %s
    """, (checklist_id,))

    conn.commit()
    connection_pool.putconn(conn)

def obtener_ultimos_checklists(limit=10):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        c.id,
        m.tipo,
        m.activo_fijo,
        m.numero_equipo,
        c.fecha,
        (
            SELECT COUNT(*) 
            FROM checklist_items 
            WHERE checklist_id = c.id AND cumple = 0
        ) as fallas
    FROM checklists c
    JOIN maquinas m ON c.maquina_id = m.id
    ORDER BY c.fecha DESC
    LIMIT %s
    """, (limit,))

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return data

def obtener_checklists_por_ciudad(ciudad):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        c.id,
        m.tipo,
        m.activo_fijo,
        m.numero_equipo,
        c.fecha,
        (
            SELECT COUNT(*) 
            FROM checklist_items 
            WHERE checklist_id = c.id AND cumple = 0
        ) as fallas
    FROM checklists c
    JOIN maquinas m ON c.maquina_id = m.id
    JOIN sedes s ON m.sede_id = s.id
    WHERE s.ciudad = %s
    ORDER BY c.fecha DESC
    LIMIT 10
    """, (ciudad,))

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return data

def obtener_checklists_por_sede(sede):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        c.id,
        m.tipo,
        m.activo_fijo,
        m.numero_equipo,
        c.fecha,
        (
            SELECT COUNT(*) 
            FROM checklist_items 
            WHERE checklist_id = c.id AND cumple = 0
        ) as fallas
    FROM checklists c
    JOIN maquinas m ON c.maquina_id = m.id
    JOIN sedes s ON m.sede_id = s.id
    WHERE s.nombre = %s
    ORDER BY c.fecha DESC
    LIMIT 10
    """, (sede,))

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return data

# EDICION DE CHECKLISTS
def obtener_categorias(tipo_maquina):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre
        FROM categorias_checklist
        WHERE tipo_maquina = %s
        ORDER BY orden ASC
    """, (tipo_maquina,))

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return [{"id": d[0], "nombre": d[1]} for d in data]

def obtener_items(categoria_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre
        FROM items_checklist
        WHERE categoria_id = %s AND activo = TRUE
        ORDER BY orden ASC
    """, (categoria_id,))

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return [{"id": d[0], "nombre": d[1]} for d in data]

def crear_categoria(nombre, tipo_maquina, orden):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO categorias_checklist (nombre, tipo_maquina, orden)
        VALUES (%s, %s, %s)
    """, (nombre, tipo_maquina, orden))

    conn.commit()
    connection_pool.putconn(conn)

def crear_item(categoria_id, nombre, orden):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items_checklist (categoria_id, nombre, orden)
        VALUES (%s, %s, %s)
    """, (categoria_id, nombre, orden))

    conn.commit()
    connection_pool.putconn(conn)
    
def editar_item(item_id, nuevo_nombre):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items_checklist
        SET nombre = %s
        WHERE id = %s
    """, (nuevo_nombre, item_id))

    conn.commit()
    connection_pool.putconn(conn)   
    
def desactivar_item(item_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items_checklist
        SET activo = FALSE
        WHERE id = %s
    """, (item_id,))

    conn.commit()
    connection_pool.putconn(conn)
    
def actualizar_orden_item(item_id, nuevo_orden):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items_checklist
        SET orden = %s
        WHERE id = %s
    """, (nuevo_orden, item_id))

    conn.commit()
    connection_pool.putconn(conn)    

def obtener_checklists_paginados(limit, offset):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.fecha, c.maquina_id
        FROM checklists c
        ORDER BY c.id DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return data

def contar_checklists():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM checklists")
    total = cursor.fetchone()[0]

    connection_pool.putconn(conn)
    return total 

def obtener_detalle_checklist(checklist_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item, cumple, observaciones
        FROM checklist_items
        WHERE checklist_id = %s
    """, (checklist_id,))

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return data

def obtener_checklists_filtrados(limit, offset, fecha_inicio=None, fecha_fin=None, tipo_maquina=None, maquina_id=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT c.id, c.fecha, c.maquina_id
        FROM checklists c
        JOIN maquinas m ON c.maquina_id = m.id
        WHERE 1=1
    """

    params = []

    # Filtro por fecha
    if fecha_inicio and fecha_fin:
        query += " AND c.fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])

    # Filtro por tipo de máquina
    if tipo_maquina:
        query += " AND m.tipo = %s"
        params.append(tipo_maquina)

    # Filtro por máquina específica
    if maquina_id:
        query += " AND c.maquina_id = %s"
        params.append(maquina_id)

    # Orden + paginación
    query += " ORDER BY c.id DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    connection_pool.putconn(conn)
    return data

def contar_checklists_filtrados(fecha_inicio=None, fecha_fin=None, tipo_maquina=None, maquina_id=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT COUNT(*)
        FROM checklists c
        JOIN maquinas m ON c.maquina_id = m.id
        WHERE 1=1
    """

    params = []

    # Filtro por fecha
    if fecha_inicio and fecha_fin:
        query += " AND c.fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])

    # Filtro por tipo de máquina
    if tipo_maquina:
        query += " AND m.tipo = %s"
        params.append(tipo_maquina)

    # Filtro por máquina específica
    if maquina_id:
        query += " AND c.maquina_id = %s"
        params.append(maquina_id)

    cursor.execute(query, tuple(params))
    total = cursor.fetchone()[0]

    connection_pool.putconn(conn)
    return total   

def obtener_checklists_export(fecha_inicio=None, fecha_fin=None, tipo_maquina=None, maquina_id=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT 
            c.id,
            c.fecha,
            m.tipo,
            m.numero_equipo,
            s.ciudad,
            s.nombre
        FROM checklists c
        JOIN maquinas m ON c.maquina_id = m.id
        LEFT JOIN sedes s ON m.sede_id = s.id
        WHERE 1=1
    """

    params = []

    if fecha_inicio and fecha_fin:
        query += " AND c.fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])

    if tipo_maquina:
        query += " AND m.tipo = %s"
        params.append(tipo_maquina)

    if maquina_id:
        query += " AND c.maquina_id = %s"
        params.append(maquina_id)

    query += " ORDER BY c.fecha DESC"

    cursor.execute(query, tuple(params))
    checklists = cursor.fetchall()

    # 🔥 Obtener detalles
    resultado = []

    for c in checklists:

        checklist_id = c[0]

        cursor.execute("""
            SELECT item, cumple, observaciones
            FROM checklist_items
            WHERE checklist_id = %s
        """, (checklist_id,))

        items = cursor.fetchall()

        no_conformes = [(i[0], i[2]) for i in items if i[1] == 0]

        if not no_conformes:
            resumen = "Sin no conformidades"
        else:
            lista_items = [i[0] for i in no_conformes]
            resumen = f"{len(no_conformes)} fallas: " + ", ".join(lista_items)

        resultado.append((
            c[1],  # fecha
            f"{c[2]} {c[3]}",  # maquina
            c[4],  # ciudad
            c[5],  # sede
            resumen
        ))

    connection_pool.putconn(conn)
    return resultado

def existe_checklist_dia(maquina_id, fecha):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 1
    FROM checklists
    WHERE maquina_id = %s
    AND fecha = %s
    LIMIT 1
    """, (maquina_id, fecha))

    existe = cursor.fetchone()

    connection_pool.putconn(conn)

    return existe is not None



    
#---------------------
# SOLICITUDES DE MANTENIMIENTO
def solicitud_pendiente_existente(maquina_id, descripcion):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM solicitudes_mantenimiento
        WHERE maquina_id = %s
        AND descripcion_falla = %s
        AND estado = 'Pendiente'
    """, (maquina_id, descripcion))

    resultado = cursor.fetchone()

    connection_pool.putconn(conn)

    return resultado is not None

def insertar_solicitud(maquina_id, item_falla, observacion, origen):

    conn = conectar()
    cursor = conn.cursor()
    
    item_falla_normalizado = normalizar_item(item_falla)

    # Buscar si ya existe solicitud pendiente para ese item
    cursor.execute("""
    SELECT id, veces_detectada
    FROM solicitudes_mantenimiento
    WHERE maquina_id = %s
    AND LOWER(item_falla) = %s
    AND estado = 'Pendiente'
    """, (maquina_id, item_falla_normalizado))

    solicitud = cursor.fetchone()

    # Si ya existe → aumentar contador
    if solicitud:

        solicitud_id = solicitud[0]
        veces = solicitud[1] + 1

        cursor.execute("""
        UPDATE solicitudes_mantenimiento
        SET veces_detectada = %s
        WHERE id = %s
        """, (veces, solicitud_id))

        conn.commit()
        connection_pool.putconn(conn)

        return False, veces

    # Si no existe → crear nueva solicitud
    else:

        descripcion = f"{item_falla} - {observacion}"

        cursor.execute("""
        INSERT INTO solicitudes_mantenimiento
        (maquina_id, fecha, item_falla, descripcion_falla, origen, estado, veces_detectada)
        VALUES (%s, CURRENT_DATE, %s, %s, %s, 'Pendiente', 1)
        """, (maquina_id, item_falla_normalizado, descripcion, origen))

        conn.commit()
        connection_pool.putconn(conn)

        return True, 1

def obtener_solicitudes_pendientes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        s.id,
        m.numero_equipo,
        m.tipo,
        s.descripcion_falla,
        s.estado
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    WHERE s.estado = 'Pendiente'
    ORDER BY s.id DESC
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def cerrar_solicitud(solicitud_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE solicitudes_mantenimiento
    SET estado = 'Cerrada'
    WHERE id = %s
    """, (solicitud_id,))

    conn.commit()
    connection_pool.putconn(conn)

def obtener_todas_solicitudes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        s.id,
        m.numero_equipo,
        m.tipo,
        s.descripcion_falla,
        s.veces_detectada,
        s.origen,
        s.fecha,
        s.estado
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    ORDER BY s.id DESC
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_solicitudes_pendientes_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        item_falla,
        MAX(veces_detectada)
    FROM solicitudes_mantenimiento
    WHERE maquina_id = %s
    AND estado = 'Pendiente'
    GROUP BY item_falla
    """, (maquina_id,))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def actualizar_estado_por_solicitudes(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM solicitudes_mantenimiento
    WHERE maquina_id = %s
    AND estado = 'Pendiente'
    """, (maquina_id,))

    pendientes = cursor.fetchone()[0]

    if pendientes > 0:
        nuevo_estado = "Operativa con falla"
    else:
        nuevo_estado = "Operativa"

    cursor.execute("""
    UPDATE maquinas
    SET estado_operacion = %s
    WHERE id = %s
    """, (nuevo_estado, maquina_id))

    conn.commit()
    connection_pool.putconn(conn)

def actualizar_estado_maquina(maquina_id, nuevo_estado):

    conn = conectar()
    cursor = conn.cursor()

    # Obtener estado actual
    cursor.execute("""
    SELECT estado_operacion
    FROM maquinas
    WHERE id = %s
    """, (maquina_id,))

    estado_actual = cursor.fetchone()[0]

    # Solo registrar si el estado cambia
    if estado_actual != nuevo_estado:

        cursor.execute("""
        UPDATE maquinas
        SET estado_operacion = %s
        WHERE id = %s
        """, (nuevo_estado, maquina_id))

        cursor.execute("""
        INSERT INTO historial_estado_maquina (maquina_id, estado, fecha)
        VALUES (%s, %s, CURRENT_DATE)
        """, (maquina_id, nuevo_estado))

    conn.commit()
    connection_pool.putconn(conn)

def obtener_solicitudes_filtradas(ciudad=None, sede=None, tipo=None, maquina=None, pagina=1, limite=15):

    conn = conectar()
    cursor = conn.cursor()

    offset = (pagina - 1) * limite

    query = """
    SELECT 
        s.id,
        m.numero_equipo,
        m.tipo,
        s.descripcion_falla,
        s.veces_detectada,
        s.origen,
        s.fecha,
        s.estado
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    LEFT JOIN sedes sd ON m.sede_id = sd.id
    WHERE 1=1
    """

    params = []

    if ciudad and ciudad != "Todas":
        query += " AND sd.ciudad = %s"
        params.append(ciudad)

    if sede and sede != "Todas":
        query += " AND sd.nombre = %s"
        params.append(sede)

    if tipo and tipo != "Todos":
        query += " AND m.tipo = %s"
        params.append(tipo)

    if maquina and maquina != "Todas":
        query += " AND m.numero_equipo = %s"
        params.append(maquina)

    query += " ORDER BY s.id DESC LIMIT %s OFFSET %s"
    params.extend([limite, offset])

    cursor.execute(query, params)
    datos = cursor.fetchall()

    connection_pool.putconn(conn)
    return datos

def contar_solicitudes_filtradas(ciudad=None, sede=None, tipo=None, maquina=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT COUNT(*)
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    LEFT JOIN sedes sd ON m.sede_id = sd.id
    WHERE 1=1
    """

    params = []

    if ciudad and ciudad != "Todas":
        query += " AND sd.ciudad = %s"
        params.append(ciudad)

    if sede and sede != "Todas":
        query += " AND sd.nombre = %s"
        params.append(sede)

    if tipo and tipo != "Todos":
        query += " AND m.tipo = %s"
        params.append(tipo)

    if maquina and maquina != "Todas":
        query += " AND m.numero_equipo = %s"
        params.append(maquina)

    cursor.execute(query, params)
    total = cursor.fetchone()[0]

    connection_pool.putconn(conn)
    return total

def resumen_estados_solicitudes(ciudad=None, sede=None, tipo=None, maquina=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT 
        SUM(CASE WHEN s.estado = 'Pendiente' THEN 1 ELSE 0 END),
        SUM(CASE WHEN s.estado = 'Cerrada' THEN 1 ELSE 0 END),
        COUNT(*)
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    LEFT JOIN sedes sd ON m.sede_id = sd.id
    WHERE 1=1
    """

    params = []

    if ciudad and ciudad != "Todas":
        query += " AND sd.ciudad = %s"
        params.append(ciudad)

    if sede and sede != "Todas":
        query += " AND sd.nombre = %s"
        params.append(sede)

    if tipo and tipo != "Todos":
        query += " AND m.tipo = %s"
        params.append(tipo)

    if maquina and maquina != "Todas":
        query += " AND m.numero_equipo = %s"
        params.append(maquina)

    cursor.execute(query, params)

    pendientes, cerradas, total = cursor.fetchone()

    connection_pool.putconn(conn)

    return pendientes or 0, cerradas or 0, total or 0

def obtener_solicitudes_export(ciudad=None, sede=None, tipo=None, maquina_id=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT 
            s.fecha,
            (m.tipo || ' ' || m.numero_equipo) AS maquina,
            m.tipo,
            s.item_falla,
            s.veces_detectada,
            s.estado,
            s.origen
        FROM solicitudes_mantenimiento s
        JOIN maquinas m ON s.maquina_id = m.id
        WHERE 1=1
    """

    params = []

    # -------------------------
    # FILTRO CIUDAD
    # -------------------------
    if ciudad and ciudad != "Todas":
        query += " AND m.ciudad = %s"
        params.append(ciudad)

    # -------------------------
    # FILTRO SEDE
    # -------------------------
    if sede and sede != "Todas":
        query += " AND m.sede = %s"
        params.append(sede)

    # -------------------------
    # FILTRO TIPO
    # -------------------------
    if tipo and tipo != "Todos":
        query += " AND m.tipo = %s"
        params.append(tipo)

    # -------------------------
    # FILTRO MÁQUINA
    # -------------------------
    if maquina_id:
        query += " AND s.maquina_id = %s"
        params.append(maquina_id)

    query += " ORDER BY s.fecha DESC"

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    connection_pool.putconn(conn)
    return data



#---------------------
# MANTENIMIENTOS
def registrar_mantenimiento(maquina_id, fecha, tecnico, recibido_por, observaciones, solicitudes):

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
        INSERT INTO mantenimientos (maquina_id, fecha, tecnico, recibido_por, observaciones)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """, (maquina_id, fecha, tecnico, recibido_por, observaciones))

        mantenimiento_id = cursor.fetchone()[0]

        for item in solicitudes:

            cursor.execute("""
            SELECT id FROM solicitudes_mantenimiento
            WHERE maquina_id = %s
            AND item_falla = %s
            AND estado = 'Pendiente'
            """, (maquina_id, item))

            solicitudes_db = cursor.fetchall()

            for s in solicitudes_db:

                cursor.execute("""
                INSERT INTO mantenimiento_solicitudes (mantenimiento_id, solicitud_id)
                VALUES (%s, %s)
                """, (mantenimiento_id, s[0]))

                cursor.execute("""
                UPDATE solicitudes_mantenimiento
                SET estado = 'Cerrada'
                WHERE id = %s
                """, (s[0],))

        conn.commit()
        actualizar_estado_por_solicitudes(maquina_id)
        
        return mantenimiento_id
    
    except Exception as e:
        conn.rollback()
        print("Error al registrar mantenimiento:", e)
        return None
    
    finally:
        connection_pool.putconn(conn)
         
def obtener_mantenimientos_paginados(pagina, registros_por_pagina=15):

    conn = conectar()
    cursor = conn.cursor()

    offset = (pagina - 1) * registros_por_pagina

    cursor.execute("""
    SELECT 
        s.ciudad,
        s.nombre,
        m2.numero_equipo,
        m2.tipo,
        m.fecha,
        m.observaciones
    FROM mantenimientos m
    LEFT JOIN maquinas m2 ON m.maquina_id = m2.id
    LEFT JOIN sedes s ON m2.sede_id = s.id
    ORDER BY m.id DESC
    LIMIT %s OFFSET %s
    """, (registros_por_pagina, offset))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def contar_mantenimientos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM mantenimientos")

    total = cursor.fetchone()[0]

    connection_pool.putconn(conn)

    return total

def obtener_mantenimientos_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        m.id, 
        m.fecha,
        ma.numero_equipo,
        ma.tipo,
        m.tecnico,
        m.recibido_por,
        m.observaciones
    FROM mantenimientos m
    JOIN maquinas ma ON m.maquina_id = ma.id
    WHERE m.maquina_id = %s
    ORDER BY m.fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_todos_mantenimientos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.id,
        m.fecha,
        ma.numero_equipo,
        ma.tipo,
        m.tecnico,
        m.observaciones
    FROM mantenimientos m
    JOIN maquinas ma ON m.maquina_id = ma.id
    ORDER BY m.fecha DESC, m.id DESC
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_mantenimientos_con_solicitudes(maquina_id=None):

    conn = conectar()
    cursor = conn.cursor()

    if maquina_id:
        cursor.execute("""
        SELECT 
            m.id,
            m.fecha,
            ma.numero_equipo,
            ma.tipo,
            m.tecnico,
            m.recibido_por,
            m.observaciones,
            STRING_AGG(sm.solicitud_id::text, ',')
        FROM mantenimientos m
        JOIN maquinas ma ON m.maquina_id = ma.id
        LEFT JOIN mantenimiento_solicitudes sm ON m.id = sm.mantenimiento_id
        WHERE m.maquina_id = %s
        GROUP BY 
            m.id,
            m.fecha,
            ma.numero_equipo,
            ma.tipo,
            m.tecnico,
            m.recibido_por,
            m.observaciones
        ORDER BY m.fecha DESC, m.id DESC
        """, (maquina_id,))
    else:
        cursor.execute("""
        SELECT 
            m.id,
            m.fecha,
            ma.numero_equipo,
            ma.tipo,
            m.tecnico,
            m.recibido_por,
            m.observaciones,
            STRING_AGG(sm.solicitud_id::text, ',')
        FROM mantenimientos m
        JOIN maquinas ma ON m.maquina_id = ma.id
        LEFT JOIN mantenimiento_solicitudes sm ON m.id = sm.mantenimiento_id
        GROUP BY 
            m.id,
            m.fecha,
            ma.numero_equipo,
            ma.tipo,
            m.tecnico,
            m.recibido_por,
            m.observaciones
        ORDER BY m.fecha DESC, m.id DESC
        """)

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos

def actualizar_mantenimiento(mantenimiento_id, tecnico, recibido_por, observaciones):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE mantenimientos
    SET tecnico = %s, recibido_por = %s, observaciones = %s
    WHERE id = %s
    """, (tecnico, recibido_por, observaciones, mantenimiento_id))

    conn.commit()
    connection_pool.putconn(conn)

def obtener_descripciones_solicitudes(ids_str):

    if not ids_str:
        return "Sin solicitudes"

    conn = conectar()
    cursor = conn.cursor()

    ids = ids_str.split(",")

    query = f"""
    SELECT item_falla
    FROM solicitudes_mantenimiento
    WHERE id IN ({','.join(['%s']*len(ids))})
    """

    cursor.execute(query, ids)

    resultados = [r[0] for r in cursor.fetchall()]

    connection_pool.putconn(conn)

    return ", ".join(resultados)

def insertar_costo(mantenimiento_id, tipo, descripcion, cantidad, costo_unitario):

    conn = conectar()
    cursor = conn.cursor()

    costo_total = cantidad * costo_unitario

    cursor.execute("""
    INSERT INTO costos_mantenimiento
    (mantenimiento_id, tipo_costo, descripcion, cantidad, costo_unitario, costo_total)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, (mantenimiento_id, tipo, descripcion, cantidad, costo_unitario, costo_total))

    conn.commit()
    connection_pool.putconn(conn)

def obtener_costos_por_mantenimiento(mantenimiento_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM costos_mantenimiento
    WHERE mantenimiento_id = %s
    """, (mantenimiento_id,))

    resultados = cursor.fetchall()

    connection_pool.putconn(conn)

    return resultados

def actualizar_costo(costo_id, descripcion, cantidad, costo_unitario):

    conn = conectar()
    cursor = conn.cursor()

    costo_total = cantidad * costo_unitario

    cursor.execute("""
    UPDATE costos_mantenimiento
    SET descripcion = %s, cantidad = %s, costo_unitario = %s, costo_total = %s
    WHERE id = %s
    """, (descripcion, cantidad, costo_unitario, costo_total, costo_id))

    conn.commit()
    connection_pool.putconn(conn)

def eliminar_costo(costo_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM costos_mantenimiento WHERE id = %s", (costo_id,))

    conn.commit()
    connection_pool.putconn(conn)
    
def obtener_mantenimientos_export(maquina_id=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT 
            m.ciudad,
            m.sede,
            (mq.tipo || ' ' || mq.numero_equipo) AS maquina,
            mq.tipo,
            m.fecha,
            m.descripcion
        FROM mantenimientos m
        JOIN maquinas mq ON m.maquina_id = mq.id
        WHERE 1=1
    """
    params = []

    if maquina_id:
        query += " AND m.maquina_id = %s"
        params.append(maquina_id)

    query += " ORDER BY m.fecha DESC"

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    connection_pool.putconn(conn)
    return data    

def obtener_mantenimientos_con_costos_export(maquina_id=None):

    conn = conectar()
    cursor = conn.cursor()

    # -------------------------
    # MANTENIMIENTOS
    # -------------------------
    query_mant = """
        SELECT 
            m.id,
            mq.tipo,
            mq.numero_equipo,
            m.fecha,
            m.tecnico
        FROM mantenimientos m
        JOIN maquinas mq ON m.maquina_id = mq.id
        WHERE 1=1
    """

    params = []

    if maquina_id:
        query_mant += " AND m.maquina_id = %s"
        params.append(maquina_id)

    query_mant += " ORDER BY m.fecha DESC"

    cursor.execute(query_mant, tuple(params))
    mantenimientos = cursor.fetchall()

    # -------------------------
    # COSTOS
    # -------------------------
    cursor.execute("""
        SELECT 
            mantenimiento_id,
            tipo_costo,
            descripcion,
            cantidad,
            costo_unitario,
            costo_total
        FROM costos_mantenimiento
    """)

    costos = cursor.fetchall()

    connection_pool.putconn(conn)

    return mantenimientos, costos


   

# HOJA DE VIDA
def obtener_costo_total_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(cm.costo_total)
    FROM costos_mantenimiento cm
    JOIN mantenimientos m ON cm.mantenimiento_id = m.id
    WHERE m.maquina_id = %s
    """, (maquina_id,))

    total = cursor.fetchone()[0]

    connection_pool.putconn(conn)

    return total or 0

def obtener_total_por_mantenimiento(mantenimiento_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT SUM(costo_total)
    FROM costos_mantenimiento
    WHERE mantenimiento_id = %s
    """, (mantenimiento_id,))

    total = cursor.fetchone()[0]

    connection_pool.putconn(conn)

    return total or 0

def obtener_ultimas_solicitudes(maquina_id, limite=3):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT item_falla, fecha
    FROM solicitudes_mantenimiento
    WHERE maquina_id = %s
    ORDER BY fecha DESC
    LIMIT %s
    """, (maquina_id, limite))

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos

def obtener_costos_por_maquina(maquina_id, limite=10):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        cm.tipo_costo,
        cm.descripcion,
        cm.cantidad,
        cm.costo_unitario,
        cm.costo_total,
        m.fecha
    FROM costos_mantenimiento cm
    JOIN mantenimientos m ON cm.mantenimiento_id = m.id
    WHERE m.maquina_id = %s
    ORDER BY m.fecha DESC
    LIMIT %s
    """, (maquina_id, limite))

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos


#---------------------
# HISTORIAL DE ESTADOS
def obtener_solicitudes_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fecha, item_falla, veces_detectada, estado
    FROM solicitudes_mantenimiento
    WHERE maquina_id = %s
    ORDER BY fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_checklists_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        c.id,
        c.fecha,
        SUM(CASE WHEN ci.cumple = 0 THEN 1 ELSE 0 END) AS fallas
    FROM checklists c
    LEFT JOIN checklist_items ci ON c.id = ci.checklist_id
    WHERE c.maquina_id = %s
    GROUP BY c.id
    ORDER BY c.fecha DESC
    """, (maquina_id,))

    checklists = cursor.fetchall()

    resultado = []

    for c in checklists:

        checklist_id = c[0]

        cursor.execute("""
        SELECT item
        FROM checklist_items
        WHERE checklist_id = %s
        AND cumple = 0
        """, (checklist_id,))

        items_no_conformes = [i[0] for i in cursor.fetchall()]

        resultado.append((
            c[0],  # id
            c[1],  # fecha
            c[2],  # número de fallas
            items_no_conformes
        ))

    connection_pool.putconn(conn)

    return resultado

def obtener_traslados_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        s1.ciudad,
        s1.nombre,
        s2.ciudad,
        s2.nombre,
        t.fecha,
        t.responsable
    FROM traslados t
    LEFT JOIN sedes s1 ON t.sede_origen = s1.id
    LEFT JOIN sedes s2 ON t.sede_destino = s2.id
    WHERE t.maquina_id = %s
    ORDER BY t.fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_indicadores_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    # Estado operativo
    cursor.execute("""
    SELECT estado_operacion
    FROM maquinas
    WHERE id = %s
    """, (maquina_id,))
    estado = cursor.fetchone()
    estado = estado[0] if estado else "Desconocido"

    # Total mantenimientos
    cursor.execute("""
    SELECT COUNT(*)
    FROM mantenimientos
    WHERE maquina_id = %s
    """, (maquina_id,))
    total_mantenimientos = cursor.fetchone()[0]

    # Total fallas detectadas
    cursor.execute("""
    SELECT SUM(veces_detectada)
    FROM solicitudes_mantenimiento
    WHERE maquina_id = %s
    """, (maquina_id,))
    total_fallas = cursor.fetchone()[0]
    total_fallas = total_fallas if total_fallas else 0

    # Falla más repetida
    cursor.execute("""
    SELECT item_falla, MAX(veces_detectada) as max_rep
    FROM solicitudes_mantenimiento
    WHERE maquina_id = %s
    GROUP BY item_falla
    ORDER BY max_rep DESC
    LIMIT 1
    """, (maquina_id,))
    falla = cursor.fetchone()

    falla_nombre = falla[0] if falla else "-"
    falla_repeticiones = falla[1] if falla else 0

    # Último mantenimiento
    cursor.execute("""
    SELECT fecha
    FROM mantenimientos
    WHERE maquina_id = %s
    ORDER BY fecha DESC
    LIMIT 1
    """, (maquina_id,))
    ultimo = cursor.fetchone()
    ultimo = ultimo[0] if ultimo else "Sin registros"

    connection_pool.putconn(conn)

    return {
        "estado": estado,
        "mantenimientos": total_mantenimientos,
        "fallas": total_fallas,
        "falla_top": falla_nombre,
        "falla_top_rep": falla_repeticiones,
        "ultimo_mantenimiento": ultimo
    }

def obtener_ubicacion_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        s.ciudad,
        s.nombre
    FROM maquinas m
    LEFT JOIN sedes s ON m.sede_id = s.id
    WHERE m.id = %s
    """, (maquina_id,))

    datos = cursor.fetchone()

    connection_pool.putconn(conn)

    return datos

def obtener_ultimo_traslado(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fecha
    FROM traslados
    WHERE maquina_id = %s
    ORDER BY fecha DESC
    LIMIT 1
    """, (maquina_id,))

    dato = cursor.fetchone()

    connection_pool.putconn(conn)

    return dato[0] if dato else None

def obtener_historial_estado(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT estado, fecha
    FROM historial_estado_maquina
    WHERE maquina_id = %s
    ORDER BY fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_resumen_general():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT estado_operacion, COUNT(*)
    FROM maquinas
    GROUP BY estado_operacion
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    resumen = {
        "Operativa": 0,
        "Operativa con falla": 0,
        "En mantenimiento": 0,
        "Fuera de servicio": 0
    }

    for estado, cantidad in datos:
        if estado in resumen:
            resumen[estado] = cantidad

    return resumen

def obtener_top_fallas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        s.item_falla,
        SUM(s.veces_detectada) as total
    FROM solicitudes_mantenimiento s
    GROUP BY s.item_falla
    ORDER BY total DESC
    LIMIT 5
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_top_fallas_por_maquina():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.tipo,
        m.numero_equipo,
        s.item_falla,
        COUNT(*) as total
    FROM solicitudes_mantenimiento s
    JOIN maquinas m ON s.maquina_id = m.id
    GROUP BY m.tipo, m.numero_equipo, s.item_falla
    ORDER BY total DESC
    LIMIT 10
    """)

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos

def obtener_ultimos_mantenimientos_dashboard():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT m.fecha, ma.numero_equipo, ma.tipo, m.observaciones
    FROM mantenimientos m
    LEFT JOIN maquinas ma ON m.maquina_id = ma.id
    ORDER BY m.fecha DESC
    LIMIT 5
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def calcular_disponibilidad():

    conn = conectar()
    cursor = conn.cursor()

    # Total de máquinas
    cursor.execute("SELECT COUNT(*) FROM maquinas")
    total = cursor.fetchone()[0]

    # Máquinas disponibles (operativas)
    cursor.execute("""
    SELECT COUNT(*)
    FROM maquinas
    WHERE estado_operacion IN ('Operativa', 'Operativa con falla')
    """)

    operativas = cursor.fetchone()[0]

    connection_pool.putconn(conn)

    if total == 0:
        return 0

    disponibilidad = (operativas / total) * 100

    return round(disponibilidad, 2)

def obtener_alertas():

    conn = conectar()
    cursor = conn.cursor()

    alertas = []

    # 1️⃣ Máquinas fuera de servicio
    cursor.execute("""
    SELECT numero_equipo, tipo
    FROM maquinas
    WHERE estado_operacion = 'Fuera de servicio'
    """)

    for m in cursor.fetchall():
        alertas.append(f"🔴 {m[1]} {m[0]} fuera de servicio")

    # 2️⃣ Máquinas con muchas fallas
    cursor.execute("""
    SELECT m.numero_equipo, m.tipo, SUM(s.veces_detectada) as total
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    WHERE s.estado = 'Pendiente'
    GROUP BY s.maquina_id, m.numero_equipo, m.tipo
    HAVING SUM(s.veces_detectada) >= 5
    """)

    for m in cursor.fetchall():
        alertas.append(f"⚠️ {m[1]} {m[0]} con {m[2]} fallas acumuladas")

    # 3️⃣ Máquinas sin mantenimiento reciente
    cursor.execute("""
    SELECT m.numero_equipo, m.tipo, MAX(mt.fecha)
    FROM maquinas m
    LEFT JOIN mantenimientos mt ON m.id = mt.maquina_id
    GROUP BY m.id
    """)

    

    hoy = date.today()  # 🔥 usamos date

    for m in cursor.fetchall():

        fecha = m[2]

        if fecha:
            # 🔥 convertir SIEMPRE a date
            if isinstance(fecha, datetime):
                fecha = fecha.date()

            dias = (hoy - fecha).days

            if dias > 30:
                alertas.append(f"🟡 {m[1]} {m[0]} sin mantenimiento hace {dias} días")

    connection_pool.putconn(conn)

    return alertas

def obtener_ranking_maquinas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.numero_equipo,
        m.tipo,
        SUM(s.veces_detectada) as total_fallas
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    GROUP BY s.maquina_id, m.numero_equipo, m.tipo
    ORDER BY total_fallas DESC
    LIMIT 5
    """)

    datos = cursor.fetchall()

    connection_pool.putconn(conn)

    return datos

def obtener_costos_dashboard():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.activo_fijo,
        m.tipo,
        m.numero_equipo,
        SUM(CAST(cm.costo_total AS NUMERIC)) as total_costos
    FROM costos_mantenimiento cm
    JOIN mantenimientos mt ON cm.mantenimiento_id = mt.id
    JOIN maquinas m ON mt.maquina_id = m.id
    GROUP BY m.id
    """)

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos


#----------------------------
# DAHSBOARD DE COSTOS
def obtener_costos_filtrados(fecha_inicio=None, fecha_fin=None, tipo=None, maquina=None, tipo_costo=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT 
        m.fecha,
        ma.tipo,
        ma.numero_equipo,
        cm.tipo_costo,
        cm.descripcion,
        cm.costo_total
    FROM costos_mantenimiento cm
    JOIN mantenimientos m ON cm.mantenimiento_id = m.id
    JOIN maquinas ma ON m.maquina_id = ma.id
    WHERE 1=1
    """

    params = []

    if fecha_inicio:
        query += " AND m.fecha >= %s"
        params.append(fecha_inicio)

    if fecha_fin:
        query += " AND m.fecha <= %s"
        params.append(fecha_fin)

    if tipo and tipo != "Todos":
        query += " AND ma.tipo = %s"
        params.append(tipo)

    if maquina:
        query += " AND ma.numero_equipo = %s"
        params.append(maquina)

    if tipo_costo and tipo_costo != "Todos":
        query += " AND cm.tipo_costo = %s"
        params.append(tipo_costo)

    query += " ORDER BY m.fecha DESC"

    cursor.execute(query, params)
    datos = cursor.fetchall()

    connection_pool.putconn(conn)
    return datos 

def obtener_kpis_costos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(costo_total), COUNT(*) FROM costos_mantenimiento")
    total, cantidad = cursor.fetchone()

    promedio = (total / cantidad) if cantidad else 0

    cursor.execute("""
    SELECT MAX(m.fecha)
    FROM costos_mantenimiento cm
    JOIN mantenimientos m ON cm.mantenimiento_id = m.id
    """)
    ultima_fecha = cursor.fetchone()[0]

    connection_pool.putconn(conn)

    return total or 0, promedio or 0, cantidad or 0, ultima_fecha

def obtener_ranking_costos_maquinas(limite=5):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        ma.tipo,
        ma.numero_equipo,
        SUM(cm.costo_total) as total
    FROM costos_mantenimiento cm
    JOIN mantenimientos m ON cm.mantenimiento_id = m.id
    JOIN maquinas ma ON m.maquina_id = ma.id
    GROUP BY ma.tipo, ma.numero_equipo
    ORDER BY total DESC
    LIMIT %s
    """, (limite,))

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos

def obtener_costos_por_mes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        TO_CHAR(m.fecha, 'YYYY-MM') as mes,
        SUM(cm.costo_total)
    FROM costos_mantenimiento cm
    JOIN mantenimientos m ON cm.mantenimiento_id = m.id
    GROUP BY mes
    ORDER BY mes ASC
    """)

    datos = cursor.fetchall()
    connection_pool.putconn(conn)

    return datos

#----------------------------
# OPERARIOS
def crear_tabla_operarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operarios (
        id SERIAL PRIMARY KEY,
        cedula TEXT UNIQUE,
        nombre TEXT,
        apellido TEXT
    )
    """)

    conn.commit()
    connection_pool.putconn(conn)
    
def agregar_columna_operario():
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE checklists ADD COLUMN operario_id INTEGER")
    except:
        pass

    conn.commit()
    connection_pool.putconn(conn)
    
def agregar_sede_operario():
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        ALTER TABLE operarios ADD COLUMN sede_id INTEGER
        """)
        
    except Exception as e:
        None

    conn.commit()
    connection_pool.putconn(conn)
    
def obtener_operario_por_cedula(cedula):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        o.id,
        o.nombre,
        o.apellido,
        s.nombre,
        s.ciudad
    FROM operarios o
    LEFT JOIN sedes s ON o.sede_id = s.id
    WHERE o.cedula = %s
    """, (cedula,))

    resultado = cursor.fetchone()
    connection_pool.putconn(conn)

    return resultado


def registrar_operario(cedula, nombre, apellido, sede):

    conn = conectar()
    cursor = conn.cursor()

    try:
        cedula = limpiar_cedula(cedula)
        nombre = limpiar_nombre(nombre)
        apellido = limpiar_nombre(apellido)
        sede = sede.strip()
        
        if not cedula:
            return False, "La cédula no es válida"

        cursor.execute("""
        INSERT INTO operarios (cedula, nombre, apellido, sede_id)
        VALUES (%s, %s, %s,
            (SELECT id FROM sedes WHERE nombre = %s)
        )
        """, (cedula, nombre, apellido, sede))

        conn.commit()
        return True, "Operario registrado correctamente"

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, "La cédula ya está registrada"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        connection_pool.putconn(conn)
        
        
def obtener_historial_operarios(filtro_sede=None, filtro_tipo=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT 
        c.fecha,
        o.nombre,
        o.apellido,
        o.cedula,
        m.tipo,
        m.numero_equipo,
        s.nombre,
        s.ciudad,
        (
            SELECT COUNT(*) 
            FROM checklist_items ci 
            WHERE ci.checklist_id = c.id AND ci.cumple = 0
        ) as fallas,
        CASE 
            WHEN c.id IS NOT NULL THEN 'Sí'
            ELSE 'No'
        END as cumplio
    FROM checklists c
    LEFT JOIN operarios o ON c.operario_id = o.id
    LEFT JOIN maquinas m ON c.maquina_id = m.id
    LEFT JOIN sedes s ON m.sede_id = s.id
    WHERE c.operario_id IS NOT NULL
    """

    params = []

    # 🔹 filtro sede
    if filtro_sede and filtro_sede != "Todas":
        query += " AND s.nombre = %s"
        params.append(filtro_sede)

    # 🔹 filtro tipo máquina
    if filtro_tipo and filtro_tipo != "Todos":
        query += " AND m.tipo = %s"
        params.append(filtro_tipo)

    query += " ORDER BY c.fecha DESC"

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    connection_pool.putconn(conn)
    return data

def obtener_control_diario_operarios():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM operarios
    """)
    total_operarios = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(DISTINCT operario_id)
    FROM checklists
    WHERE fecha = CURRENT_DATE
    AND operario_id IS NOT NULL
    """)
    operarios_activos = cursor.fetchone()[0]

    connection_pool.putconn(conn)

    return total_operarios, operarios_activos

def obtener_operarios_pendientes(filtro_sede=None):

    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT o.nombre, o.apellido, o.cedula, s.nombre
    FROM operarios o
    LEFT JOIN sedes s ON o.sede_id = s.id
    WHERE o.id NOT IN (
        SELECT DISTINCT operario_id
        FROM checklists
        WHERE fecha = CURRENT_DATE
        AND operario_id IS NOT NULL
    )
    """

    params = []

    if filtro_sede and filtro_sede != "Todas":
        query += " AND s.nombre = %s"
        params.append(filtro_sede)

    query += " ORDER BY o.nombre"

    cursor.execute(query, tuple(params))
    data = cursor.fetchall()

    connection_pool.putconn(conn)
    return data

def obtener_kpi_por_sede():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        s.nombre,
        COUNT(DISTINCT c.operario_id) as activos
    FROM sedes s
    LEFT JOIN maquinas m ON s.id = m.sede_id
    LEFT JOIN checklists c 
        ON m.id = c.maquina_id 
        AND c.fecha = CURRENT_DATE
        AND c.operario_id IS NOT NULL
    GROUP BY s.nombre
    ORDER BY s.nombre
    """)

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return data

def obtener_kpi_real_por_sede():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        s.nombre,
        COUNT(DISTINCT o.id) as total_operarios,
        COUNT(DISTINCT c.operario_id) as activos
    FROM sedes s
    LEFT JOIN operarios o ON o.sede_id = s.id
    LEFT JOIN checklists c 
        ON o.id = c.operario_id 
        AND c.fecha = CURRENT_DATE
    GROUP BY s.nombre
    ORDER BY s.nombre
    """)

    data = cursor.fetchall()
    connection_pool.putconn(conn)

    return data






