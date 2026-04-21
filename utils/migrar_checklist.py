from database import conectar
from config_checklist import checklists_por_tipo

def migrar():

    conn = conectar()
    cursor = conn.cursor()

    for tipo, estructura in checklists_por_tipo.items():

        # Si es lista → convertir a categoría única
        if isinstance(estructura, list):
            estructura = {"General": estructura}

        orden_cat = 0

        for categoria, items in estructura.items():

            # Insertar categoría
            cursor.execute("""
                INSERT INTO categorias_checklist (nombre, tipo_maquina, orden)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (categoria, tipo, orden_cat))

            categoria_id = cursor.fetchone()[0]

            orden_item = 0

            for item in items:
                cursor.execute("""
                    INSERT INTO items_checklist (categoria_id, nombre, orden)
                    VALUES (%s, %s, %s)
                """, (categoria_id, item, orden_item))

                orden_item += 1

            orden_cat += 1

    conn.commit()
    conn.close()

    print("✅ Migración completada")


if __name__ == "__main__":
    migrar()