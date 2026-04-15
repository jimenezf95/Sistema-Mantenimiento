

from database import (
    crear_tablas,
    #Maquinaria
    insertar_maquina, 
    obtener_maquinas,
    obtener_maquina_por_id, 
    eliminar_maquina,
    actualizar_maquina,
    conteo_maquinas_por_sede,
    #Sedes 
    insertar_sede, 
    obtener_sedes,
    sede_tiene_maquinas, 
    eliminar_sede,
    #Traslados
    insertar_traslado,
    obtener_traslados,
    obtener_ultimos_traslados,
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
    #Mantenimientos
    registrar_mantenimiento,
    obtener_mantenimientos_paginados,
    contar_mantenimientos,
    insertar_costo,
    obtener_costos_por_mantenimiento,
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
    obtener_costos_dashboard,
)

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from config_checklist import checklists_por_tipo

# Definir tipos de máquina
TIPOS_MAQUINA = [
    "Compactadora",
    "Montacargas",
    "Cizalladora",
    "Briqueteadora",
    "Herramienta Manual y Potencia",
    "Equipo Oxicorte",
    "Otro"
]

ESTADOS_OPERACION = [
    "Operativa",
    "Operativa con falla",
    "En mantenimiento",
    "Fuera de servicio"
]

if "editar_maquina_id" not in st.session_state:
    st.session_state.editar_maquina_id = None

st.set_page_config(
    page_title="Sistema de Gestión de Mantenimiento",
    layout="wide"
)

crear_tablas()

# Título página principal
st.title("Sistema de Gestión de Mantenimiento de Maquinaria")

# Menú lateral
st.sidebar.title("Menú del sistema")
opcion = None
# -----------------------------
# INICIO
# -----------------------------
if st.sidebar.button("🏠 Inicio"):
    st.session_state.opcion = "Inicio" 
# -----------------------------
# MAQUINARIA
# -----------------------------   
with st.sidebar.expander("Maquinaria"):
    
    if st.button("Inventario de Máquinas"):
        st.session_state.opcion = "Inventario de Máquinas"
        
    if st.button("Control de traslados"):
        st.session_state.opcion = "Control de Traslados"

    if st.button("Registro de Sedes"):
        st.session_state.opcion = "Registro de Sedes"

    if st.button("Registro de Maquinaria"):
        st.session_state.opcion = "Registro de Maquinaria"
# -----------------------------
# MANTENIMIENTO
# -----------------------------
with st.sidebar.expander("Mantenimiento"):
    
    if st.button("Checklists Diarias"):
        st.session_state.opcion = "Checklists Diarias"

    if st.button("Solicitudes de Mantenimiento"):
        st.session_state.opcion = "Solicitudes de Mantenimiento"

    if st.button("Registro de Mantenimientos"):
        st.session_state.opcion = "Registro de Mantenimientos"
# -----------------------------
# REPORTES
# -----------------------------
with st.sidebar.expander("Reportes"):
    
    if st.button("Dashboard de Análisis"):
        st.session_state.opcion = "Dashboard de Análisis"
    
    if st.button("Historial de Mantenimientos"):
        st.session_state.opcion = "Historial de Mantenimientos"

    if st.button("Historial de Solicitudes"):
        st.session_state.opcion = "Historial de Solicitudes"

    if st.button("Hoja de Vida de Equipos"):
        st.session_state.opcion = "Hoja de Vida de Equipos"
        
    if st.button("Dashboard de Costos"):
        st.session_state.opcion = "Dashboard de Costos"
if "opcion" not in st.session_state:
    st.session_state.opcion = "Inicio"
opcion = st.session_state.opcion




if opcion == "Inicio":
    st.header("Bienvenido al sistema")

    st.write("Este sistema permite gestionar el mantenimiento de maquinaria de la empresa.")

    st.subheader("Funciones principales")

    st.write("✔ Registro de maquinaria")
    st.write("✔ Registro de checklists diarias")
    st.write("✔ Registro de mantenimientos")
    st.write("✔ Control de traslado entre sedes")
    st.write("✔ Análisis de fallas")
    st.write("✔ Historial de mantenimiento por máquina")

