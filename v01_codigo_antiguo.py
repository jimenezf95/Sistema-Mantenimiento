from database import (
    crear_tablas, 
    #Maquinaria
    insertar_maquina, 
    obtener_maquinas, 
    eliminar_maquina,
    actualizar_maquina,
    #Sedes 
    insertar_sede, 
    obtener_sedes, 
    eliminar_sede, 
    #Mantenimientos
    insertar_mantenimiento, 
    obtener_mantenimientos,
    eliminar_mantenimiento,
    #Checklists
    insertar_checklist,
    insertar_item_checklist,
    crear_solicitud_mantenimiento,
    obtener_checklists,
    eliminar_checklist,
    insertar_solicitud,
    obtener_solicitudes,
    obtener_solicitudes_pendientes_por_maquina,
    cerrar_solicitudes
    
)
import streamlit as st
from config_checklist import checklists_por_tipo

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

    if st.button("Registro de Sedes"):
        st.session_state.opcion = "Registro de Sedes"

    if st.button("Registro de Maquinaria"):
        st.session_state.opcion = "Registro de Maquinaria"
    
    if st.button("Control de traslados"):
        st.session_state.opcion = "Control de Traslados"
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
    sede_nombres = {f"{sede[1]} - {sede[2]}": sede[0] for sede in sedes}

    with st.form("form_maquina", clear_on_submit=True):

        tipo = st.text_input("Tipo de máquina")
        numero_equipo = st.text_input("Número de equipo")
        modelo = st.text_input("Modelo")
        fabricante = st.text_input("Fabricante")

        estado_operacion = st.selectbox(
            "Estado de operación",
            ["Operativa", "En mantenimiento", "Fuera de servicio"]
        )

        sede_seleccionada = st.selectbox(
            "Sede",
            list(sede_nombres.keys())
        )

        submitted = st.form_submit_button("Registrar máquina")

        if submitted:
            insertar_maquina(
                tipo,
                numero_equipo,
                modelo,
                fabricante,
                estado_operacion,
                sede_nombres[sede_seleccionada]
            )
            st.success("Máquina registrada correctamente")

    st.subheader("Maquinaria registrada")

    maquinas = obtener_maquinas()

    # Encabezados de la tabla
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
    col1.write("ID")
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
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
        col1.write(maquina[0])
        col2.write(maquina[1])
        col3.write(maquina[2])
        col4.write(maquina[3])
        col5.write(maquina[4])
        col6.write(maquina[5])
        col7.write(maquina[6])
        col8.write(maquina[7])

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
            tipo = st.text_input("Tipo de máquina", value=maquina_editar[1])
            numero_equipo = st.text_input("Número de equipo", value=maquina_editar[2])
            modelo = st.text_input("Modelo", value=maquina_editar[3])
            fabricante = st.text_input("Fabricante", value=maquina_editar[4])

            estado_operacion = st.selectbox(
                "Estado de operación",
                ["Operativa", "En mantenimiento", "Fuera de servicio"]
            )

            sede_seleccionada = st.selectbox(
                "Sede",
                list(sede_nombres.keys())
            )

            submitted = st.form_submit_button("Guardar cambios")

            if submitted:
                actualizar_maquina(
                    st.session_state.editar_maquina_id,
                    tipo,
                    numero_equipo,
                    modelo,
                    fabricante,
                    estado_operacion,
                    sede_nombres[sede_seleccionada]
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

    for sede in sedes:
        col1, col2, col3, col4 = st.columns(4)

        col1.write(sede[0])
        col2.write(sede[1])
        col3.write(sede[2])

        # Primer botón de eliminar
        if col4.button("Eliminar", key=f"sede_{sede[0]}"):
            st.session_state["confirm_delete_sede_id"] = sede[0]

        # Confirmación de eliminación
        if "confirm_delete_sede_id" in st.session_state and st.session_state["confirm_delete_sede_id"] == sede[0]:
            st.warning("¿Seguro que quieres eliminar esta sede?")
            col_confirm, col_cancel = st.columns([1,1])

            if col_confirm.button("Confirmar", key=f"confirm_sede_{sede[0]}"):
                eliminar_sede(sede[0])
                del st.session_state["confirm_delete_sede_id"]
                st.rerun()

            if col_cancel.button("Cancelar", key=f"cancel_sede_{sede[0]}"):
                del st.session_state["confirm_delete_sede_id"]
                st.rerun()

elif opcion == "Checklists Diarias":

    st.header("Registro de Checklist de Inspección")

    # Mostrar mensaje si se guardó checklist
    if "checklist_guardada" in st.session_state:
        st.success("Checklist registrada correctamente")
        del st.session_state.checklist_guardada

    maquinas = obtener_maquinas()

    if not maquinas:
        st.warning("Primero debes registrar máquinas.")

    else:

        maquinas_dict = {f"{m[2]} - {m[1]}": m for m in maquinas}

        maquina_seleccionada = st.selectbox(
            "Seleccione la máquina",
            list(maquinas_dict.keys())
        )

        maquina = maquinas_dict[maquina_seleccionada]

        maquina_id = maquina[0]
        tipo_maquina = maquina[1]

        st.write(f"**Tipo de máquina:** {tipo_maquina}")

        fecha = st.date_input("Fecha de inspección")

        items = checklists_por_tipo.get(tipo_maquina, checklists_por_tipo["General"])

        st.subheader("Checklist de inspección")

        with st.form("form_checklist"):

            checklist_respuestas = {}

            col1, col2, col3, col4 = st.columns([3,1,1,3])

            col1.write("Item")
            col2.write("Conforme")
            col3.write("No conforme")
            col4.write("Observación")

            st.divider()

            for item in items:

                col1, col2, col3, col4 = st.columns([3,1,1,3])

                col1.write(item)

                estado = col2.radio(
                    "",
                    ["Conforme", "No conforme"],
                    horizontal=True,
                    key=f"estado_{item}"
                )
                conforme = estado == "Conforme"
                no_conforme = estado == "No conforme"
                # Mostrar item en rojo si es no conforme
                if no_conforme:
                    col1.markdown(f"🔴 **{item}**")
                else:
                    col1.write(item)

                observacion = col4.text_input("", key=f"obs_{item}")

                checklist_respuestas[item] = (conforme, no_conforme, observacion)

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
                    tipo_maquina,
                    str(fecha)
                )

                for item, (conforme, no_conforme, observacion) in checklist_respuestas.items():
                    cumple = 1 if conforme else 0
                    insertar_item_checklist(
                        checklist_id,
                        item,
                        cumple,
                        observacion
                    )

                    if no_conforme:

                        insertar_solicitud(
                            maquina_id,
                            f"{item} - {observacion}",
                            "Checklist"
                        )

                st.session_state.checklist_guardada = True
                st.rerun()

        # -------------------------
        # HISTORIAL DE CHECKLISTS
        # -------------------------

        st.subheader("Historial de checklists")

        checklists = obtener_checklists()

        if not checklists:
            st.info("Aún no hay checklists registradas.")

        else:

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.write("ID")
            col2.write("Tipo")
            col3.write("Máquina")
            col4.write("Fecha")
            col5.write("")

            for c in checklists:

                col1, col2, col3, col4, col5 = st.columns(5)

                col1.write(c[0])
                col2.write(c[1])
                col3.write(c[2])
                col4.write(c[3])
                
                if f"confirmar_checklist_{c[0]}" not in st.session_state:
                    st.session_state[f"confirmar_checklist_{c[0]}"] = False

                if not st.session_state[f"confirmar_checklist_{c[0]}"]:

                    if col5.button("Eliminar", key=f"del_checklist_{c[0]}"):
                        st.session_state[f"confirmar_checklist_{c[0]}"] = True

                else:

                    col5.warning("¿Confirmar?")

                    colA, colB = st.columns(2)

                    if colA.button("Sí", key=f"si_checklist_{c[0]}"):

                        eliminar_checklist(c[0])

                        st.success("Checklist eliminada")

                        del st.session_state[f"confirmar_checklist_{c[0]}"]

                        st.rerun()

                    if colB.button("No", key=f"no_checklist_{c[0]}"):

                        st.session_state[f"confirmar_checklist_{c[0]}"] = False

                        st.rerun()
                
