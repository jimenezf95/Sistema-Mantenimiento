import pandas as pd
from io import BytesIO

def generar_excel_solicitudes(data):

    columnas = [
        "Fecha",
        "Máquina",
        "Tipo",
        "Falla",
        "Veces detectada",
        "Estado",
        "Origen"
    ]

    df = pd.DataFrame(data, columns=columnas)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Solicitudes')

    return output.getvalue()


def generar_excel_mantenimientos_pro(mantenimientos, costos):

    # -------------------------
    # HOJA 1: RESUMEN
    # -------------------------
    resumen_data = []

    for m in mantenimientos:
        mant_id = m[0]

        costos_mant = [c for c in costos if c[0] == mant_id]
        total_costos = sum([float(c[5]) for c in costos_mant])

        resumen_data.append([
            mant_id,
            f"{m[1]} {m[2]}",
            m[3],
            m[4],
            total_costos
        ])

    df_resumen = pd.DataFrame(resumen_data, columns=[
        "ID",
        "Máquina",
        "Fecha",
        "Técnico",
        "Costo total"
    ])

    # -------------------------
    # HOJA 2: COSTOS (MEJORADA)
    # -------------------------
    detalle_data = []

    for c in costos:

        mant = next((m for m in mantenimientos if m[0] == c[0]), None)
        maquina = f"{mant[1]} {mant[2]}" if mant else "N/A"

        detalle_data.append([
            c[0],
            maquina,
            c[1],
            c[2],
            c[3],
            c[4],
            c[5]
        ])

    df_detalle = pd.DataFrame(detalle_data, columns=[
        "ID mantenimiento",
        "Máquina",
        "Tipo",
        "Descripción",
        "Cantidad",
        "Costo unitario",
        "Total"
    ])

    # -------------------------
    # EXPORTAR
    # -------------------------
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resumen.to_excel(writer, index=False, sheet_name="Resumen")
        df_detalle.to_excel(writer, index=False, sheet_name="Costos")

    return output.getvalue()

    columnas = [
        "Ciudad",
        "Sede",
        "Máquina",
        "Tipo",
        "Fecha",
        "Descripción"
    ]

    df = pd.DataFrame(data, columns=columnas)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mantenimientos')

    return output.getvalue()


def generar_excel_checklists(data):


    columnas = [
        "Fecha",
        "Máquina",
        "Ciudad",
        "Sede",
        "Resultado checklist"
    ]

    df = pd.DataFrame(data, columns=columnas)

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Checklists')

    return output.getvalue()


def generar_excel_maquinas(maquinas):


    data = []

    for m in maquinas:
        data.append([
            m[1],  # ID activo
            m[2],  # tipo
            m[3],  # equipo
            m[4],  # modelo
            m[5],  # fabricante
            m[6],  # estado
            m[7],  # sede
            m[8]   # ciudad
        ])

    columnas = [
        "ID Activo",
        "Tipo",
        "Equipo",
        "Modelo",
        "Fabricante",
        "Estado",
        "Sede",
        "Ciudad"
    ]

    df = pd.DataFrame(data, columns=columnas)

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario')

    return output.getvalue()


def generar_excel_operarios_control(data):

    columnas = [
        "Nombre",
        "Apellido",
        "Cédula"
    ]

    df = pd.DataFrame(data, columns=columnas)

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Operarios Pendientes')

    return output.getvalue()


def generar_excel_historial_operarios(data):

    columnas = [
        "Fecha",
        "Nombre",
        "Apellido",
        "Cédula",
        "Tipo Máquina",
        "Equipo",
        "Sede",
        "Ciudad",
        "Fallas",
        "Cumplió"
    ]

    df = pd.DataFrame(data, columns=columnas)
    df["Cumplió"] = df["Cumplió"].map({
        "Sí": "✅",
        "No": "❌"
    })

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Historial')

    return output.getvalue()

