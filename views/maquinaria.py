import streamlit as st

# Funciones de la base de datos
from database import (
    # Maquinaria
    insertar_maquina, 
    obtener_maquinas,
    obtener_maquina_por_id, 
    eliminar_maquina,
    actualizar_maquina,
    conteo_maquinas_por_sede,
    # Sedes
    insertar_sede, 
    obtener_sedes,
    sede_tiene_maquinas, 
    eliminar_sede,
    # Traslados
    insertar_traslado,
    obtener_traslados,
    obtener_ultimos_traslados,
    actualizar_estado_maquina
)

from utils.qr_etiquetas import generar_qr_etiqueta
from utils.pdf_qr import generar_qr_pdf

from utils.config_url import BASE_URL
from utils.export import generar_excel_maquinas

# Listas de opciones para formularios
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

def vista_registro_maquinaria():
    
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
        modelo = st.text_input("Área")
        fabricante = st.text_input("Material")

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
    col4.write("Área")
    col5.write("Material")
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
        col2.markdown(f"<div style='white-space:nowrap'>{maquina[2]}</div>", unsafe_allow_html=True) #Tipo
        col3.markdown(f"<div style='white-space:nowrap'>{maquina[3]}</div>", unsafe_allow_html=True) #Equipo
        col4.markdown(f"<div style='white-space:nowrap'>{maquina[4]}</div>", unsafe_allow_html=True) #Modelo
        col5.markdown(f"<div style='white-space:nowrap'>{maquina[5]}</div>", unsafe_allow_html=True) #Fabricante
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

def vista_registro_sedes():

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

def vista_inventario_maquinas():
    
    if "confirmar_export_maquinas" not in st.session_state:
        st.session_state.confirmar_export_maquinas = False

    if "excel_maquinas" not in st.session_state:
        st.session_state.excel_maquinas = None

    if "nombre_archivo_maquinas" not in st.session_state:
        st.session_state.nombre_archivo_maquinas = ""

    if "texto_export_maquinas" not in st.session_state:
        st.session_state.texto_export_maquinas = ""
    
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
    
    #DEBUG
    st.write(maquinas[0])
    
    ################
    #----------------
    # CAMBIAR URL
    base_url = BASE_URL

    if maquinas:
        pdf_buffer = generar_qr_pdf(maquinas, base_url)

        st.download_button(
            label="📄 Descargar lista de QR",
            data=pdf_buffer,
            file_name="QR__Listado_Maquinas.pdf",
            mime="application/pdf"
        )
    else:
        st.info("No hay máquinas registradas para generar códigos QR.")
        
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
        
    
    st.divider()
    st.subheader("📥 Exportar inventario")

    if st.button("Exportar inventario de máquinas"):

        if filtro_sede != "Todas" and filtro_tipo != "Todos":
            texto = f"para {filtro_sede} - {filtro_tipo}"
            nombre = f"inventario_{filtro_sede}_{filtro_tipo}"

        elif filtro_sede != "Todas":
            texto = f"para {filtro_sede}"
            nombre = f"inventario_{filtro_sede}"

        elif filtro_tipo != "Todos":
            texto = f"para {filtro_tipo}"
            nombre = f"inventario_{filtro_tipo}"

        else:
            texto = "completo"
            nombre = "inventario_completo"

        nombre = nombre.replace(" ", "_").replace("-", "_")

        st.session_state.confirmar_export_maquinas = True
        st.session_state.texto_export_maquinas = texto
        st.session_state.nombre_archivo_maquinas = nombre
        
    if st.session_state.confirmar_export_maquinas:

        st.warning(
            f"¿Desea descargar el inventario de máquinas {st.session_state.texto_export_maquinas}?"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Descargar inventario"):

                st.session_state.excel_maquinas = generar_excel_maquinas(maquinas_filtradas)
                st.session_state.confirmar_export_maquinas = False

        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_export_maquinas = False
                st.rerun()
        
    if st.session_state.excel_maquinas:

        st.download_button(
            label="⬇️ Descargar Excel de inventario",
            data=st.session_state.excel_maquinas,
            file_name=f"{st.session_state.nombre_archivo_maquinas}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    

    st.subheader("Máquinas registradas")

    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)

    col1.write("ID Activo")
    col2.write("Tipo")
    col3.write("Equipo")
    col4.write("Área")
    col5.write("Material")
    col6.write("Estado")
    col7.write("Sede")
    col8.write("Ciudad")
    col9.write("QR")
    

    for m in maquinas_filtradas:

        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)

        col1.write(m[1]) # ID Activo 
        col2.markdown(f"<div style='white-space:nowrap'>{m[2]}</div>", unsafe_allow_html=True) # Tipo máquina
        col3.markdown(f"<div style='white-space:nowrap'>{m[3]}</div>", unsafe_allow_html=True) # Equipo
        col4.write(m[4]) # Modelo
        col5.write(m[5]) # Fabricante
        col6.write(m[6]) # Estado
        col7.write(m[7]) # Sede
        col8.write(m[8]) # Ciudad
        col9.write("") # QR
        
        # Boton QR
        
        ################
        #---------------
        # CAMBIAR URL
        base_url = BASE_URL

        qr_bytes = generar_qr_etiqueta(m, base_url)

        col9.download_button(
            label="QR",
            data=qr_bytes,
            file_name=f"QR_{m[1]}.png",
            mime="image/png",
            key=f"qr_{m[0]}"
        )

def vista_traslados():

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