elif opcion == "Registro de Mantenimientos":

    st.header("Registro de mantenimiento / fallas")

    # Inicializamos flag de éxito
    if "mantenimiento_exitoso" not in st.session_state:
        st.session_state.mantenimiento_exitoso = False

    maquinas = obtener_maquinas()

    if not maquinas:
        st.warning("Primero debes registrar al menos una máquina.")
    else:
        maquina_opciones = {f"{m[2]} - {m[1]}": m[0] for m in maquinas}

        with st.form("form_mantenimiento"):

            # Inputs del formulario
            maquina_seleccionada = st.selectbox(
                "Máquina",
                list(maquina_opciones.keys())
            )
            
            maquina_id = maquina_opciones[maquina_seleccionada]

            # Buscar solicitudes pendientes
            solicitudes_pendientes = obtener_solicitudes_pendientes_por_maquina(maquina_id)

            solicitudes_dict = {}
            
            if solicitudes_pendientes:

                st.subheader("Solicitudes pendientes de esta máquina")

                for s in solicitudes_pendientes:
                    solicitudes_dict[f"{s[0]} - {s[1]}"] = s[0]

                solicitudes_seleccionadas = st.multiselect(
                    "Seleccionar solicitudes atendidas",
                    list(solicitudes_dict.keys())
                )
            
            else:

                st.info("Esta máquina no tiene solicitudes pendientes")
                solicitudes_seleccionadas = []

            fecha = st.date_input("Fecha")

            tipo_evento = st.selectbox(
                "Tipo de evento",
                ["Correctivo", "Preventivo"]
            )

            descripcion_falla = st.text_area("Falla detectada")

            accion_realizada = st.text_area("Acción realizada")

            responsable = st.text_input("Responsable")

            estado_final = st.selectbox(
                "Estado final de la máquina",
                ["Operativa", "En mantenimiento", "Fuera de servicio"]
            )

            estado_solicitud = st.selectbox(
                "Estado de la solicitud",
                ["Pendiente", "Cerrado"]
            )

            submitted = st.form_submit_button("Registrar mantenimiento")

            if submitted:
                # Insertar mantenimiento
                insertar_mantenimiento(
                    maquina_id,
                    str(fecha),
                    tipo_evento,
                    descripcion_falla,
                    accion_realizada,
                    responsable,
                    estado_final,
                    estado_solicitud
                )
                
                # cerrar solicitudes seleccionadas
                if solicitudes_seleccionadas:

                    ids_solicitudes = [
                        solicitudes_dict[s] for s in solicitudes_seleccionadas
                ]
                cerrar_solicitudes(ids_solicitudes)

                # Setear flag de éxito
                st.session_state.mantenimiento_exitoso = True

        # Mostrar mensaje de éxito fuera del formulario
        if st.session_state.mantenimiento_exitoso:
            st.success("Evento de mantenimiento registrado")
            st.session_state.mantenimiento_exitoso = False
            st.rerun()

        # Historial de mantenimientos
        st.subheader("Historial de mantenimiento")
        mantenimientos = obtener_mantenimientos()

        if not mantenimientos:
            st.info("Aún no hay mantenimientos registrados.")
        else:
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)

            col1.write("ID")
            col2.write("Equipo")
            col3.write("Tipo máquina")
            col4.write("Fecha")
            col5.write("Tipo")
            col6.write("Falla")
            col7.write("Acción")
            col8.write("Responsable")
            col9.write("Estado final")
            col10.write("Eliminar")

            for m in mantenimientos:
                col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)

                col1.write(m[0])
                col2.write(m[1])
                col3.write(m[2])
                col4.write(m[3])
                col5.write(m[4])
                col6.write(m[5])
                col7.write(m[6])
                col8.write(m[7])
                col9.write(m[8])
                col10.write("Eliminar")

                # Botón para eliminar mantenimiento
                if col10.button("Eliminar", key=f"del_mant_{m[0]}"):
                    st.session_state["confirm_delete_id"] = m[0]

                # Confirmación de eliminación
                if "confirm_delete_id" in st.session_state and st.session_state["confirm_delete_id"] == m[0]:
                    st.warning("¿Seguro que quieres eliminar este registro?")
                    col_confirm, col_cancel = st.columns([1,1])

                    if col_confirm.button("Confirmar", key=f"confirm_{m[0]}"):
                        eliminar_mantenimiento(m[0])
                        del st.session_state["confirm_delete_id"]
                        st.rerun()

                    if col_cancel.button("Cancelar", key=f"cancel_{m[0]}"):
                        del st.session_state["confirm_delete_id"]
                        st.rerun()

elif opcion == "Solicitudes de Mantenimiento":

    st.header("Solicitudes de mantenimiento")

    solicitudes = obtener_solicitudes()

    if not solicitudes:
        st.info("No hay solicitudes registradas")

    else:

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        col1.write("ID")
        col2.write("Tipo")
        col3.write("Máquina")
        col4.write("Falla")
        col5.write("Fecha")
        col6.write("Estado")

        for s in solicitudes:

            col1, col2, col3, col4, col5, col6 = st.columns(6)

            col1.write(s[0])
            col2.write(s[1])
            col3.write(s[2])
            col4.write(s[3])
            col5.write(s[4])
            col6.write(s[5])

                    
elif opcion == "Control de Traslados":
    st.header("Control de Traslados")

    st.write("Aquí se registrará el traslado de maquinaria entre sedes.")

elif opcion == "Dashboard de Análisis":
    st.header("Dashboard de Análisis")

    st.write("Aquí se mostrarán las gráficas de análisis de fallas.")

elif opcion == "Hoja de Vida de Equipos":
    st.header("Hoja de Vida de Equipos")

    st.write("Aquí se mostrará el historial completo de cada máquina.")


