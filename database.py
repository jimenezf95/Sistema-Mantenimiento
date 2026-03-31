import sqlite3

def conectar():
    conn = sqlite3.connect("mantenimiento.db", timeout=30)
    return conn


def crear_tablas():

    conn = conectar()
    cursor = conn.cursor()

    # ======================
    # SEDES
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sedes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        ciudad TEXT
    )
    """)

    # ======================
    # TIPOS DE MAQUINA
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipos_maquina (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE
    )
    """)

    # ======================
    # MAQUINAS (MEJORADA)
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maquinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        activo_fijo TEXT UNIQUE,
        numero_equipo TEXT,
        modelo TEXT,
        fabricante TEXT,
        anio INTEGER,
        estado_operacion TEXT,
        sede_id INTEGER,
        fecha_registro TEXT DEFAULT CURRENT_DATE,
        FOREIGN KEY (sede_id) REFERENCES sedes(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traslados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maquina_id INTEGER,
        sede_origen INTEGER,
        sede_destino INTEGER,
        fecha TEXT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maquina_id INTEGER,
        fecha TEXT,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_id INTEGER,
        item TEXT,
        cumple INTEGER,
        observaciones TEXT,
        FOREIGN KEY (checklist_id) REFERENCES checklists(id)
    )
    """)

    # ======================
    # SOLICITUDES (MEJORADA)
    # ======================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitudes_mantenimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maquina_id INTEGER,
        fecha TEXT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maquina_id INTEGER,
        fecha TEXT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mantenimiento_id INTEGER,
        solicitud_id INTEGER,
        FOREIGN KEY (mantenimiento_id) REFERENCES mantenimientos(id),
        FOREIGN KEY (solicitud_id) REFERENCES solicitudes_mantenimiento(id)
    )
    """)

    conn.commit()
    conn.close()   

#---------------------
#MAQUINAS

def insertar_maquina(tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id):

    conn = conectar()
    cursor = conn.cursor()

    activo_fijo = activo_fijo.strip().upper()

    cursor.execute("""
    INSERT INTO maquinas 
    (tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id))

    maquina_id = cursor.lastrowid  

    conn.commit()
    conn.close()

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

    conn.close()

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
    WHERE maquinas.id = ?
    """, (maquina_id,))

    maquina = cursor.fetchone()

    conn.close()

    return maquina

def eliminar_maquina(id_maquina):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM maquinas WHERE id = ?", (id_maquina,))

    conn.commit()
    conn.close()

def actualizar_maquina(id, tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id):

    conn = conectar()
    cursor = conn.cursor()

    activo_fijo = activo_fijo.strip().upper()

    cursor.execute("""
    UPDATE maquinas
    SET tipo = ?, activo_fijo = ?, numero_equipo = ?, modelo = ?, fabricante = ?, estado_operacion = ?, sede_id = ?
    WHERE id = ?
    """, (tipo, activo_fijo, numero_equipo, modelo, fabricante, estado_operacion, sede_id, id))

    conn.commit()
    conn.close()

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

    conn.close()

    return datos

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
    VALUES (?, ?)
    """, (nombre, ciudad))

    conn.commit()
    conn.close()

def obtener_sedes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sedes")

    datos = cursor.fetchall()

    conn.close()

    return datos

def sede_tiene_maquinas(sede_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM maquinas
    WHERE sede_id = ?
    """, (sede_id,))

    cantidad = cursor.fetchone()[0]

    conn.close()

    return cantidad

def eliminar_sede(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sedes WHERE id = ?", (id,))

    conn.commit()
    conn.close()

#---------------------
# TRASLADOS
def insertar_traslado(maquina_id, sede_origen, sede_destino, fecha, responsable, observaciones):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO traslados (maquina_id, sede_origen, sede_destino, fecha, responsable, observaciones)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (maquina_id, sede_origen, sede_destino, fecha, responsable, observaciones))

    # actualizar sede actual de la máquina
    cursor.execute("""
    UPDATE maquinas
    SET sede_id = ?
    WHERE id = ?
    """, (sede_destino, maquina_id))

    conn.commit()
    conn.close()

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

    conn.close()

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
    LIMIT ?
    """, (limit,))

    datos = cursor.fetchall()
    conn.close()

    return datos

#---------------------
# REGISTRO DE CHECKLISTS
def insertar_checklist(maquina_id, fecha):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checklists (maquina_id, fecha)
        VALUES (?, ?)
    """, (maquina_id, fecha))

    checklist_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return checklist_id

