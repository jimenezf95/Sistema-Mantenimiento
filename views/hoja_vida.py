import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import (
    crear_tablas,
    obtener_maquinas,
    #Checklists
    obtener_checklists,
    obtener_ultimos_checklists_por_maquina,
    obtener_items_checklist,
    insertar_checklist,
    insertar_item_checklist,
    eliminar_checklist,
    obtener_ultimos_checklists,
    obtener_checklists_por_sede,
    obtener_checklists_por_ciudad,
    #Solicitudes de mantenimiento
    insertar_solicitud,
    obtener_solicitudes_pendientes,
    obtener_todas_solicitudes,
    cerrar_solicitud,
    solicitud_pendiente_existente,
    obtener_solicitudes_pendientes_por_maquina,
    obtener_solicitudes_filtradas,
    contar_solicitudes_filtradas,
    #Mantenimientos
    registrar_mantenimiento,
    obtener_mantenimientos_paginados,
    contar_mantenimientos,
    insertar_costo,
    obtener_costos_por_mantenimiento,
    obtener_todos_mantenimientos,
    obtener_costo_total_maquina,
    obtener_costos_por_maquina,
    #Dashboard 
    obtener_mantenimientos_por_maquina,
    obtener_solicitudes_por_maquina,
    obtener_checklists_por_maquina,
    obtener_traslados_por_maquina, 
    obtener_indicadores_maquina, 
    obtener_ubicacion_maquina, 
    obtener_ultimo_traslado,
    obtener_total_por_mantenimiento,
    obtener_ultimas_solicitudes,
    obtener_mantenimientos_con_solicitudes,
    obtener_descripciones_solicitudes,
    actualizar_estado_por_solicitudes,
    actualizar_estado_maquina,
    obtener_historial_estado,
    obtener_resumen_general,
    obtener_top_fallas,
    obtener_ultimos_mantenimientos_dashboard,
    calcular_disponibilidad,
    obtener_alertas,
    obtener_ranking_maquinas,
    obtener_costos_dashboard
)

