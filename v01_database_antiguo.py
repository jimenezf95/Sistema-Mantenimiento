import sqlite3

def conectar():
    conn = sqlite3.connect("mantenimiento.db")
    return conn


def crear_tablas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maquinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        numero_equipo TEXT,
        modelo TEXT,
        fabricante TEXT,
        estado_operacion TEXT,
        sede_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sedes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        ciudad TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mantenimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maquina_id INTEGER,
        fecha TEXT,
        tipo_evento TEXT,
        descripcion_falla TEXT,
        accion_realizada TEXT,
        responsable TEXT,
        estado_final TEXT,
        estado_solicitud TEXT,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maquina_id INTEGER,
        tipo_maquina TEXT,
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
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS solicitudes_mantenimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        maquina_id INTEGER,
        fecha TEXT,
        descripcion_falla TEXT,
        origen TEXT,
        estado TEXT,
        FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
    )
    """)

    conn.commit()
    conn.close()
    

#---------------------
#MAQUINAS Y SEDES

def insertar_maquina(tipo, numero_equipo, modelo, fabricante, estado_operacion, sede_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO maquinas (tipo, numero_equipo, modelo, fabricante, estado_operacion, sede_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (tipo, numero_equipo, modelo, fabricante, estado_operacion, sede_id))

    conn.commit()
    conn.close()

def obtener_maquinas():

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
        sedes.nombre,
        sedes.ciudad
    FROM maquinas
    LEFT JOIN sedes ON maquinas.sede_id = sedes.id
    """)

    datos = cursor.fetchall()

    conn.close()

    return datos

def eliminar_maquina(id_maquina):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM maquinas WHERE id = ?", (id_maquina,))

    conn.commit()
    conn.close()

def actualizar_maquina(id, tipo, numero_equipo, modelo, fabricante, estado_operacion, sede_id):

    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE maquinas
    SET tipo = ?, numero_equipo = ?, modelo = ?, fabricante = ?, estado_operacion = ?, sede_id = ?
    WHERE id = ?
    """, (tipo, numero_equipo, modelo, fabricante, estado_operacion, sede_id, id))

    conn.commit()
    conn.close()


def insertar_sede(nombre, ciudad):

    conn = conectar()
    cursor = conn.cursor()

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

def eliminar_sede(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sedes WHERE id = ?", (id,))

    conn.commit()
    conn.close()
#---------------------

 

def insertar_mantenimiento(maquina_id, fecha, tipo_evento, descripcion_falla, accion_realizada, responsable, estado_final,estado_solicitud):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO mantenimientos (
        maquina_id,
        fecha,
        tipo_evento,
        descripcion_falla,
        accion_realizada,
        responsable,
        estado_final,
        estado_solicitud
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (maquina_id, fecha, tipo_evento, descripcion_falla, accion_realizada, responsable, estado_final, estado_solicitud))

    conn.commit()
    conn.close()

def eliminar_mantenimiento(mantenimiento_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM mantenimientos
    WHERE id = ?
    """, (mantenimiento_id,))

    conn.commit()
    conn.close()

def obtener_mantenimientos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        mantenimientos.id,
        maquinas.numero_equipo,
        maquinas.tipo,
        mantenimientos.fecha,
        mantenimientos.tipo_evento,
        mantenimientos.descripcion_falla,
        mantenimientos.accion_realizada,
        mantenimientos.responsable,
        mantenimientos.estado_final
    FROM mantenimientos
    LEFT JOIN maquinas ON mantenimientos.maquina_id = maquinas.id
    ORDER BY mantenimientos.fecha DESC
    """)

    datos = cursor.fetchall()

    conn.close()

    return datos



def insertar_checklist(maquina_id, tipo_maquina, fecha):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checklists (maquina_id, tipo_maquina, fecha)
        VALUES (?, ?, ?)
    """, (maquina_id, tipo_maquina, fecha))

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
    
def crear_solicitud_mantenimiento(maquina_id, item, observacion):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mantenimientos
        (maquina_id, fecha, tipo_evento, descripcion_falla, accion_realizada, responsable, estado_final)
        VALUES (?, date('now'), ?, ?, ?, ?, ?)
    """, (
        maquina_id,
        "Solicitud",
        item + " - " + observacion,
        "",
        "",
        "Pendiente"
    ))

    conn.commit()
    conn.close()

def obtener_checklists():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.id,
            m.tipo,
            m.numero_equipo,
            c.fecha
        FROM checklists c
        JOIN maquinas m ON c.maquina_id = m.id
        ORDER BY c.fecha DESC
    """)

    checklists = cursor.fetchall()

    conn.close()

    return checklists

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



def insertar_solicitud(maquina_id, descripcion_falla, origen):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO solicitudes_mantenimiento
        (maquina_id, fecha, descripcion_falla, origen, estado)
        VALUES (?, date('now'), ?, ?, ?)
    """, (
        maquina_id,
        descripcion_falla,
        origen,
        "Pendiente"
    ))

    conn.commit()
    conn.close()

def obtener_solicitudes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            s.id,
            m.tipo,
            m.numero_equipo,
            s.descripcion_falla,
            s.fecha,
            s.estado
        FROM solicitudes_mantenimiento s
        JOIN maquinas m ON s.maquina_id = m.id
        WHERE s.estado = 'Pendiente'
        ORDER BY s.fecha DESC
    """)

    solicitudes = cursor.fetchall()

    conn.close()

    return solicitudes

def obtener_solicitudes_pendientes_por_maquina(maquina_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descripcion_falla
        FROM solicitudes_mantenimiento
        WHERE maquina_id = ?
        AND estado = 'Pendiente'
    """, (maquina_id,))

    solicitudes = cursor.fetchall()

    conn.close()

    return solicitudes

def cerrar_solicitudes(ids_solicitudes):

    conn = conectar()
    cursor = conn.cursor()

    for s in ids_solicitudes:
        cursor.execute("""
            UPDATE solicitudes_mantenimiento
            SET estado = 'Cerrado'
            WHERE id = ?
        """, (s,))

    conn.commit()
    conn.close()
