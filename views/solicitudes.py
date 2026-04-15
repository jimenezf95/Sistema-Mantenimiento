import streamlit as st

from database import (
    obtener_maquinas,
    insertar_solicitud,
    actualizar_estado_por_solicitudes
)

from config_checklist import checklists_por_tipo

def vista_solicitudes():
    
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
            key="sol_item",
            format_func=lambda x: x.upper() if x != "Seleccione una opción" else x
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