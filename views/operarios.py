import streamlit as st
import pandas as pd
from database import(
    registrar_operario, 
    obtener_operario_por_cedula,
    obtener_historial_operarios, 
    obtener_control_diario_operarios,
    obtener_operarios_pendientes, 
    obtener_sedes_diff,
    obtener_tipos_maquina,
    obtener_kpi_por_sede,
    obtener_kpi_real_por_sede,
)

from utils.export import generar_excel_operarios_control
from utils.export import generar_excel_historial_operarios

def vista_gestion_operarios():

    st.title("👷 Gestión de Operarios")

    # =========================
    # FORMULARIO REGISTRO
    # =========================
    st.subheader("Registrar nuevo operario")

    with st.form("form_operario"):

        cedula = st.text_input("Cédula")
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        
        sedes = obtener_sedes_diff()
        sede = st.selectbox("Sede", ["Seleccionar"] + sedes)

        submitted = st.form_submit_button("Registrar")

        if submitted:

            if not cedula or not nombre or not apellido or not sede or sede == "Seleccionar":
                st.error("Todos los campos son obligatorios")
                return

            ok, msg = registrar_operario(cedula, nombre, apellido, sede)

            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.divider()

    # =========================
    # BUSCAR OPERARIO
    # =========================
    st.subheader("Consultar operario")

    cedula_buscar = st.text_input("Ingrese cédula para buscar")

    if cedula_buscar:

        operario = obtener_operario_por_cedula(cedula_buscar)

        if operario:
            nombre_sede = operario[3] if operario[3] else "Sin sede"
            ciudad = operario[4] if operario[4] else ""

            st.success(
                f"Operario: {operario[1]} {operario[2]} | "
                f"Sede: {nombre_sede} | {ciudad}"
            )
        else:
            st.warning("Operario no encontrado")
            
            


def vista_historial_operarios():

    st.title("📊 Historial de Operarios")

    # =========================
    # KPI GLOBAL
    # =========================
    total, activos = obtener_control_diario_operarios()

    pendientes = total - activos
    porcentaje = activos / total if total > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Operarios Totales", total)
    col2.metric("Cumplieron Hoy", activos)
    col3.metric("Pendientes", pendientes)

    # 🔥 BARRA DE PROGRESO
    st.progress(porcentaje)
    st.write(f"Cumplimiento global: {round(porcentaje * 100, 2)}%")

    if pendientes > 0:
        st.warning(f"⚠ Faltan {pendientes} operarios por completar checklist hoy")
    else:
        st.success("✅ Todos los operarios cumplieron hoy")

    # =========================
    # KPI POR SEDE
    # =========================
    st.divider()
    st.subheader("🏭 Cumplimiento por sede")

    data_sedes = obtener_kpi_real_por_sede()

    if not data_sedes:
        st.warning("No hay sedes registradas")
    else:
        for sede, total_sede, activos_sede in data_sedes:

            if total_sede == 0:
                continue

            porcentaje = activos_sede / total_sede

            st.write(f"**{sede}**")

            st.progress(porcentaje)

            st.write(
                f"{activos_sede}/{total_sede} "
                f"({round(porcentaje * 100, 1)}%)"
            )
    
    st.divider()

    # =========================
    # FILTROS
    # =========================
    sedes = ["Todas"] + obtener_sedes_diff()
    tipos = ["Todos"] + obtener_tipos_maquina()

    col1, col2 = st.columns(2)

    filtro_sede = col1.selectbox("Filtrar por sede", sedes)
    filtro_tipo = col2.selectbox("Filtrar por tipo de máquina", tipos)

    # =========================
    # DATA HISTORIAL
    # =========================
    data = obtener_historial_operarios(filtro_sede, filtro_tipo)

    if not data:
        st.warning("No hay registros")
        return
    st.write("Registros encontrados: " + str(len(data)))
    df = pd.DataFrame(data, columns=[
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
    ])
    
    df["Cumplió"] = df["Cumplió"].map({
        "Sí": "✅",
        "No": "❌"
    })

    # =========================
    # PAGINACIÓN
    # =========================
    registros_por_pagina = 15

    if "pagina_historial" not in st.session_state:
        st.session_state.pagina_historial = 1

    total_registros = len(df)
    total_paginas = (total_registros // registros_por_pagina) + (1 if total_registros % registros_por_pagina > 0 else 0)

    inicio = (st.session_state.pagina_historial - 1) * registros_por_pagina
    fin = inicio + registros_por_pagina

    df_pagina = df.iloc[inicio:fin]

    st.dataframe(df_pagina, use_container_width=True)

    # 🔘 CONTROLES
    col1, col2, col3 = st.columns([1,2,1])

    with col1:
        if st.button("⬅️ Anterior") and st.session_state.pagina_historial > 1:
            st.session_state.pagina_historial -= 1

    with col3:
        if st.button("Siguiente ➡️") and st.session_state.pagina_historial < total_paginas:
            st.session_state.pagina_historial += 1

    with col2:
        st.write(f"Página {st.session_state.pagina_historial} de {total_paginas}")

    # =========================
    # EXPORTAR
    # =========================
    archivo = generar_excel_historial_operarios(data)

    st.download_button(
        "📥 Descargar Excel",
        archivo,
        "historial_operarios.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # =========================
    # PENDIENTES (ABAJO)
    # =========================
    st.divider()
    st.subheader("🚨 Operarios pendientes hoy")

    pendientes_data = obtener_operarios_pendientes(filtro_sede)

    if pendientes_data:

        df_pend = pd.DataFrame(pendientes_data, columns=[
            "Nombre", "Apellido", "Cédula", "Sede"
        ])

        # =========================
        # PAGINACIÓN PENDIENTES
        # =========================
        registros_por_pagina = 10

        if "pagina_pendientes" not in st.session_state:
            st.session_state.pagina_pendientes = 1

        total_registros = len(df_pend)
        total_paginas = (total_registros // registros_por_pagina) + (
            1 if total_registros % registros_por_pagina > 0 else 0
        )

        # evitar página inválida
        if st.session_state.pagina_pendientes > total_paginas:
            st.session_state.pagina_pendientes = 1

        inicio = (st.session_state.pagina_pendientes - 1) * registros_por_pagina
        fin = inicio + registros_por_pagina

        df_pagina = df_pend.iloc[inicio:fin]

        st.dataframe(df_pagina, use_container_width=True)

        # 🔘 CONTROLES
        col1, col2, col3 = st.columns([1,2,1])

        with col1:
            if st.button("⬅️ Anterior", key="prev_pend") and st.session_state.pagina_pendientes > 1:
                st.session_state.pagina_pendientes -= 1

        with col3:
            if st.button("Siguiente ➡️", key="next_pend") and st.session_state.pagina_pendientes < total_paginas:
                st.session_state.pagina_pendientes += 1

        with col2:
            st.write(f"Página {st.session_state.pagina_pendientes} de {total_paginas}")

        
    else:
        st.success("Todos los operarios cumplieron hoy")