elif opcion == "Registro de Maquinaria":

    st.header("Registro de Maquinaria")

    st.subheader("Agregar nueva máquina")

    sedes = obtener_sedes()
    if not sedes: 
        st.warning("⚠️ Debe registrar al menos una sede antes de crear una máquina.") 
        st.stop()
    
    sede_nombres = {f"{sede[1]} - {sede[2]}": sede[0] for sede in sedes}

    with st.form("form_maquina", clear_on_submit=True):
        #FORMULARIO REGISTRO MAQUINARIA
        tipo = st.selectbox("Tipo de máquina",TIPOS_MAQUINA)
        activo_fijo = st.text_input("ID Activo Fijo (Contable)")
        numero_equipo = st.text_input("Número de equipo")
        modelo = st.text_input("Modelo")
        fabricante = st.text_input("Fabricante")

        estado_operacion = st.selectbox(
            "Estado de operación",
            ESTADOS_OPERACION
        )

        sede_seleccionada = st.selectbox(
            "Sede",
            list(sede_nombres.keys())
        )

        submitted = st.form_submit_button("Registrar máquina")

        if submitted:
            if activo_fijo.strip() == "":
                st.error("El ID Activo Fijo es obligatorio.")
                st.stop()
            
            maquina_id = insertar_maquina(
                tipo,
                activo_fijo,
                numero_equipo,
                modelo,
                fabricante,
                estado_operacion,
                sede_nombres[sede_seleccionada]
            )
            # Obtener la maquina recién creada
            maquinas_actualizadas = obtener_maquinas()
            #maquina_id = maquinas_actualizadas[-1][0] 
            actualizar_estado_maquina(maquina_id, estado_operacion)
            
            st.success("Máquina registrada correctamente")

    st.subheader("Maquinaria registrada")

    maquinas = obtener_maquinas()

    # Encabezados de la tabla
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1.5, 2, 1, 2, 1.5, 2, 1.5, 1.5, 1.5, 2]) #Ajustar ancho de columnas
    #col1.write("ID Interno")
    col1.write("ID Activo")
    col2.write("Tipo")
    col3.write("Equipo")
    col4.write("Modelo")
    col5.write("Fabricante")
    col6.write("Estado")
    col7.write("Sede")
    col8.write("Ciudad")
    col9.write("")
    col10.write("")

    # Tabla de máquinas
    for maquina in maquinas:
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1.5, 2, 1, 2, 1.5, 2, 1.5, 1.5, 1.5, 2]) #Ajustar ancho de columnas
        #col1.write(maquina[0]) #Id interno
        col1.write(maquina[1]) #ID Activo Fijo
        col2.markdown(f"<div style='white-space:nowrap'>{maquina[2]}</div>", unsafe_allow_html=True)
        col3.markdown(f"<div style='white-space:nowrap'>{maquina[3]}</div>", unsafe_allow_html=True)
        col4.markdown(f"<div style='white-space:nowrap'>{maquina[4]}</div>", unsafe_allow_html=True)
        col5.markdown(f"<div style='white-space:nowrap'>{maquina[5]}</div>", unsafe_allow_html=True)
        col6.write(maquina[6]) #Estado
        col7.write(maquina[7]) #Sede
        col8.write(maquina[8]) #Ciudad

        if col9.button("Editar", key=f"edit_{maquina[0]}"):
            st.session_state.editar_maquina_id = maquina[0]

        # Botón de eliminar con confirmación
        if col10.button("Eliminar", key=f"maq_{maquina[0]}"):
            st.session_state["confirm_delete_maquina_id"] = maquina[0]

        if "confirm_delete_maquina_id" in st.session_state and st.session_state["confirm_delete_maquina_id"] == maquina[0]:
            st.warning("¿Seguro que quieres eliminar esta máquina?")
            col_confirm, col_cancel = st.columns([1,1])

            if col_confirm.button("Confirmar", key=f"confirm_maquina_{maquina[0]}"):
                eliminar_maquina(maquina[0])
                del st.session_state["confirm_delete_maquina_id"]
                st.rerun()

            if col_cancel.button("Cancelar", key=f"cancel_maquina_{maquina[0]}"):
                del st.session_state["confirm_delete_maquina_id"]
                st.rerun()

    # Formulario de edición de máquina
    if st.session_state.editar_maquina_id is not None:

        st.subheader("Editar máquina")

        maquina_editar = None
        for m in maquinas:
            if m[0] == st.session_state.editar_maquina_id:
                maquina_editar = m
                break

        sedes = obtener_sedes()
        sede_nombres = {f"{sede[1]} - {sede[2]}": sede[0] for sede in sedes}

        with st.form("form_editar_maquina"):

            tipo = st.selectbox(
                "Tipo de máquina",
            TIPOS_MAQUINA,
            index=TIPOS_MAQUINA.index(maquina_editar[2]) if maquina_editar[2] in TIPOS_MAQUINA else 0
            )

            activo_fijo = st.text_input(
                "ID Activo Fijo (Contable)",
                value=maquina_editar[1]
            )

            numero_equipo = st.text_input(
                "Número de equipo",
                value=maquina_editar[3]
            )

            modelo = st.text_input(
                "Modelo",
                value=maquina_editar[4]
            )

            fabricante = st.text_input(
                "Fabricante",
                value=maquina_editar[5]
            )

            estado_operacion = st.selectbox(
                "Estado de operación",
                ESTADOS_OPERACION,
                index=ESTADOS_OPERACION.index(maquina_editar[6]) if maquina_editar[6] in ESTADOS_OPERACION else 0
            )

            sede_seleccionada = st.selectbox(
                "Sede",
                list(sede_nombres.keys())
            )

            submitted = st.form_submit_button("Guardar cambios")

            if submitted:

                if activo_fijo.strip() == "":
                    st.error("El ID Activo Fijo es obligatorio")
                    st.stop()

                actualizar_maquina(
                    st.session_state.editar_maquina_id,
                    tipo,
                    activo_fijo,
                    numero_equipo,
                    modelo,
                    fabricante,
                    estado_operacion,
                    sede_nombres[sede_seleccionada]
                )

                actualizar_estado_maquina(
                    st.session_state.editar_maquina_id,
                    estado_operacion
                )

                st.success("Máquina actualizada correctamente")
                st.session_state.editar_maquina_id = None
                st.rerun()

elif opcion == "Registro de Sedes":

    st.header("Registro de Sedes")

    st.subheader("Agregar nueva sede")

    with st.form("form_sede", clear_on_submit=True):

        nombre = st.text_input("Nombre de la sede")

        ciudad = st.text_input("Ciudad")

        submitted = st.form_submit_button("Registrar sede")

        if submitted:

            insertar_sede(nombre, ciudad)

            st.success("Sede registrada correctamente")
        
            #st.rerun()

    st.subheader("Sedes registradas")

    sedes = obtener_sedes()
    
    col1, col2, col3 = st.columns(3)
    col1.write("Sede")
    col2.write("Ciudad")
    col3.write("")

    for sede in sedes:         
        col1, col2, col3 = st.columns(3)

        col1.write(sede[1])
        col2.write(sede[2])
        col3.write("") #Espacio para botones

        # Primer botón de eliminar
        if col3.button("Eliminar", key=f"sede_{sede[0]}"):
            st.session_state["confirm_delete_sede_id"] = sede[0]

        # Confirmación de eliminación
        if "confirm_delete_sede_id" in st.session_state and st.session_state["confirm_delete_sede_id"] == sede[0]:
            st.warning("¿Seguro que quieres eliminar esta sede?")
            col_confirm, col_cancel = st.columns([1,1])

            if col_confirm.button("Confirmar", key=f"confirm_sede_{sede[0]}"):
                
                cantidad = sede_tiene_maquinas(sede[0])
                if cantidad > 0:
                    st.error("No se puede eliminar esta sede porque tiene máquinas registradas.")
                else:
                    eliminar_sede(sede[0])
                    st.success("Sede eliminada correctamente")
                    del st.session_state["confirm_delete_sede_id"]
                    st.rerun()

            if col_cancel.button("Cancelar", key=f"cancel_sede_{sede[0]}"):
                del st.session_state["confirm_delete_sede_id"]
                st.rerun()

