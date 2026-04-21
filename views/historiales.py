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
    resumen_estados_solicitudes,
    #Mantenimientos
    registrar_mantenimiento,
    obtener_mantenimientos_paginados,
    contar_mantenimientos,
    insertar_costo,
    obtener_costos_por_mantenimiento,
    obtener_todos_mantenimientos,
    obtener_mantenimientos_con_solicitudes, 
    obtener_descripciones_solicitudes,
    actualizar_costo,
    eliminar_costo,
    actualizar_mantenimiento,
    
    
    #Historial
    obtener_total_por_mantenimiento,
    #Dashboard 
    obtener_mantenimientos_por_maquina,
    obtener_solicitudes_por_maquina,
    obtener_checklists_por_maquina,
    obtener_traslados_por_maquina, 
    obtener_indicadores_maquina, 
    obtener_ubicacion_maquina, 
    obtener_ultimo_traslado,
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
from utils.export import generar_excel_solicitudes
from database import obtener_solicitudes_export
from utils.export import generar_excel_mantenimientos_pro
from database import obtener_mantenimientos_con_costos_export

def construir_mensaje_y_nombre(modo_filtro, ciudad, sede, tipo, maquina_texto):

    if modo_filtro == "Por ubicación":
        if ciudad != "Todas" and sede != "Todas":
            texto = f"para {ciudad} - {sede}"
            nombre = f"solicitudes_{ciudad}_{sede}"
        elif ciudad != "Todas":
            texto = f"para {ciudad}"
            nombre = f"solicitudes_{ciudad}"
        else:
            texto = "por ubicación"
            nombre = "solicitudes_ubicacion"

    elif modo_filtro == "Por tipo de máquina" and tipo and tipo != "Todos":
        texto = f"para {tipo}"
        nombre = f"solicitudes_{tipo}"

    elif modo_filtro == "Por máquina específica" and maquina_texto:
        texto = f"para {maquina_texto}"
        nombre = f"solicitudes_{maquina_texto}"

    else:
        texto = "completo"
        nombre = "solicitudes_completo"

    nombre = nombre.replace(" ", "_").replace("|", "").replace("-", "_")

    return texto, nombre