def vista_hoja_vida():
    st.header("Hoja de Vida de Maquinaria y Equipo")

    maquinas = obtener_maquinas()

    if not maquinas:
        st.warning("No hay máquinas registradas.")
        st.stop()
        
    # -------------------------
    # FILTRO POR TIPO DE MÁQUINA
    # -------------------------

    tipos = sorted(list(set([m[2] for m in maquinas if m[2] is not None])))

    tipo_seleccionado = st.selectbox(
        "Tipo de máquina",
        tipos
    )

    maquinas_filtradas = [m for m in maquinas if m[2] == tipo_seleccionado]

    maquinas_dict = {f"{m[1]} - {m[2]} - {m[3]}": m for m in maquinas_filtradas}

    if not maquinas_filtradas:
        st.warning("No hay máquinas de este tipo.")
        st.stop()
    
    maquina_seleccionada = st.selectbox(
        "Seleccione la máquina",
        list(maquinas_dict.keys())
    )

    maquina = maquinas_dict[maquina_seleccionada]
    maquina_id = maquina[0]
    
    # =========================
    # HEADER
    # =========================

    indicadores = obtener_indicadores_maquina(maquina_id)
    ubicacion = obtener_ubicacion_maquina(maquina_id)
    ultimo_traslado = obtener_ultimo_traslado(maquina_id)

    # Datos máquina
    activo = maquina[1]
    tipo = maquina[2]
    equipo = maquina[3]

    titulo = f"{activo} | {tipo} {equipo}"

    st.markdown(f"## {titulo}")

    # Ubicación
    ciudad = ubicacion[0] if ubicacion else "-"
    sede = ubicacion[1] if ubicacion else "-"
    traslado = ultimo_traslado if ultimo_traslado else "Sin registros"
    
    # Información General
    modelo = maquina[4] if maquina[4] else "N/A"
    fabricante = maquina[5] if maquina[5] else "N/A"
    
    st.markdown(f"##### Fabricante: {fabricante} | Modelo: {modelo}")
    st.markdown(f"### 📍 **{ciudad} - {sede}** | Último traslado: {traslado}")

    # Métricas
    col1, col2, col3= st.columns(3)
    
    # Estado
    estado = indicadores["estado"]

    if estado == "Operativa":
        col1.metric("Estado", "🟢 Operativa")
    elif estado == "Operativa con falla":
        col1.metric("Estado", "🟡 Con falla")
    elif estado == "En mantenimiento":
        col1.metric("Estado", "🔧 Mantenimiento")
    else:
        col1.metric("Estado", "🔴 Fuera de servicio")

    # Fallas
    #col2.metric("Fallas", indicadores["fallas"])
    col2.metric("Mantenimientos Realizados", indicadores["mantenimientos"])

    ultimo_mant = indicadores["ultimo_mantenimiento"]
    if ultimo_mant:
        ultimo_mant = ultimo_mant.strftime("%Y-%m-%d")
    else:
        ultimo_mant = "Sin datos"
    # Mantenimientos
    col3.metric("Último mantenimiento", ultimo_mant)
    
    costo_total = obtener_costo_total_maquina(maquina_id)
    costo_formateado = f"{costo_total:,.0f}".replace(",", ".")

    # Costos
    #col4 .metric("Costo total de mantenimientos", f"${costo_formateado}")
    
    
    
    
    st.divider()
    st.markdown("### ⚠️ Resumen de solicitudes")

    ultimas = obtener_ultimas_solicitudes(maquina_id)

    col1, col2 = st.columns(2)

    col1.metric("Total solicitudes generadas", indicadores["fallas"])

    if indicadores["falla_top"] != "-":
        col2.metric(
            "Falla más frecuente",
            indicadores["falla_top"],
            f"{indicadores['falla_top_rep']} veces"
        )
    else:
        col2.metric("Falla más frecuente", "Sin datos")

    st.markdown("**Últimas solicitudes:**")

    for s in ultimas:
        st.write(f"- {s[0]} - {s[1]}")
        st.markdown(f"""
                <div style="padding:10px;border-radius:10px;background-color:#37374A;margin-bottom:8px">
                    <b> Item: {s[0]}</b><br>
                    📅 Fecha: {s[1]}<br>
                     
                </div>
                """, unsafe_allow_html=True)
    
    
    
    st.markdown("### 🔧 Historial de mantenimientos")

    mantenimientos = obtener_mantenimientos_con_solicitudes(maquina_id)

    total_general = 0

    if not mantenimientos:
        st.info("No hay mantenimientos")
    else:

        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.7,0.8,0.5,1.3,1,1.2,1])

        col1.write("Fecha")
        col2.write("Tipo")
        col3.write("Equipo")
        col4.write("Técnico")
        col5.write("Recibió")
        col6.write("Solicitudes cerradas")
        col7.write("Costo de Mantenimiento")

        for m in mantenimientos:

            costo = obtener_total_por_mantenimiento(m[0])
            total_general += costo

            costo_fmt = f"{costo:,.0f}".replace(",", ".")

            solicitudes = obtener_descripciones_solicitudes(m[7])

            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.7,0.8,0.5,1.3,1,1.2,1])

            col1.write(m[1])
            col2.write(m[3])
            col3.write(m[2])
            col4.write(m[4])
            col5.write(m[5])
            col6.write(solicitudes)
            col7.write(f"${costo_fmt}")

        st.divider()

        total_fmt = f"{total_general:,.0f}".replace(",", ".")
        st.markdown(f"### 💰 Total acumulado: ${total_fmt}") 
        
        
        
        
    # =========================
    # COSTOS / REPUESTOS
    # =========================

    st.markdown("### 📦 Costos recientes")

    costos = obtener_costos_por_maquina(maquina_id)

    if not costos:
        st.info("No hay costos registrados")
    else:

        for c in costos:

            tipo = c[0]
            descripcion = c[1]
            cantidad = c[2]
            unitario = c[3]
            total = c[4]
            fecha = c[5]

            total_fmt = f"{total:,.0f}".replace(",", ".")

            # 🔥 Lógica según tipo
            if tipo in ["Repuestos", "Insumos"]:

                st.markdown(f"""
                <div style="padding:10px;border-radius:10px;background-color:#37374A;margin-bottom:8px">
                    <b>{tipo}</b><br>
                    {descripcion}<br>
                    💰 ${total_fmt} | 📅 {fecha}
                </div>
                """, unsafe_allow_html=True)

            elif tipo == "Mano de obra":

                st.markdown(f"""
                <div style="padding:10px;border-radius:10px;background-color:#37374A;margin-bottom:8px">
                    <b>{tipo}</b><br>
                    {descripcion}<br>
                    💰 ${total_fmt} | 📅 {fecha}
                </div>
                """, unsafe_allow_html=True)

            else:

                st.markdown(f"""
                <div style="padding:10px;border-radius:10px;background-color:#37374A;margin-bottom:8px">
                    <b>{tipo}</b><br>
                    {descripcion}<br>
                    💰 ${total_fmt} | 📅 {fecha}
                </div>
                """, unsafe_allow_html=True)

            st.divider()
        
        
        