elif opcion == "Inventario de Máquinas":
    
    ## Dashboard con conteo de máquinas por sede
    st.subheader("Distribución de maquinaria por sede")
    conteo = conteo_maquinas_por_sede()
    for c in conteo:
        st.metric(
            label=f"{c[1]} ({c[0]})",
            value=f"{c[2]} máquinas"
        )
        
    ## Tabla de máquinas con filtros
    st.header("Inventario de Máquinas")
    maquinas = obtener_maquinas()
    sedes = obtener_sedes()

    filtro_sede = st.selectbox(
        "Filtrar por sede",
        ["Todas"] + [sede[1] for sede in sedes]
    )

    filtro_tipo = st.selectbox(
        "Filtrar por tipo de máquina",
        ["Todos"] + TIPOS_MAQUINA
    )

    maquinas_filtradas = []

    for m in maquinas:

        sede = m[7] # Sede  
        tipo = m[2] # Tipo de máquina

        if filtro_sede != "Todas" and sede != filtro_sede:
            continue

        if filtro_tipo != "Todos" and tipo != filtro_tipo:
            continue

        maquinas_filtradas.append(m)

    st.subheader("Máquinas registradas")

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    col1.write("ID Activo")
    col2.write("Tipo")
    col3.write("Equipo")
    col4.write("Modelo")
    col5.write("Fabricante")
    col6.write("Estado")
    col7.write("Sede")
    col8.write("Ciudad")

    for m in maquinas_filtradas:

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

        col1.write(m[1]) # ID Activo 
        col2.markdown(f"<div style='white-space:nowrap'>{m[2]}</div>", unsafe_allow_html=True) # Tipo máquina
        col3.markdown(f"<div style='white-space:nowrap'>{m[3]}</div>", unsafe_allow_html=True) # Equipo
        col4.write(m[4]) # Modelo
        col5.write(m[5]) # Fabricante
        col6.write(m[6]) # Estado
        col7.write(m[7]) # Sede
        col8.write(m[8]) # Ciudad

elif opcion == "Control de Traslados":

    st.header("Control de Traslados de Maquinaria")

    maquinas = obtener_maquinas()
    sedes = obtener_sedes()
    
    # 🔄 RESET CONTROLADO
    if "reset_traslado" in st.session_state:

        st.session_state.tipo_traslado = "Seleccione una opción"
        st.session_state.maquina_traslado = "Seleccione una opción"
        st.session_state.ciudad_traslado = "Seleccione una opción"
        st.session_state.sede_traslado = "Seleccione una opción"

        del st.session_state.reset_traslado
        
    # 🔴 VALIDACIÓN BÁSICA
    if not maquinas or not sedes:
        st.warning("Debes tener máquinas y sedes registradas.")
        st.stop()

    # 🔔 MENSAJE DE ÉXITO
    if "traslado_ok" in st.session_state:
        st.success("Traslado registrado correctamente")
        del st.session_state.traslado_ok

    

    # -------------------------
    # FILTRO POR TIPO
    # -------------------------

    tipos = sorted(list(set([m[2] for m in maquinas])))

    tipo_seleccionado = st.selectbox(
        "Tipo de máquina",
        ["Seleccione una opción"] + tipos, 
        key="tipo_traslado"
    )

    if tipo_seleccionado != "Seleccione una opción":

        maquinas_filtradas = [m for m in maquinas if m[2] == tipo_seleccionado]

        maquinas_dict = {f"{m[1]} | {m[2]} | {m[3]}": m[0] for m in maquinas_filtradas}

        maquina_seleccionada = st.selectbox(
            "Seleccionar máquina",
            ["Seleccione una opción"] + list(maquinas_dict.keys()),
            key="maquina_traslado"
        )

    if tipo_seleccionado != "Seleccione una opción" and maquina_seleccionada != "Seleccione una opción":

        maquina_id = maquinas_dict[maquina_seleccionada]

        maquina_info = obtener_maquina_por_id(maquina_id)

        sede_origen_id = maquina_info[6]
        sede_origen = maquina_info[7]
        ciudad_origen = maquina_info[8]

        col1, col2 = st.columns(2)
        col1.info(f"Ciudad origen: {ciudad_origen}")
        col2.info(f"Sede origen: {sede_origen}")

        # -------------------------
        # Ciudades disponibles
        # -------------------------

        ciudades = sorted(list(set([s[2] for s in sedes])))

        ciudad_destino = st.selectbox(
            "Ciudad destino",
            ["Seleccione una opción"] + ciudades,
            key="ciudad_traslado"

        )

        if ciudad_destino != "Seleccione una opción":

            # -------------------------
            # Filtrar sedes por ciudad
            # -------------------------

            sedes_destino = [
                s for s in sedes 
                if s[2] == ciudad_destino and s[0] != sede_origen_id
            ]
            sedes_destino_dict = {s[1]: s[0] for s in sedes_destino}
            
            if not sedes_destino:
                st.warning("No hay sedes disponibles diferentes a la sede origen.")
                st.stop()
            # -------------------------
            # Formulario traslado
            # -------------------------

            with st.form("form_traslado", clear_on_submit=True):

                sede_destino = st.selectbox(
                    "Sede destino",
                    ["Seleccione una opción"] + list(sedes_destino_dict.keys()),
                    key="sede_traslado"
                )

                fecha = st.date_input("Fecha de traslado")
                responsable = st.text_input("Responsable traslado")
                observaciones = st.text_area("Observaciones")

                submitted = st.form_submit_button("Registrar traslado")

                if submitted:

                    if sede_destino == "Seleccione una opción":
                        st.error("Debes seleccionar una sede destino")
                        st.stop()

                    insertar_traslado(
                        maquina_id,
                        sede_origen_id,
                        sedes_destino_dict[sede_destino],
                        str(fecha),
                        responsable,
                        observaciones
                    )
                    
                    # 🔄 RESET COMPLETO
                    st.session_state.reset_traslado = True              
                    st.session_state.traslado_ok = True
                    st.rerun()

    # =========================
    # HISTORIAL DE TRASLADOS
    # =========================

    st.divider()
    st.subheader("Historial reciente de traslados")

    traslados = obtener_ultimos_traslados(10)

    if not traslados:
        st.info("No hay traslados registrados.")
    else:

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        col1.write("Máquina")
        col2.write("Ciudad origen")
        col3.write("Sede origen")
        col4.write("Ciudad destino")
        col5.write("Sede destino")
        col6.write("Fecha")

        for t in traslados:

            col1, col2, col3, col4, col5, col6 = st.columns(6)

            col1.write(t[0]) #Maquina
            col2.write(t[1]) #Ciudad origen
            col3.write(t[2]) #Sede origen
            col4.write(t[3]) #Ciudad destino
            col5.write(t[4]) #Sede destino
            col6.write(t[5]) #Fecha

