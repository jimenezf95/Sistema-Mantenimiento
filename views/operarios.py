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
                f"Sede: {nombre_sede} | {ciudad})"
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

    df = pd.DataFrame(data, columns=[
        "Fecha",
        "Nombre",
        "Apellido",
        "Cédula",
        "Tipo Máquina",
        "Equipo",
        "Sede",
        "Ciudad",
        "Fallas"
    ])

    st.dataframe(df, use_container_width=True)

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

    pendientes_data = obtener_operarios_pendientes()

    if pendientes_data:

        df_pend = pd.DataFrame(pendientes_data, columns=[
            "Nombre", "Apellido", "Cédula"
        ])

        st.dataframe(df_pend, use_container_width=True)

        archivo_pend = generar_excel_operarios_control(pendientes_data)

        st.download_button(
            "📥 Descargar pendientes",
            archivo_pend,
            "pendientes_operarios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.success("Todos los operarios cumplieron hoy")