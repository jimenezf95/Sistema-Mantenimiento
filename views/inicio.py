import streamlit as st

from database import (
    calcular_disponibilidad,
    obtener_resumen_general,
    obtener_alertas,
    obtener_ultimos_mantenimientos_dashboard
)


def vista_inicio():

    st.title("🏠 Centro de control")

    # =========================
    # 🚨 ALERTAS (PRIORIDAD #1)
    # =========================

    st.subheader("🚨 Atención requerida")

    alertas = obtener_alertas()

    if not alertas:
        st.success("No hay alertas activas")
    else:
        for alerta in alertas:
            st.error(alerta)

    st.divider()

    # =========================
    # ⚡ ACCIONES RÁPIDAS
    # =========================

    st.subheader("⚡ Acciones rápidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Nueva checklist"):
            st.session_state.opcion = "Registro de Checklists"
            st.rerun()
            
        if st.button("📋 Hoja de vida de equipos"):
            st.session_state.opcion = "Hoja de vida de Equipos"
            st.rerun()

    with col2:
        if st.button("➕ Nueva solicitud de mantenimiento"):
            st.session_state.opcion = "Solicitudes de Mantenimiento"
            st.rerun()
            
        if st.button("📂 Historial de solicitudes"):
            st.session_state.opcion = "Historial de Solicitudes"
            st.rerun()

    with col3:
        if st.button("➕ Nueva registro de mantenimiento"):
            st.session_state.opcion = "Registro de Mantenimientos"
            st.rerun()
        
        if st.button("📊 Ver Dashboard general"):
            st.session_state.opcion = "Dashboard General"
            st.rerun()

    st.divider()

    # =========================
    # 📊 RESUMEN RÁPIDO
    # =========================

    st.subheader("📊 Estado general")

    resumen = obtener_resumen_general()
    disponibilidad = calcular_disponibilidad()

    total_maquinas = sum(resumen.values())
    maquinas_falla = resumen["Operativa con falla"] + resumen["Fuera de servicio"]

    porcentaje_falla = (maquinas_falla / total_maquinas * 100) if total_maquinas > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Disponibilidad", f"{disponibilidad}%")
    col2.metric("Máquinas", total_maquinas)
    col3.metric("Con fallas", maquinas_falla)
    col4.metric("% fallas", f"{porcentaje_falla:.1f}%")

    st.progress(int(disponibilidad))

    st.divider()

    # =========================
    # 📋 ACTIVIDAD RECIENTE
    # =========================

    st.subheader("📋 Últimos mantenimientos")

    mantenimientos = obtener_ultimos_mantenimientos_dashboard()

    if not mantenimientos:
        st.info("No hay mantenimientos registrados")
    else:

        col1, col2, col3, col4 = st.columns(4)

        col1.write("Fecha")
        col2.write("Tipo")
        col3.write("Equipo")
        col4.write("Descripción")

        for m in mantenimientos:

            col1, col2, col3, col4 = st.columns(4)

            col1.write(m[0])
            col2.write(m[2])
            col3.write(m[1])
            col4.write(m[3])