elif opcion == "Checklists Diarias":

    st.header("Registro de Checklist de Inspección")
    maquinas = obtener_maquinas()
    
    maquina_id = None
    ciudad_sel = None
    sede_sel = None
    
    
    # 🔄 RESET CONTROLADO
    if "reset_checklist" in st.session_state:

        st.session_state.check_ciudad = "Seleccione una opción"
        st.session_state.check_sede = "Seleccione una opción"
        st.session_state.check_maquina = "Seleccione una opción"

        del st.session_state.reset_checklist

    if not maquinas:
        st.warning("Primero debes registrar máquinas.")

    else:

        # -------------------------
        # FILTRO POR CIUDAD
        # -------------------------

        ciudades = sorted(list(set([m[8] for m in maquinas if m[8] is not None])))

        ciudad = st.selectbox(
            "Ciudad",
            ["Seleccione una opción"] + ciudades,
            key="check_ciudad"
        )
        if ciudad != "Seleccione una opción":
            ciudad_sel = ciudad
        
        maquinas_ciudad = [m for m in maquinas if m[8] == ciudad]

        # -------------------------
        # FILTRO POR SEDE
        # -------------------------

        sedes = sorted(list(set([m[7] for m in maquinas_ciudad if m[7] is not None])))

        sede = st.selectbox(
            "Sede",
            ["Seleccione una opción"] + sedes,
            key="check_sede"   
        )
        
        if sede != "Seleccione una opción":
            sede_sel = sede
        maquinas_sede = [m for m in maquinas_ciudad if m[7] == sede]

        # -------------------------
        # SELECCIÓN DE MÁQUINA
        # -------------------------

        #if not maquinas_sede:
            #st.warning("No hay máquinas registradas en esta sede.")
            #st.stop()

        maquinas_dict = {f"{m[1]} | {m[2]} | {m[3]}": m for m in maquinas_sede}

        maquina_seleccionada = st.selectbox(
            "Seleccione la máquina",
            ["Seleccione una opción"] + list(maquinas_dict.keys()),
            key="check_maquina"
        )
        
        tipo_maquina = None
        
        if maquina_seleccionada != "Seleccione una opción":
            maquina = maquinas_dict[maquina_seleccionada]
            maquina_id = maquina[0]
            tipo_maquina = maquina[2]
            
        if maquina_id:     
        
            fecha = st.date_input("Fecha de inspección")

            estructura = checklists_por_tipo.get(tipo_maquina, checklists_por_tipo["General"])
        
            # 🔥 convertir lista → categoría automática
            if isinstance(estructura, list):
                estructura = {"General": estructura}
            
            st.subheader("Checklist de inspección")
        
            if "form_checklist_key" not in st.session_state:
                st.session_state.form_checklist_key = 0
        
            with st.form(f"form_checklist_{st.session_state.form_checklist_key}"):

                checklist_respuestas = {}

                col1, col2, col3, col4 = st.columns([3,1,1,3])

                col1.write("Item")
                col2.write("Conforme")
                col3.write("No conforme")
                col4.write("Observación")

                st.divider()

                for categoria, items in estructura.items():

                    st.markdown(f"## 🔧 {categoria}")

                    for item in items:

                        col1, col2, col3 = st.columns([3,3,3])

                        estado = col2.radio(
                            "",
                            ["Conforme", "No conforme"],
                            horizontal=True,
                            index=0,
                            key=f"estado_{item}_{st.session_state.form_checklist_key}"
                        )
                        conforme = estado == "Conforme"
                        no_conforme = estado == "No conforme"
                        # Mostrar item en rojo si es no conforme
                        if no_conforme:
                            col1.markdown(f"🔴 **{item}**")
                        else:
                            col1.write(item)

                        observacion = col3.text_input("", key=f"obs_{item}_{st.session_state.form_checklist_key}")
                
                        checklist_respuestas[item] = (conforme, no_conforme, observacion)
                    
                    st.divider()
                
                submitted = st.form_submit_button("Guardar checklist")

                if submitted:

                    # VALIDAR OBSERVACIONES EN NO CONFORMES
                    for item, (conforme, no_conforme, observacion) in checklist_respuestas.items():

                        if no_conforme and observacion.strip() == "":
                            st.error(f"Debes escribir una observación para el item: {item}")
                            st.stop()

                    # GUARDAR CHECKLIST
                    checklist_id = insertar_checklist(
                        maquina_id,
                        fecha.isoformat()
                    )
                
                    st.session_state["ultima_checklist"] = checklist_id
                
                    fallas_detectadas = 0
                
                    for item, (conforme, no_conforme, observacion) in checklist_respuestas.items():
                        cumple = 1 if conforme else 0
                        insertar_item_checklist(
                            checklist_id,
                            item,
                            cumple,
                            observacion
                        )

                        if no_conforme:
                            fallas_detectadas += 1
                        
                            creada, veces = insertar_solicitud(
                                maquina_id,
                                item,
                                observacion,
                                "Checklist"
                            )
                            actualizar_estado_por_solicitudes(maquina_id)

                            # Si ya existía la solicitud, mostrar indicador
                            if not creada:
                                st.info(f"Falla repetida detectada ({veces} veces): {item}")
                        
                    #mensaje de éxito con cantidad de fallas detectadas        
                    st.session_state.checklist_msg = f"Checklist guardada. Fallas detectadas: {fallas_detectadas}"
                
                    st.session_state.reset_checklist = True
                    st.session_state.checklist_guardada = True
                    st.session_state.form_checklist_key += 1                
                    st.rerun()
                    
        # Mostrar mensaje si se guardó checklist
        if "checklist_msg" in st.session_state:
            st.success(st.session_state.checklist_msg)
            del st.session_state.checklist_msg
            
        # -------------------------
        # HISTORIAL DE CHECKLISTS
        # -------------------------
        
        if maquina_id and "ultima_checklist" in st.session_state:
            st.success(f"Última checklist registrada: #{st.session_state['ultima_checklist']}")
    
        if maquina_id:
            st.subheader("Historial de registros por máquina")
            checklists = obtener_ultimos_checklists_por_maquina(maquina_id)
        
        elif sede_sel:
            st.subheader(f"Historial de registros por sede: {sede_sel}")
            checklists = obtener_checklists_por_sede(sede_sel)

        elif ciudad_sel:
            st.subheader(f"Historial de registros por ciudad: {ciudad_sel}")
            checklists = obtener_checklists_por_ciudad(ciudad_sel)
        
        else:
            st.subheader("Historial general de registros")
            checklists = obtener_ultimos_checklists(10)  # 👈 Cambiar numero de historial

        if not checklists:
            st.info("Aún no hay checklists registradas.")

        else:

            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

            col1.write("ID Activo")
            col2.write("Tipo")
            col3.write("Equipo")
            col4.write("Fecha")
            col5.write("Fallas")
            col6.write("ver")
            col7.write("")

            for c in checklists:
                
                es_ultima = False

                if "ultima_checklist" in st.session_state:
                    if c[0] == st.session_state["ultima_checklist"]:
                        es_ultima = True

                
                
                
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

                if es_ultima:
                    col1.markdown(f"🟢 **{c[2]}**")
                else:
                    col1.write(c[2]) # ID Activo
                col2.write(c[1]) # Tipo máquina
                col3.write(c[3]) # Equipo
                col4.write(c[4]) # Fecha
                
                # Mostrar fallas con color
                if c[5] > 0:
                    col5.markdown(f"🔴 **{c[5]}**")
                else:
                    col5.markdown("🟢 0")
                
                # Botón para ver detalles del checklist
                if col6.button("Ver", key=f"ver_checklist_{c[0]}"):

                    items = obtener_items_checklist(c[0])

                    st.markdown(f"### Checklist #{c[0]}")
                    
                    no_conformes = []
                    for item in items:
                        
                        nombre_item = item[0]
                        cumple = item[1]
                        observacion = item[2]
                        
                        if cumple == 0:
                            no_conformes.append((nombre_item, observacion))
                        
                    # SI TODO ESTÁ CONFORME
                    if len(no_conformes) == 0:
                        st.markdown("🟢 **Todo está conforme en esta inspección**")
                        
                    # SI HAY FALLAS
                    else:
                        st.markdown(f"**No conformidades detectadas: {len(no_conformes)}**")
                        for nombre_item, observacion in no_conformes:
                            st.markdown(f"🔴 **{nombre_item}**")

                            if observacion and str(observacion).strip() != "":
                                st.write(f"Observación: {observacion}")

                            st.divider()   
                        
                
                if f"confirmar_checklist_{c[0]}" not in st.session_state:
                    st.session_state[f"confirmar_checklist_{c[0]}"] = False

                if not st.session_state[f"confirmar_checklist_{c[0]}"]:

                    if col7.button("Eliminar", key=f"del_checklist_{c[0]}"):
                        st.session_state[f"confirmar_checklist_{c[0]}"] = True

                else:

                    col7.warning("¿Confirmar?")

                    colA, colB = st.columns(2)

                    if colA.button("Sí", key=f"si_checklist_{c[0]}"):

                        eliminar_checklist(c[0])

                        st.success("Checklist eliminada")

                        del st.session_state[f"confirmar_checklist_{c[0]}"]

                        st.rerun()

                    if colB.button("No", key=f"no_checklist_{c[0]}"):

                        st.session_state[f"confirmar_checklist_{c[0]}"] = False

                        st.rerun()
                        
            if "ultima_checklist" in st.session_state:
                del st.session_state["ultima_checklist"]
  