def insertar_item_checklist(checklist_id, item, cumple, observaciones):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checklist_items (checklist_id, item, cumple, observaciones)
        VALUES (?, ?, ?, ?)
    """, (checklist_id, item, cumple, observaciones))

    conn.commit()
    conn.close()
    
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

    conn.close()

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
        WHERE c.maquina_id = ?
        GROUP BY c.id
        ORDER BY c.fecha DESC, c.id DESC
        LIMIT 5
    """, (maquina_id,))

    datos = cursor.fetchall()

    conn.close()

    return datos

def obtener_items_checklist(checklist_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item, cumple, observaciones
        FROM checklist_items
        WHERE checklist_id = ?
    """, (checklist_id,))

    datos = cursor.fetchall()

    conn.close()

    return datos

def eliminar_checklist(checklist_id):

    conn = conectar()
    cursor = conn.cursor()

    # Primero eliminar los items de la checklist
    cursor.execute("""
        DELETE FROM checklist_items
        WHERE checklist_id = ?
    """, (checklist_id,))

    # Luego eliminar la checklist
    cursor.execute("""
        DELETE FROM checklists
        WHERE id = ?
    """, (checklist_id,))

    conn.commit()
    conn.close()

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
    LIMIT ?
    """, (limit,))

    data = cursor.fetchall()
    conn.close()

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
    WHERE s.ciudad = ?
    ORDER BY c.fecha DESC
    LIMIT 10
    """, (ciudad,))

    data = cursor.fetchall()
    conn.close()

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
    WHERE s.nombre = ?
    ORDER BY c.fecha DESC
    LIMIT 10
    """, (sede,))

    data = cursor.fetchall()
    conn.close()

    return data




#---------------------
# SOLICITUDES DE MANTENIMIENTO
def solicitud_pendiente_existente(maquina_id, descripcion):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM solicitudes_mantenimiento
        WHERE maquina_id = ?
        AND descripcion_falla = ?
        AND estado = 'Pendiente'
    """, (maquina_id, descripcion))

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None

def insertar_solicitud(maquina_id, item_falla, observacion, origen):

    conn = conectar()
    cursor = conn.cursor()

    # Buscar si ya existe solicitud pendiente para ese item
    cursor.execute("""
    SELECT id, veces_detectada
    FROM solicitudes_mantenimiento
    WHERE maquina_id = ?
    AND item_falla = ?
    AND estado = 'Pendiente'
    """, (maquina_id, item_falla))

    solicitud = cursor.fetchone()

    # Si ya existe → aumentar contador
    if solicitud:

        solicitud_id = solicitud[0]
        veces = solicitud[1] + 1

        cursor.execute("""
        UPDATE solicitudes_mantenimiento
        SET veces_detectada = ?
        WHERE id = ?
        """, (veces, solicitud_id))

        conn.commit()
        conn.close()

        return False, veces

    # Si no existe → crear nueva solicitud
    else:

        descripcion = f"{item_falla} - {observacion}"

        cursor.execute("""
        INSERT INTO solicitudes_mantenimiento
        (maquina_id, fecha, item_falla, descripcion_falla, origen, estado, veces_detectada)
        VALUES (?, DATE('now'), ?, ?, ?, 'Pendiente', 1)
        """, (maquina_id, item_falla, descripcion, origen))

        conn.commit()
        conn.close()

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

    conn.close()

    return datos

def cerrar_solicitud(solicitud_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE solicitudes_mantenimiento
    SET estado = 'Cerrada'
    WHERE id = ?
    """, (solicitud_id,))

    conn.commit()
    conn.close()

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

    conn.close()

    return datos

def obtener_solicitudes_pendientes_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        item_falla,
        MAX(veces_detectada)
    FROM solicitudes_mantenimiento
    WHERE maquina_id = ?
    AND estado = 'Pendiente'
    GROUP BY item_falla
    """, (maquina_id,))

    datos = cursor.fetchall()

    conn.close()

    return datos

def actualizar_estado_por_solicitudes(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM solicitudes_mantenimiento
    WHERE maquina_id = ?
    AND estado = 'Pendiente'
    """, (maquina_id,))

    pendientes = cursor.fetchone()[0]

    if pendientes > 0:
        nuevo_estado = "Operativa con falla"
    else:
        nuevo_estado = "Operativa"

    cursor.execute("""
    UPDATE maquinas
    SET estado_operacion = ?
    WHERE id = ?
    """, (nuevo_estado, maquina_id))

    conn.commit()
    conn.close()