def vista_historial_solicitudes():
    st.subheader("Lista de solicitudes registradas")
    
    if "confirmar_export_solicitudes" not in st.session_state:
        st.session_state.confirmar_export_solicitudes = False

    if "excel_solicitudes" not in st.session_state:
        st.session_state.excel_solicitudes = None

    if "nombre_archivo" not in st.session_state:
        st.session_state.nombre_archivo = None

    if "texto_export" not in st.session_state:
        st.session_state.texto_export = ""
        
    ###
    
    col_filtros, col_resumen = st.columns([2,1])
    
    with col_filtros:
        # -------------------------
        # TIPO DE FILTRO
        # -------------------------
        modo_filtro = st.radio(
            "Tipo de filtro",
            ["Sin filtro", "Por ubicación", "Por tipo de máquina", "Por máquina específica"]
        )
        
        if "filtro_prev" not in st.session_state:
            st.session_state.filtro_prev = modo_filtro

        if st.session_state.filtro_prev != modo_filtro:
            st.session_state.pagina_solicitudes = 1
            st.session_state.filtro_prev = modo_filtro
        
        maquinas = obtener_maquinas()

        ciudad_sel = None
        sede_sel = None
        tipo_sel = None
        maquina_sel_val = None

        # -------------------------
        # SIN FILTRO
        # -------------------------
        if modo_filtro == "Sin filtro":
            pass

        # -------------------------
        # POR UBICACIÓN
        # -------------------------
        elif modo_filtro == "Por ubicación":

            # -------------------------
            # CIUDAD
            # -------------------------
            ciudades = ["Todas"] + sorted(list(set([m[8] for m in maquinas if m[8]])))
            ciudad_sel = st.selectbox("Ciudad", ciudades)

            # -------------------------
            # SEDES DEPENDIENTES
            # -------------------------
            if ciudad_sel == "Todas":
                sedes_filtradas = ["Todas"] + sorted(list(set([m[7] for m in maquinas if m[7]])))
            else:
                sedes_filtradas = ["Todas"] + sorted(list(set([
                    m[7] for m in maquinas if m[8] == ciudad_sel
                ])))

            sede_sel = st.selectbox("Sede", sedes_filtradas)

        # -------------------------
        # POR TIPO
        # -------------------------
        elif modo_filtro == "Por tipo de máquina":

            tipos = ["Todos"] + sorted(list(set([m[2] for m in maquinas])))
            tipo_sel = st.selectbox("Tipo de máquina", tipos)

        # -------------------------
        # POR MÁQUINA
        # -------------------------
        elif modo_filtro == "Por máquina específica":

            # -------------------------
            # FILTRO POR TIPO (OBLIGATORIO)
            # -------------------------
            tipos = ["Todos"] + sorted(list(set([m[2] for m in maquinas])))
            tipo_sel = st.selectbox("Tipo de máquina", tipos)

            # -------------------------
            # MÁQUINAS DEPENDIENTES DEL TIPO
            # -------------------------
            if tipo_sel == "Todos":
                maquinas_filtradas = maquinas
            else:
                maquinas_filtradas = [m for m in maquinas if m[2] == tipo_sel]

            maquinas_dict = {
                f"{m[2]} {m[3]}": m[3] for m in maquinas_filtradas
            }

            maquina_sel = st.selectbox(
                "Máquina",
                ["Todas"] + list(maquinas_dict.keys())
            )

            maquina_sel_val = maquinas_dict.get(maquina_sel, None)
    
    # Descargar historial
    st.divider()
    st.subheader("📥 Exportar historial")

    if st.button("Exportar historial de solicitudes"):
        maquina_texto = None
        if modo_filtro == "Por máquina específica" and maquina_sel != "Todas":
            maquina_texto = maquina_sel_val  # tu variable del selectbox
        texto, nombre = construir_mensaje_y_nombre(
            modo_filtro,
            None,  # fecha_inicio,
            None,  # fecha_fin,
            tipo_sel if tipo_sel != "Todos" else None,
            maquina_texto
        )
        st.session_state.confirmar_export_solicitudes = True
        st.session_state.texto_export = texto
        st.session_state.nombre_archivo = nombre 
        
    if st.session_state.confirmar_export_solicitudes:
        st.warning(
            f"¿Deseas descargar el historial de solicitudes de mantenimiento {st.session_state.texto_export}?"
        )
        col1, col2 = st.columns(2)
        # CONFIRMAR
        with col1:
            if st.button("✅ Descargar"):

                data = obtener_solicitudes_export(
                    ciudad_sel,
                    sede_sel,
                    tipo_sel,
                    maquina_sel_val
                )

                st.session_state.excel_solicitudes = generar_excel_solicitudes(data)
                st.session_state.confirmar_export_solicitudes = False

        # CANCELAR
        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_export_solicitudes = False
                st.rerun()
                
    if st.session_state.excel_solicitudes:
        st.download_button(
            label="⬇️ Descargar archivo",
            data=st.session_state.excel_solicitudes,
            file_name=f"{st.session_state.nombre_archivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )    
        ## Hasta acá va descargar       
    
    with col_resumen:

        st.markdown("### 📊 Resumen")

        pendientes, cerradas, total_resumen = resumen_estados_solicitudes(
            ciudad_sel,
            sede_sel,
            tipo_sel,
            maquina_sel_val
        )

        st.markdown(f"""
        <div style="background-color:#37374A;padding:10px;border-radius:10px;margin-bottom:8px">
            🔴 <b>Pendientes:</b> {pendientes}
        </div>
        <div style="background-color:#37374A;padding:10px;border-radius:10px;margin-bottom:8px">
            🟢 <b>Cerradas:</b> {cerradas}
        </div>
        <div style="background-color:#37374A;padding:10px;border-radius:10px">
            📊 <b>Total:</b> {total_resumen}
        </div>
        """, unsafe_allow_html=True)
           
    # -------------------------
    # PAGINACIÓN
    # -------------------------
    registros_por_pagina = 10

    if "pagina_solicitudes" not in st.session_state:
        st.session_state.pagina_solicitudes = 1

    pagina = st.session_state.pagina_solicitudes

    total = contar_solicitudes_filtradas(
        ciudad_sel,
        sede_sel,
        tipo_sel,
        maquina_sel_val
        )
    
    st.markdown(f"🔎 **{total} resultados**")
    
        
    
    total_paginas = max(1, (total + registros_por_pagina - 1) // registros_por_pagina)

    colA, colB, colC = st.columns([1,2,1])

    if colA.button("⬅ Anterior") and pagina > 1:
        st.session_state.pagina_solicitudes -= 1
        st.rerun()

    colB.markdown(f"**Página {pagina} de {total_paginas}**")

    if colC.button("Siguiente ➡") and pagina < total_paginas:
        st.session_state.pagina_solicitudes += 1
        st.rerun()

    # -------------------------
    # DATA
    # -------------------------
    solicitudes = obtener_solicitudes_filtradas(
        ciudad_sel,
        sede_sel,
        tipo_sel,
        maquina_sel_val,
        pagina,
        registros_por_pagina
    )

    # -------------------------
    # TABLA
    # -------------------------
    if not solicitudes:
        st.info("No hay solicitudes registradas")
    else:

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

        col1.write("ID")
        col2.write("Máquina")
        col3.write("Tipo")
        col4.write("Descripción")
        col5.write("Veces repetida")
        col6.write("Origen")
        col7.write("Fecha")
        col8.write("Estado")

        for s in solicitudes:

            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

            col1.write(s[0])
            col2.write(s[1])
            col3.write(s[2])

            if s[3]:
                partes = s[3].split(" - ", 1)
                item = partes[0].upper()
                observacion = partes[1].lower() if len(partes) > 1 else ""

                col4.markdown(f"""
                <div>
                    <b>{item}</b><br>
                    <span style='color:gray'>→ {observacion}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                col4.write("")

            if s[4] > 1:
                col5.markdown(f"<span style='background-color:#E1B102;padding:4px 8px;border-radius:6px'>{s[4]} rep.</span>", unsafe_allow_html=True)
            else:
                col5.markdown(f"**{s[4]} rep.**")

            col6.write(s[5])
            col7.write(s[6])

            col8.markdown("🔴 Pendiente" if s[7] == "Pendiente" else "🟢 Cerrada")

def vista_historial_mantenimientos():
    st.subheader("Últimos mantenimientos")
    
    if "confirmar_export_mantenimientos" not in st.session_state:
        st.session_state.confirmar_export_mantenimientos = False
    if "excel_mantenimientos" not in st.session_state:
        st.session_state.excel_mantenimientos = None
    if "nombre_archivo_mant" not in st.session_state:
        st.session_state.nombre_archivo_mant = None
    if "texto_export_mant" not in st.session_state:
        st.session_state.texto_export_mant = ""
        
    
    
    st.subheader("Historial de mantenimientos")
    # -------------------------
    # FILTROS
    # -------------------------
    modo_filtro = st.radio(
        "Filtrar mantenimientos",
        ["Mostrar todos", "Por tipo de máquina", "Por máquina específica"]
    )

    maquinas = obtener_maquinas()

    tipo_sel = None
    maquina_id = None
    maquina_texto = None

    if modo_filtro == "Por tipo de máquina":
        tipos = ["Seleccione una opción"] + sorted(list(set([m[2] for m in maquinas])))
        tipo_sel = st.selectbox("Tipo de máquina", tipos)

    elif modo_filtro == "Por máquina específica":

        tipos = sorted(list(set([m[2] for m in maquinas])))
        tipo_sel = st.selectbox("Tipo de máquina", tipos)

        maquinas_filtradas = [m for m in maquinas if m[2] == tipo_sel]

        maquinas_dict = {
            f"{m[2]} {m[3]}": m[0] for m in maquinas_filtradas
        }

        maquina_texto = st.selectbox("Máquina", list(maquinas_dict.keys()))
        maquina_id = maquinas_dict[maquina_texto]
    
    
    
    
    
    
    
    
    
    
    registros_por_pagina = 15
    # Obtener total de registros
    
    if modo_filtro == "Mostrar todos":
        mantenimientos_all = obtener_mantenimientos_con_solicitudes()

    elif modo_filtro == "Por tipo de máquina":
        mantenimientos_all = [
            m for m in obtener_mantenimientos_con_solicitudes()
            if m[4] == tipo_sel
        ]

    elif modo_filtro == "Por máquina específica":
        mantenimientos_all = obtener_mantenimientos_con_solicitudes(maquina_id)

    total_registros = len(mantenimientos_all)
    
    
    

    # Calcular número total de páginas
    total_paginas = max(1, (total_registros + registros_por_pagina - 1) // registros_por_pagina)

    # Inicializar página
    if "pagina_mantenimientos" not in st.session_state:
        st.session_state.pagina_mantenimientos = 1

    pagina = st.session_state.pagina_mantenimientos
    
    inicio = (pagina - 1) * registros_por_pagina
    fin = inicio + registros_por_pagina

    mantenimientos = mantenimientos_all[inicio:fin]

    # Botones de navegación
    colA, colB, colC = st.columns([1,2,1])

    if colA.button("⬅ Anterior") and pagina > 1:
        st.session_state.pagina_mantenimientos -= 1
        st.rerun()

    colB.markdown(f"**Página {pagina} de {total_paginas}**")

    if colC.button("Siguiente ➡") and pagina < total_paginas:
        st.session_state.pagina_mantenimientos += 1
        st.rerun()

    
    # Mostrar tabla
    if not mantenimientos:
        st.info("Aún no hay mantenimientos registrados.")

    else:
        maquinas = obtener_maquinas()
        # Mapa: (tipo, numero_equipo) → ciudad
        mapa_ciudad = {
            (m[2], m[3]): m[8] for m in maquinas
        }

        col1, col2, col3, col4, col5, col6 = st.columns([1.5,1.5,2,4,2,1])

        col1.write("Fecha")
        col2.write("Ciudad")
        col3.write("Máquina")
        col4.write("Observaciones")
        col5.write("Costo Total")
        col6.write("Detalles")

        for m in mantenimientos:

            # Datos base
            mant_id = m[0]
            fecha = m[1]
            equipo = m[2]
            tipo = m[3]
            observaciones = m[6]

            # Ciudad
            ciudad = mapa_ciudad.get((tipo, equipo), "N/A")

            # Máquina formato
            maquina_texto = f"{tipo} {equipo}"

            # Costo total
            total = obtener_total_por_mantenimiento(mant_id)
            total_formateado = f"${int(total):,}".replace(",", ".")

            # -------------------------
            # FILA
            # -------------------------
            col1, col2, col3, col4, col5, col6 = st.columns([1.5,1.5,2,4,2,1])

            col1.write(fecha)
            col2.write(ciudad)
            col3.write(maquina_texto)

            # Observaciones (mejor formato)
            if observaciones:
                col4.markdown(f"""
                <div>
                    {observaciones[:60]}{"..." if len(observaciones) > 60 else ""}
                </div>
                """, unsafe_allow_html=True)
            else:
                col4.write("-")

            col5.write(total_formateado)

            if col6.button("Ver", key=f"det_{mant_id}"):
                st.session_state.ver_detalle = mant_id
            
            if "ver_detalle" in st.session_state:

                mant_id = st.session_state.ver_detalle

                mantenimiento = next((m for m in mantenimientos_all if m[0] == mant_id), None)

                if mantenimiento:
                    st.divider()
                    
                    col_titulo, col_cerrar = st.columns([5,1])

                    with col_titulo:
                        st.subheader(f"Detalle mantenimiento #{mant_id}")

                    with col_cerrar:
                        if st.button("❌", key="cerrar_detalle"):
                            del st.session_state.ver_detalle
                            st.rerun()

                    st.write(f"🔧 Máquina: {mantenimiento[3]} {mantenimiento[2]}")
                    st.write(f"📅 Fecha: {mantenimiento[1]}")
                    st.write(f"👨‍🔧 Técnico: {mantenimiento[4]}")
                    st.write(f"📦 Recibido por: {mantenimiento[5]}")
                    st.write(f"📋 Observaciones: {mantenimiento[6]}")

                    costos = obtener_costos_por_mantenimiento(mant_id)

                    if costos:
                        for c in costos:
                            st.write(f"{c[2]} - {c[3]} → ${int(c[6]):,}".replace(",", "."))
                    else:
                        st.info("Sin costos registrados")
                        
    st.divider()
    st.subheader("📥 Exportar mantenimientos")

    if st.button("Exportar historial de mantenimientos"):

        if modo_filtro == "Por máquina específica":
            texto = f"para {maquina_texto}"
            nombre = f"mantenimientos_{maquina_texto}"
            maquina_id_export = maquina_id

        elif modo_filtro == "Por tipo de máquina":
            texto = f"para {tipo_sel}"
            nombre = f"mantenimientos_{tipo_sel}"
            maquina_id_export = None

        else:
            texto = "completo"
            nombre = "mantenimientos_completo"
            maquina_id_export = None

        st.session_state.confirmar_export_mantenimientos = True
        st.session_state.texto_export_mant = texto
        st.session_state.nombre_archivo_mant = nombre
        st.session_state.maquina_id_export = maquina_id_export    
            
    
    
    st.divider()

    if "mostrar_edicion" not in st.session_state:
        st.session_state.mostrar_edicion = False

    if st.button("✏️ Editar mantenimiento"):
        st.session_state.mostrar_edicion = not st.session_state.mostrar_edicion

    if st.session_state.mostrar_edicion:
  
        col1, col2 = st.columns([5,1])

        with col1:
            st.subheader("Edición de mantenimiento")

        with col2:
            if st.button("❌ Cerrar edición"):
                st.session_state.mostrar_edicion = False
                st.rerun()
                
        st.write("### 🔎 Filtrar mantenimiento")
        
        modo = st.radio(
            "Modo de búsqueda",
            ["Filtrar por máquina", "Ver todos los mantenimientos"]
        )
        
        #-----------------------------------
        if modo == "Filtrar por máquina":

            maquinas = obtener_maquinas()
            
            if not maquinas:
                st.warning("No hay máquinas registradas.")
                return

            # FILTRAR POR TIPO
            tipos = sorted(list(set([m[2] for m in maquinas])))
            tipo_sel_edit = st.selectbox("Tipo de máquina", tipos, key="tipo_edit")

            maquinas_tipo = [m for m in maquinas if m[2] == tipo_sel]

            # FILTRAR POR EQUIPO
            maquinas_dict = {
                f"{m[1]} | Equipo #{m[3]}": m[0] for m in maquinas_tipo
            }

            if maquinas_dict:
                maquina_sel = st.selectbox(
                    "Equipo",
                    list(maquinas_dict.keys())
                )

                maquina_id = maquinas_dict[maquina_sel]
            else:
                st.info("No hay máquinas de este tipo.")
                return

            # 🔥 AQUÍ ESTÁ LA CLAVE
            mantenimientos_all = obtener_mantenimientos_con_solicitudes(maquina_id)

        else:
            mantenimientos_all = obtener_mantenimientos_con_solicitudes()


        # 🔥 CREAR LABELS CON SOLICITUDES (UNA SOLA VEZ)
        mantenimientos_dict = {}

        for m in mantenimientos_all:
            
            solicitudes_ids = m[7] if m[7] else None
            solicitudes_txt = obtener_descripciones_solicitudes(solicitudes_ids)

            # limitar texto (opcional)
            if len(solicitudes_txt) > 40:
                solicitudes_txt = solicitudes_txt[:40] + "..."

            label = f"{m[1]} | {m[3]} {m[2]} | {solicitudes_txt}"

            mantenimientos_dict[label] = m

        if not mantenimientos_dict:
            st.info("No hay mantenimientos registrados.")
            return
        
        mantenimiento_sel = st.selectbox(
            "Selecciona mantenimiento",
            list(mantenimientos_dict.keys())
        )

        mantenimiento = mantenimientos_dict[mantenimiento_sel]

        if "edit_mantenimiento" not in st.session_state:
            st.session_state.edit_mantenimiento = False
        
        
        
        st.write("### Información")
        # -------------------------
        # MODO EDICIÓN
        # -------------------------
        if st.session_state.edit_mantenimiento:

            nuevo_tecnico = st.text_input("Técnico", value=mantenimiento[4])
            nuevo_recibido = st.text_input("Recibido por", value=mantenimiento[5])  # si no lo tienes en query
            nuevas_obs = st.text_area("Observaciones", value=mantenimiento[6])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Guardar cambios mantenimiento"):

                    actualizar_mantenimiento(
                        mantenimiento[0],
                        nuevo_tecnico.strip(),
                        nuevo_recibido.strip(),
                        nuevas_obs.strip().capitalize()
                    )

                    st.session_state.edit_mantenimiento = False
                    st.session_state.mostrar_edicion = False
                    st.success("Mantenimiento actualizado")
                    st.rerun()

            with col2:
                if st.button("❌ Cancelar"):
                    st.session_state.edit_mantenimiento = False
                    st.rerun()

        # -------------------------
        # MODO NORMAL
        # -------------------------
        else:

            st.write(f"📅 Fecha: {mantenimiento[1]}")
            st.write(f"🔧 Máquina: {mantenimiento[3]} {mantenimiento[2]}")
            st.write(f"👨‍🔧 Técnico: {mantenimiento[4]}")
            st.write(f"📦 Recibido por: {mantenimiento[5]}")
            st.write(f"📋 Observaciones: {mantenimiento[6]}")

            if st.button("✏️ Editar información mantenimiento"):
                st.session_state.edit_mantenimiento = True
                st.rerun()
        
        
        costos_existentes = obtener_costos_por_mantenimiento(mantenimiento[0])

        st.write("### 💰 Costos actuales")
        
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = None
            
        if "edit_costo_id" not in st.session_state:
            st.session_state.edit_costo_id = None

        for i, c in enumerate(costos_existentes):

            col1, col2, col3 = st.columns([4,1,1])

            # -------------------------
            # MODO EDICIÓN
            # -------------------------
            if st.session_state.edit_costo_id == c[0]:

                tipo = c[2]

                with col1:

                    nueva_desc = st.text_input("Descripción",value=c[3],key=f"edit_desc_{c[0]}"
                    )

                    # -------------------------
                    # MANO DE OBRA
                    # -------------------------
                    if tipo == "Mano de obra":

                        nueva_cant = st.number_input("Cantidad",value=1.0,disabled=True,key=f"edit_cant_mo_{c[0]}"
                        )
                        nuevo_costo = st.text_input("Valor",value=str(int(c[5])),key=f"edit_costo_mo_{c[0]}"
                        )

                    # -------------------------
                    # REPUESTOS / INSUMOS
                    # -------------------------
                    elif tipo in ["Repuestos", "Insumos"]:

                        nueva_cant = st.number_input("Cantidad",min_value=1.0,value=max(1.0, float(c[4])),step=1.0,key=f"edit_cant_{c[0]}"
                        )
                        nuevo_costo = st.text_input("Costo unitario",value=str(int(c[5])),key=f"edit_costo_{c[0]}"
                        )

                    # -------------------------
                    # SIN COSTO
                    # -------------------------
                    elif tipo == "Sin costo":

                        nueva_cant = 1
                        st.number_input( "Cantidad", value=1, disabled=True, key=f"edit_cant_sc_{c[0]}"
                        )
                        st.text_input("Costo",value="0",disabled=True,key=f"edit_costo_sc_{c[0]}"
                        )
                        nuevo_costo = 0
                        
                with col2:
                    if st.button("💾", key=f"save_{c[0]}"):

                        def limpiar_numero(valor):
                            valor = valor.replace(".", "").replace(",", "")
                            return float(valor) if valor else 0

                        if tipo != "Sin costo":
                            nuevo_costo = limpiar_numero(str(nuevo_costo))
                        else:
                            nuevo_costo = 0
                            
                        if tipo in ["Repuestos", "Insumos"] and nueva_cant <= 0:
                            st.error("La cantidad debe ser mayor a 0")
                            st.stop()

                        actualizar_costo(
                            c[0],
                            nueva_desc.strip().capitalize(),
                            nueva_cant,
                            nuevo_costo
                        )

                        st.session_state.edit_costo_id = None
                        st.success("Costo actualizado")
                        st.rerun()

                with col3:
                    if st.button("❌", key=f"cancel_{c[0]}"):
                        st.session_state.edit_costo_id = None
                        st.rerun()

            # -------------------------
            # MODO NORMAL
            # -------------------------
            else:

                with col1:
                    total = float(c[6])
                    total_formateado = f"{total:,.0f}".replace(",", ".")
                    st.write(f"{c[2]} - {c[3]} → ${total_formateado}")

                with col2:
                    if st.button("✏️", key=f"edit_{c[0]}"):
                        st.session_state.edit_costo_id = c[0]
                        st.rerun()

                with col3:
                    if st.button("🗑️", key=f"btn_del_{c[0]}"):
                        st.session_state.confirm_delete = c[0]

        # -------------------------
        # CONFIRMACIÓN
        # -------------------------
        if st.session_state.confirm_delete is not None:

            # Buscar el costo seleccionado
            costo_sel = next(
                (c for c in costos_existentes if c[0] == st.session_state.confirm_delete),
                None
            )

            if costo_sel:
                total = float(costo_sel[6])
                total_formateado = f"{total:,.0f}".replace(",", ".")

                st.warning(
                    f"⚠️ ¿Eliminar este costo?\n\n"
                    f"{costo_sel[2]} - {costo_sel[3]} → ${total_formateado}"
                )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Sí, eliminar"):
                    eliminar_costo(st.session_state.confirm_delete)
                    st.session_state.confirm_delete = None
                    st.success("Costo eliminado")
                    st.rerun()

            with col2:
                if st.button("❌ Cancelar"):
                    st.session_state.confirm_delete = None
                    st.rerun()
            
        # =========================
        # AGREGAR NUEVOS COSTOS
        # =========================

        st.write("### ➕ Agregar nuevos costos")

        # Inicializar memoria
        if "costos_edit" not in st.session_state:
            st.session_state.costos_edit = []

        tipo_costo_edit = st.selectbox(
            "Tipo de costo (edición)",
            ["Mano de obra", "Repuestos", "Insumos", "Sin costo"],
            key="tipo_costo_edit"
        )

        # Reset al cambiar tipo
        if "tipo_costo_edit_prev" not in st.session_state:
            st.session_state.tipo_costo_edit_prev = tipo_costo_edit

        if st.session_state.tipo_costo_edit_prev != tipo_costo_edit:
            for key in ["desc_edit", "cant_edit", "costo_edit"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.tipo_costo_edit_prev = tipo_costo_edit

        # -------------------------
        # CAMPOS DINÁMICOS
        # -------------------------
        cantidad = 1
        costo_unitario = 0

        if tipo_costo_edit == "Mano de obra":
            descripcion = st.text_input("Descripción", key="desc_edit")
            st.number_input("Cantidad", value=1, disabled=True, key="cantidad_disabled_edit")
            costo_unitario = st.text_input("Valor", key="costo_edit")

        elif tipo_costo_edit in ["Repuestos", "Insumos"]:
            descripcion = st.text_input("Nombre del ítem", key="desc_edit")
            st.number_input("Cantidad", value=1, disabled=True, key="cantidad_sc_edit")
            costo_unitario = st.text_input("Costo unitario", key="costo_edit")

        elif tipo_costo_edit == "Sin costo":
            descripcion = st.text_input("Descripción", key="desc_edit")
            st.number_input("Cantidad", value=1, disabled=True)
            st.text_input("Costo", value="0", disabled=True, key="costo_sc_edit")

        # -------------------------
        # BOTÓN AGREGAR
        # -------------------------
        if st.button("➕ Agregar costo (edición)"):

            if not descripcion.strip():
                st.error("Debe agregar descripción")
                st.stop()

            def limpiar_numero(valor):
                valor = valor.replace(".", "").replace(",", "")
                return float(valor) if valor else 0

            costo_unitario = limpiar_numero(str(costo_unitario))

            st.session_state.costos_edit.append({
                "tipo": tipo_costo_edit,
                "descripcion": descripcion.strip().capitalize(),
                "cantidad": cantidad,
                "costo_unitario": costo_unitario
            })

            st.rerun()

        # -------------------------
        # MOSTRAR COSTOS NUEVOS
        # -------------------------
        if st.session_state.costos_edit:

            st.write("### 🧾 Nuevos costos a agregar")

            for i, c in enumerate(st.session_state.costos_edit):

                col1, col2 = st.columns([4,1])

                with col1:
                    total = float(c["cantidad"]) * float(c["costo_unitario"])
                    total_formateado = f"{total:,.0f}".replace(",", ".")
                    st.write(f"{c['tipo']} - {c['descripcion']} → ${total_formateado}")

                with col2:
                    if st.button("❌", key=f"del_edit_{i}"):
                        st.session_state.costos_edit.pop(i)
                        st.rerun()

        # -------------------------
        # GUARDAR NUEVOS COSTOS
        # -------------------------
        if st.button("💾 Guardar nuevos costos"):

            for c in st.session_state.costos_edit:
                insertar_costo(
                    mantenimiento[0],
                    c["tipo"],
                    c["descripcion"],
                    c["cantidad"],
                    c["costo_unitario"]
                )

            st.session_state.costos_edit = []

            st.success("Costos agregados correctamente")
            st.rerun()
        
        