elif opcion == "Solicitudes de Mantenimiento":

    st.subheader("Crear solicitud manual")

    maquinas = obtener_maquinas()
    
    if "reset_solicitud" in st.session_state:
        st.session_state.sol_ciudad = "Seleccione una opción"
        st.session_state.sol_sede = "Seleccione una opción"
        st.session_state.sol_maquina = "Seleccione una opción"
        st.session_state.sol_item = "Seleccione una opción"
        del st.session_state.reset_solicitud

    if not maquinas:
        st.warning("Primero debes registrar máquinas.")
        st.stop()

    # -------------------------
    # FILTRO POR CIUDAD
    # -------------------------

    ciudades = sorted(list(set([m[8] for m in maquinas if m[8] is not None])))

    ciudad = st.selectbox(
        "Ciudad",
        ["Seleccione una opción"] + ciudades,
        key="sol_ciudad"
    )
    if ciudad == "Seleccione una opción":
        st.stop()

    maquinas_ciudad = [m for m in maquinas if m[8] == ciudad]

    # -------------------------
    # FILTRO POR SEDE
    # -------------------------

    sedes = sorted(list(set([m[7] for m in maquinas_ciudad if m[7] is not None])))

    sede = st.selectbox(
        "Sede",
        ["Seleccione una opción"] + sedes,
        key="sol_sede"
    )
    if sede == "Seleccione una opción":
        st.stop()

    maquinas_sede = [m for m in maquinas_ciudad if m[7] == sede]

    if not maquinas_sede:
        st.warning("No hay máquinas registradas en esta sede.")
        st.stop()

    # -------------------------
    # SELECCIÓN DE MÁQUINA
    # -------------------------

    maquinas_dict = {m[0]: m for m in maquinas_sede}
    
    opciones_maquina = [None] + list(maquinas_dict.keys())

    maquina_id_seleccionada = st.selectbox(
        "Máquina",
        opciones_maquina,
        format_func=lambda x: (
            "Seleccione una opción"
            if x is None
            else f"{maquinas_dict[x][1]} | {maquinas_dict[x][2]} | {maquinas_dict[x][3]}"
        ),
        key="sol_maquina"
    )

    if maquina_id_seleccionada is None:
        st.stop()

    maquina = maquinas_dict[maquina_id_seleccionada]

    maquina_id = maquina[0]
    tipo_maquina = maquina[1]

    # TEMPORAL: mostrar tipo detectado
    #st.write("Tipo de máquina detectado:", tipo_maquina)

    estructura = checklists_por_tipo.get(
        tipo_maquina,
        checklists_por_tipo["General"]
    )

    # 🔥 CREAR ITEMS AGRUPADOS
    items_checklist = []

    if isinstance(estructura, dict):
        for categoria, items in estructura.items():
            for item in items:
                items_checklist.append(f"{categoria} → {item}") #Opción de cambiar
    else:
        items_checklist = estructura
    # -------------------------
    # FORMULARIO
    # -------------------------

    if "form_solicitud_key" not in st.session_state:
        st.session_state.form_solicitud_key = 0

    with st.form(f"form_solicitud_manual_{st.session_state.form_solicitud_key}"):

        item_falla = st.selectbox(
            "Item que presenta la falla",
            ["Seleccione una opción"] + items_checklist,
            key="sol_item"
        )

        observacion = st.text_area("Observación")

        submitted = st.form_submit_button("Crear solicitud")

        if submitted:
            if item_falla == "Seleccione una opción":
                st.error("Debe seleccionar un item")
                st.stop()

            if observacion.strip() == "":
                st.error("Debe escribir una observación")
                st.stop()
                
            if "→" in item_falla:
                item_falla = item_falla.split("→")[1].strip()

            descripcion = f"{item_falla} - {observacion}"

            creada, veces = insertar_solicitud(
                maquina_id,
                item_falla,
                observacion,
                "Manual"
            )
            actualizar_estado_por_solicitudes(maquina_id)

            if not creada:
                st.warning(f"Esa falla ya tiene una solicitud pendiente. Detectada {veces} veces.")
                st.stop()
                #st.rerun()

            st.session_state.reset_solicitud = True
            st.session_state.solicitud_creada = True
            st.session_state.form_solicitud_key += 1
            st.rerun()

    if "solicitud_creada" in st.session_state:
        st.success("Solicitud creada correctamente")
        del st.session_state.solicitud_creada           
            