def actualizar_estado_maquina(maquina_id, nuevo_estado):

    conn = conectar()
    cursor = conn.cursor()

    # Obtener estado actual
    cursor.execute("""
    SELECT estado_operacion
    FROM maquinas
    WHERE id = ?
    """, (maquina_id,))

    estado_actual = cursor.fetchone()[0]

    # Solo registrar si el estado cambia
    if estado_actual != nuevo_estado:

        cursor.execute("""
        UPDATE maquinas
        SET estado_operacion = ?
        WHERE id = ?
        """, (nuevo_estado, maquina_id))

        cursor.execute("""
        INSERT INTO historial_estado_maquina (maquina_id, estado, fecha)
        VALUES (?, ?, DATE('now'))
        """, (maquina_id, nuevo_estado))

    conn.commit()
    conn.close()



#---------------------
# MANTENIMIENTOS
def registrar_mantenimiento(maquina_id, fecha, tecnico, recibido_por, observaciones, solicitudes):

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
        INSERT INTO mantenimientos (maquina_id, fecha, tecnico, recibido_por, observaciones)
        VALUES (?, ?, ?, ?, ?)
        """, (maquina_id, fecha, tecnico, recibido_por, observaciones))

        mantenimiento_id = cursor.lastrowid

        for item in solicitudes:

            cursor.execute("""
            SELECT id FROM solicitudes_mantenimiento
            WHERE maquina_id = ?
            AND item_falla = ?
            AND estado = 'Pendiente'
            """, (maquina_id, item))

            solicitudes_db = cursor.fetchall()

            for s in solicitudes_db:

                cursor.execute("""
                INSERT INTO mantenimiento_solicitudes (mantenimiento_id, solicitud_id)
                VALUES (?, ?)
                """, (mantenimiento_id, s[0]))

                cursor.execute("""
                UPDATE solicitudes_mantenimiento
                SET estado = 'Cerrada'
                WHERE id = ?
                """, (s[0],))

        conn.commit()
        actualizar_estado_por_solicitudes(maquina_id)
    finally:
        conn.close()
        return mantenimiento_id
         
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
    LIMIT ? OFFSET ?
    """, (registros_por_pagina, offset))

    datos = cursor.fetchall()

    conn.close()

    return datos

def contar_mantenimientos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM mantenimientos")

    total = cursor.fetchone()[0]

    conn.close()

    return total

def obtener_mantenimientos_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.fecha,
        m.tecnico,
        m.recibido_por,
        m.observaciones
    FROM mantenimientos m
    WHERE m.maquina_id = ?
    ORDER BY m.fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    conn.close()

    return datos

def insertar_costo(mantenimiento_id, tipo, descripcion, cantidad, costo_unitario):

    conn = conectar()
    cursor = conn.cursor()

    costo_total = cantidad * costo_unitario

    cursor.execute("""
    INSERT INTO costos_mantenimiento
    (mantenimiento_id, tipo_costo, descripcion, cantidad, costo_unitario, costo_total)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (mantenimiento_id, tipo, descripcion, cantidad, costo_unitario, costo_total))

    conn.commit()
    conn.close()

def obtener_costos_por_mantenimiento(mantenimiento_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM costos_mantenimiento
    WHERE mantenimiento_id = ?
    """, (mantenimiento_id,))

    resultados = cursor.fetchall()

    conn.close()

    return resultados