elif opcion == "Registro de Mantenimientos":

    st.header("Registro de Mantenimientos")

    maquinas = obtener_maquinas()

    if not maquinas:
        st.warning("Primero debes registrar máquinas.")
        st.stop()

    # -------------------------
    # FILTRO POR CIUDAD
    # -------------------------

    ciudades = sorted(list(set([m[8] for m in maquinas if m[8] is not None])))

    ciudad = st.selectbox("Ciudad", ciudades)

    maquinas_ciudad = [m for m in maquinas if m[8] == ciudad]

    # -------------------------
    # FILTRO POR SEDE
    # -------------------------

    sedes = sorted(list(set([m[7] for m in maquinas_ciudad if m[7] is not None])))

    sede = st.selectbox("Sede", sedes)

    maquinas_sede = [m for m in maquinas_ciudad if m[7] == sede]

    if not maquinas_sede:
        st.warning("No hay máquinas registradas en esta sede.")
        st.stop()

    # -------------------------
    # SELECCIÓN DE MÁQUINA
    # -------------------------

    maquinas_dict = {f"{m[1]} | {m[2]} | {m[3]}": m for m in maquinas_sede}

    maquina_seleccionada = st.selectbox(
        "Máquina",
        list(maquinas_dict.keys())
    )

    maquina = maquinas_dict[maquina_seleccionada]

    maquina_id = maquina[0]

    # -------------------------
    # SOLICITUDES PENDIENTES
    # -------------------------

    solicitudes = obtener_solicitudes_pendientes_por_maquina(maquina_id)

    solicitudes_dict = {f"{s[0]} ({s[1]} veces)": s[0] for s in solicitudes}

    if "form_mantenimiento_key" not in st.session_state:
        st.session_state.form_mantenimiento_key = 0

    with st.form(f"form_mantenimiento_{st.session_state.form_mantenimiento_key}"):

        solicitudes_seleccionadas = st.multiselect(
            "Solicitudes atendidas",
            list(solicitudes_dict.keys())
        )

        fecha = st.date_input("Fecha del mantenimiento")

        tecnico = st.text_input("Técnico / Empresa")

        recibido_por = st.text_input("Recibido por")

        observaciones = st.text_area("Observaciones")
        
        estado_maquina = st.selectbox(
            "Estado operativo después del mantenimiento",
            ESTADOS_OPERACION,
            index=ESTADOS_OPERACION.index(maquina[6]) if maquina[6] in ESTADOS_OPERACION else 0
        )

        submitted = st.form_submit_button("Registrar mantenimiento")

        if submitted:

            if not solicitudes_seleccionadas:
                st.error("Debes seleccionar al menos una solicitud.")
                st.stop()

            solicitudes_ids = [solicitudes_dict[s] for s in solicitudes_seleccionadas]

            mantenimiento_id = registrar_mantenimiento(
                maquina_id,
                fecha.isoformat(),
                tecnico,
                recibido_por,
                observaciones,
                solicitudes_ids
            )
            actualizar_estado_maquina(maquina_id, estado_maquina)
            
            st.session_state.mantenimiento_actual = mantenimiento_id
            
            st.session_state.form_mantenimiento_key += 1
            
            
    if "mantenimiento_actual" in st.session_state:
        st.subheader("💰 Costos del mantenimiento")
        
        tipo_costo = st.selectbox(
            "Tipo de costo",
            ["Mano de obra", "Repuestos", "Otros"]
        )

        descripcion_costo = st.text_input("Descripción del costo")

        cantidad = st.number_input("Cantidad", min_value=1.0)

        costo_unitario = st.number_input("Costo unitario", min_value=0.0)

        if st.button("Agregar costo"):

            insertar_costo(
                st.session_state.mantenimiento_actual,
                tipo_costo,
                descripcion_costo,
                cantidad,
                costo_unitario
            )
            
        if st.button("Finalizar mantenimiento"):

            del st.session_state.mantenimiento_actual
            st.success("Mantenimiento finalizado correctamente")
            st.rerun()
            
        if "mantenimiento_actual" in st.session_state:

            costos = obtener_costos_por_mantenimiento(st.session_state.mantenimiento_actual)

            st.subheader("Costos registrados")

            for c in costos:
                st.write(f"{c[2]} - {c[3]} - ${c[6]}")
            
            
elif opcion == "Historial de Solicitudes":
    
    st.subheader("Lista de solicitudes registradas")

    solicitudes = obtener_todas_solicitudes()

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
            col4.write(s[3])
            # Color opcional: #F2C201
            if s[4] > 1:
                col5.markdown(f"<span style='background-color:#E1B102;padding:4px 8px;border-radius:6px'>{s[4]} rep.</span>", unsafe_allow_html=True)
            else:
                col5.markdown(f" **{s[4]} rep.**")
            
            col6.write(s[5])
            col7.write(s[6])

            if s[7] == "Pendiente":
                col8.markdown("🔴 Pendiente")
            else:
                col8.markdown("🟢 Cerrada")

elif opcion == "Historial de Mantenimientos":
    st.subheader("Historial de mantenimientos")

    registros_por_pagina = 15

    # Obtener total de registros
    total_registros = contar_mantenimientos()

    # Calcular número total de páginas
    total_paginas = max(1, (total_registros + registros_por_pagina - 1) // registros_por_pagina)

    # Inicializar página
    if "pagina_mantenimientos" not in st.session_state:
        st.session_state.pagina_mantenimientos = 1

    pagina = st.session_state.pagina_mantenimientos

    # Botones de navegación
    colA, colB, colC = st.columns([1,2,1])

    if colA.button("⬅ Anterior") and pagina > 1:
        st.session_state.pagina_mantenimientos -= 1
        st.rerun()

    colB.markdown(f"**Página {pagina} de {total_paginas}**")

    if colC.button("Siguiente ➡") and pagina < total_paginas:
        st.session_state.pagina_mantenimientos += 1
        st.rerun()

    # Obtener registros
    mantenimientos = obtener_mantenimientos_paginados(pagina, registros_por_pagina)

    # Mostrar tabla
    if not mantenimientos:
        st.info("Aún no hay mantenimientos registrados.")

    else:

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        col1.write("Ciudad")
        col2.write("Sede")
        col3.write("Máquina")
        col4.write("Tipo")
        col5.write("Fecha")
        col6.write("Descripción")

        for m in mantenimientos:

            col1, col2, col3, col4, col5, col6 = st.columns(6)

            col1.write(m[0])
            col2.write(m[1])
            col3.write(m[2])
            col4.write(m[3])
            col5.write(m[4])
            col6.write(m[5])

elif opcion == "Hoja de Vida de Equipos":

    st.header("Hoja de Vida de Máquina")

    maquinas = obtener_maquinas()

    if not maquinas:
        st.warning("No hay máquinas registradas.")
        st.stop()
        
    # -------------------------
    # FILTRO POR TIPO DE MÁQUINA
    # -------------------------

    tipos = sorted(list(set([m[1] for m in maquinas if m[1] is not None])))

    tipo_seleccionado = st.selectbox(
        "Tipo de máquina",
        tipos
    )

    maquinas_filtradas = [m for m in maquinas if m[1] == tipo_seleccionado]

    maquinas_dict = {f"{m[2]} - {m[1]}": m for m in maquinas_filtradas}

    if not maquinas_filtradas:
        st.warning("No hay máquinas de este tipo.")
        st.stop()
    
    maquina_seleccionada = st.selectbox(
        "Seleccione la máquina",
        list(maquinas_dict.keys())
    )

    maquina = maquinas_dict[maquina_seleccionada]
    maquina_id = maquina[0]
    
    ubicacion = obtener_ubicacion_maquina(maquina_id)
    ultimo_traslado = obtener_ultimo_traslado(maquina_id)
    
    
    with st.expander("📍 Información general", expanded=True):
        st.subheader("Ubicación actual")

        col1, col2, col3 = st.columns(3)

        col1.metric("Ciudad", ubicacion[0] if ubicacion else "-")
        col2.metric("Sede", ubicacion[1] if ubicacion else "-")
        col3.metric("Último traslado", ultimo_traslado if ultimo_traslado else "Sin registros")

        st.divider()
    
        indicadores = obtener_indicadores_maquina(maquina_id)

    with st.expander("📊 Indicadores de la Máquina", expanded=True):

        # ---------- FILA 1 ----------
        col1, col2, col3 = st.columns(3)

        estado = indicadores["estado"]

        if estado == "Operativa":
            col1.markdown("**Estado operativo**")
            col1.markdown("🟢 **Operativa**")

        elif estado == "Fuera de servicio":
            col1.markdown("**Estado operativo**")
            col1.markdown("🔴 **Fuera de servicio**")
        
        elif estado == "Operativa con falla":
            col1.markdown("**Estado operativo**")
            col1.markdown("🟡 **Operativa con Falla**")

        else:
            col1.markdown("**Estado operativo**")
            col1.markdown("🔧 **Mantenimiento**")


        col2.metric(
            "Mantenimientos",
            indicadores["mantenimientos"]
        )

        col3.metric(
            "Fallas detectadas",
            indicadores["fallas"]
        )

        # ---------- FILA 2 ----------
        col4, col5 = st.columns(2)

        if indicadores["falla_top"] != "-":
            col4.metric(
            "Falla más frecuente",
            indicadores["falla_top"],
            f"{indicadores['falla_top_rep']} veces"
        )
        else:
            col4.metric(
                "Falla más frecuente",
                "Sin registros"
            )

        col5.metric(
            "Último mantenimiento",
            indicadores["ultimo_mantenimiento"]
        )

        st.divider()

    # =========================
    # MANTENIMIENTOS
    # =========================

    with st.expander("🔧 Historial de Mantenimientos"):

        mantenimientos = obtener_mantenimientos_por_maquina(maquina_id)

        if not mantenimientos:
            st.info("No hay mantenimientos registrados.")

        else:

            col1, col2, col3, col4 = st.columns(4)
            col1.write("Fecha")
            col2.write("Técnico")
            col3.write("Recibido por")
            col4.write("Descripción")

            for m in mantenimientos:

                col1, col2, col3, col4 = st.columns(4)

                col1.write(m[0])
                col2.write(m[1])
                col3.write(m[2])
                col4.write(m[3])

        st.divider()
    
    # =========================
    # ESTADO
    # =========================
    with st.expander("📈 Historial de Estado Operativo"):

        historial = obtener_historial_estado(maquina_id)

        if not historial:
            st.info("No hay cambios de estado registrados.")
        
        else:

            col1, col2 = st.columns(2)

            col1.write("Estado")
            col2.write("Fecha")

            for h in historial:

                col1, col2 = st.columns(2)

                estado = h[0]
                fecha = h[1]

                if estado == "Operativa":
                    col1.markdown("🟢 Operativa")
                elif estado == "Operativa con falla":
                    col1.markdown("🟡 Operativa con falla")
                elif estado == "En mantenimiento":
                    col1.markdown("🔧 En mantenimiento")
                else:
                    col1.markdown("🔴 Fuera de servicio")

                col2.write(fecha)
        

    # =========================
    # SOLICITUDES
    # =========================

    with st.expander("🚨 Historial de Solicitudes"):

        solicitudes = obtener_solicitudes_por_maquina(maquina_id)

        if not solicitudes:
            st.info("No hay solicitudes registradas.")
        else:

            col1, col2, col3, col4 = st.columns(4)
            col1.write("Fecha")
            col2.write("Item")
            col3.write("Repeticiones")
            col4.write("Estado")

            for s in solicitudes:

                col1, col2, col3, col4 = st.columns(4)

                col1.write(s[0])
                col2.write(s[1])
                col3.write(s[2])

                if s[3] == "Pendiente":
                    col4.markdown("🔴 Pendiente")
                else:
                    col4.markdown("🟢 Cerrada")

        st.divider()
    
    # =========================
    # CHECKLISTS
    # =========================

    with st.expander("📋 Historial de Checklists"):

        checklists = obtener_checklists_por_maquina(maquina_id)

        if not checklists:
            st.info("No hay checklists registradas.")
        else:

            col1, col2, col3, col4 = st.columns(4)

            col1.write("ID")
            col2.write("Fecha")
            col3.write("Fallas")
            col4.write("No Conformidades")

            for c in checklists:

                col1, col2, col3, col4 = st.columns(4)

                col1.write(c[0])
                col2.write(c[1])

                if c[2] > 0:
                    col3.markdown(f"🔴 {c[2]}")
                else:
                    col3.markdown("🟢 0")
                
                if c[3]:
                    col4.markdown("\n".join([f"• {item}" for item in c[3]]))
                else:
                    col4.write("Sin no conformidades")

        st.divider()

    # =========================
    # TRASLADOS
    # =========================

    with st.expander("🚚 Historial de Traslados"):

        traslados = obtener_traslados_por_maquina(maquina_id)

        if not traslados:
            st.info("No hay traslados registrados.")
        else:

            col1, col2, col3, col4, col5, col6  = st.columns(6)

            col1.write("Ciudad Origen")
            col2.write("Sede Origen")
            col3.write("Ciudad Destino")
            col4.write("Sede Destino")
            col5.write("Fecha")
            col6.write("Responsable")

            for t in traslados:

                col1, col2, col3, col4, col5, col6 = st.columns(6)

                col1.write(t[0])
                col2.write(t[1])
                col3.write(t[2])
                col4.write(t[3])
                col5.write(t[4])
                col6.write(t[5])

elif opcion == "Dashboard de Análisis":
    st.header("Dashboard General de Mantenimiento")
    
    # =========================
    # DISPONIBILIDAD
    # =========================

    disponibilidad = calcular_disponibilidad()

    st.subheader("Disponibilidad del sistema")

    col1, col2 = st.columns([1,3])

    col1.metric("Disponibilidad", f"{disponibilidad}%")

    # Barra visual
    col2.progress(int(disponibilidad))
    
    # =========================
    # RESUMEN DE ESTADOS
    # =========================

    resumen = obtener_resumen_general()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🟢 Operativas", resumen["Operativa"])
    col2.metric("🟡 Con falla", resumen["Operativa con falla"])
    col3.metric("🔧 En mantenimiento", resumen["En mantenimiento"])
    col4.metric("🔴 Fuera de servicio", resumen["Fuera de servicio"])

    st.divider()
    
    # =========================
    # ALERTAS
    # =========================
    st.subheader("Alertas del sistema")
    alertas = obtener_alertas()
    if not alertas:
        st.success("No hay alertas activas")
    else:
        for alerta in alertas:
            st.warning(alerta)
            
    # =========================
    # RANKING DE MÁQUINAS CRÍTICAS
    # =========================
    st.subheader("🏆 Máquinas más críticas")
    ranking = obtener_ranking_maquinas()

    if not ranking:
        st.info("No hay datos suficientes.")
    else:
        # Crear DataFrame
        df = pd.DataFrame(ranking, columns=["Equipo", "Tipo", "Fallas"])
        # Crear nombre combinado
        df["Nombre"] = df["Tipo"] + " " + df["Equipo"]
        # Ordenar (por seguridad)
        df = df.sort_values(by="Fallas", ascending=False)

        # =========================
        # GRÁFICA
        # =========================
        #st.bar_chart(
            #df.set_index("Nombre")["Fallas"]
        #)
        #st.divider()
        # =========================
        # LISTA DETALLADA
        # =========================
        for i, row in df.sort_values(by="Fallas", ascending=False).iterrows():

            st.write(
                f"🔴 {row['Nombre']} — {int(row['Fallas'])} fallas"
            )
            
    # =========================
    # FALLAS MÁS FRECUENTES
    # =========================
    st.subheader("Fallas más recurrentes")
    fallas = obtener_top_fallas()

    if not fallas:
        st.info("No hay fallas registradas.")
    else:
        # Preparar datos
        items = [f[0] for f in fallas]
        valores = [f[1] for f in fallas]

        # Crear gráfica
        fig, ax = plt.subplots()
        ax.barh(items, valores)

        ax.set_xlabel("Número de fallas")
        ax.set_title("Fallas más recurrentes")

        # Mostrar gráfica
        st.pyplot(fig)

    st.divider()

    # =========================
    # ÚLTIMOS MANTENIMIENTOS
    # =========================

    st.subheader("Últimos mantenimientos")

    mantenimientos = obtener_ultimos_mantenimientos_dashboard()

    if not mantenimientos:
        st.info("No hay mantenimientos registrados.")
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

elif opcion == "Dashboard de Costos":

    st.header("📊 Dashboard de Costos de Mantenimiento")

    datos = obtener_costos_dashboard()

    if not datos:
        st.warning("No hay costos registrados aún.")
        st.stop()
    
    ## Cálculo de costo total acumulado
    total_general = sum([float(d[2]) for d in datos])
    st.metric("Costo total acumulado", f"${float(total_general):,.2f}")
    
    ## Opcional: gráfica de pastel por tipo de costo
    st.subheader("💰 Costos por máquina")

    for d in datos:
        st.write(f"{d[0]} | {d[1]} → ${float(d[2]):,.0f}")
    
    ## Ranking de máquinas más costosas  
    st.subheader("🏆 Máquinas más costosas")
    top = sorted(datos, key=lambda x: x[2], reverse=True)
    for i, d in enumerate(top[:5], start=1):
        st.write(f"{i}. {d[0]} | {d[1]} → ${float(d[2]):,.0f}")
    
    ## Costo acumulado por tipo de máquina    
    st.subheader("🧰 Costos por tipo de máquina")
    costos_tipo = {}
    for d in datos:
        tipo = d[1]
        costos_tipo[tipo] = costos_tipo.get(tipo, 0) + float(d[2])

    for tipo, total in costos_tipo.items():
        st.write(f"{tipo} → ${total:,.0f}")
    
    ## Gráfica de barras por máquina    
    st.subheader("📊 Costos por máquina")

    nombres = [f"{d[0]}" for d in datos]  # activo fijo
    costos = [float(d[2]) for d in datos]

    plt.figure()
    plt.bar(nombres, costos)
    plt.xticks(rotation=45)

    st.pyplot(plt)
    plt.clf()
    
    ##
    st.subheader("🧰 Costos por tipo")

    costos_tipo = {}

    for d in datos:
        tipo = d[1]
        costos_tipo[tipo] = costos_tipo.get(tipo, 0) + float(d[2])

    tipos = list(costos_tipo.keys())
    valores = list(costos_tipo.values())

    plt.figure()
    plt.bar(tipos, valores)
    plt.xticks(rotation=30)
    st.pyplot(plt)
    plt.clf()
    
    ##
    st.subheader("🏆 Top 5 máquinas más costosas")

    top = sorted(datos, key=lambda x: x[2], reverse=True)[:5]

    nombres_top = [d[0] for d in top]
    costos_top = [float(d[2]) for d in top]

    plt.figure()
    plt.barh(nombres_top, costos_top)

    st.pyplot(plt)
    plt.clf()
 