#---------------------
# HISTORIAL DE ESTADOS
def obtener_solicitudes_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fecha, item_falla, veces_detectada, estado
    FROM solicitudes_mantenimiento
    WHERE maquina_id = ?
    ORDER BY fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    conn.close()

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
    WHERE c.maquina_id = ?
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
        WHERE checklist_id = ?
        AND cumple = 0
        """, (checklist_id,))

        items_no_conformes = [i[0] for i in cursor.fetchall()]

        resultado.append((
            c[0],  # id
            c[1],  # fecha
            c[2],  # número de fallas
            items_no_conformes
        ))

    conn.close()

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
    WHERE t.maquina_id = ?
    ORDER BY t.fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    conn.close()

    return datos

def obtener_indicadores_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    # Estado operativo
    cursor.execute("""
    SELECT estado_operacion
    FROM maquinas
    WHERE id = ?
    """, (maquina_id,))
    estado = cursor.fetchone()
    estado = estado[0] if estado else "Desconocido"

    # Total mantenimientos
    cursor.execute("""
    SELECT COUNT(*)
    FROM mantenimientos
    WHERE maquina_id = ?
    """, (maquina_id,))
    total_mantenimientos = cursor.fetchone()[0]

    # Total fallas detectadas
    cursor.execute("""
    SELECT SUM(veces_detectada)
    FROM solicitudes_mantenimiento
    WHERE maquina_id = ?
    """, (maquina_id,))
    total_fallas = cursor.fetchone()[0]
    total_fallas = total_fallas if total_fallas else 0

    # Falla más repetida
    cursor.execute("""
    SELECT item_falla, MAX(veces_detectada)
    FROM solicitudes_mantenimiento
    WHERE maquina_id = ?
    """, (maquina_id,))
    falla = cursor.fetchone()

    falla_nombre = falla[0] if falla else "-"
    falla_repeticiones = falla[1] if falla else 0

    # Último mantenimiento
    cursor.execute("""
    SELECT fecha
    FROM mantenimientos
    WHERE maquina_id = ?
    ORDER BY fecha DESC
    LIMIT 1
    """, (maquina_id,))
    ultimo = cursor.fetchone()
    ultimo = ultimo[0] if ultimo else "Sin registros"

    conn.close()

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
    WHERE m.id = ?
    """, (maquina_id,))

    datos = cursor.fetchone()

    conn.close()

    return datos

def obtener_ultimo_traslado(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT fecha
    FROM traslados
    WHERE maquina_id = ?
    ORDER BY fecha DESC
    LIMIT 1
    """, (maquina_id,))

    dato = cursor.fetchone()

    conn.close()

    return dato[0] if dato else None

def obtener_historial_estado(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT estado, fecha
    FROM historial_estado_maquina
    WHERE maquina_id = ?
    ORDER BY fecha DESC
    """, (maquina_id,))

    datos = cursor.fetchall()

    conn.close()

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

    conn.close()

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

    conn.close()

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

    conn.close()

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

    conn.close()

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

    # 2️⃣ Máquinas con muchas fallas (ej: más de 5)
    cursor.execute("""
    SELECT m.numero_equipo, m.tipo, SUM(s.veces_detectada) as total
    FROM solicitudes_mantenimiento s
    LEFT JOIN maquinas m ON s.maquina_id = m.id
    WHERE s.estado = 'Pendiente'
    GROUP BY s.maquina_id
    HAVING total >= 5
    """)

    for m in cursor.fetchall():
        alertas.append(f"⚠️ {m[1]} {m[0]} con {m[2]} fallas acumuladas")

    # 3️⃣ Máquinas sin mantenimiento reciente (ej: 30 días)
    cursor.execute("""
    SELECT m.numero_equipo, m.tipo, MAX(mt.fecha)
    FROM maquinas m
    LEFT JOIN mantenimientos mt ON m.id = mt.maquina_id
    GROUP BY m.id
    """)

    from datetime import datetime

    hoy = datetime.today()

    for m in cursor.fetchall():

        fecha = m[2]

        if fecha:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            dias = (hoy - fecha_dt).days

            if dias > 30:
                alertas.append(f"🟡 {m[1]} {m[0]} sin mantenimiento hace {dias} días")
        #else:
            #alertas.append(f"🟡 {m[1]} {m[0]} sin historial de mantenimiento")

    conn.close()

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
    GROUP BY s.maquina_id
    ORDER BY total_fallas DESC
    LIMIT 5
    """)

    datos = cursor.fetchall()

    conn.close()

    return datos

def obtener_costos_dashboard():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        m.activo_fijo,
        m.tipo,
        m.numero_equipo,
        SUM(CAST(cm.costo_total AS REAL)) as total_costos
    FROM costos_mantenimiento cm
    JOIN mantenimientos mt ON cm.mantenimiento_id = mt.id
    JOIN maquinas m ON mt.maquina_id = m.id
    GROUP BY m.id
    """)

    datos = cursor.fetchall()
    conn.close()

    return datos


####----------------------------
### BORRAR ESTA FUNCIÓN DESPUÉS DE USARLA 



