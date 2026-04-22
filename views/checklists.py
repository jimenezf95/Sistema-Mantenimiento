import streamlit as st

@st.cache_data(ttl=60)
def obtener_maquinas_cached():
    return obtener_maquinas()

@st.cache_data(ttl=60)
def obtener_categorias_cached(tipo_maquina):
    return obtener_categorias(tipo_maquina)

@st.cache_data(ttl=60)
def obtener_items_cached(categoria_id):
    return obtener_items(categoria_id)


from database import (
    obtener_maquinas,
    insertar_checklist,
    insertar_item_checklist,
    obtener_items_checklist,
    obtener_ultimos_checklists_por_maquina,
    obtener_checklists_por_sede,
    obtener_checklists_por_ciudad,
    obtener_ultimos_checklists,
    eliminar_checklist,
    insertar_solicitud,
    actualizar_estado_por_solicitudes, 
    obtener_categorias,
    obtener_items
)


def vista_checklists():

    params = st.query_params
    maquina_id_qr = None

    if "maquina_id" in params:
        try:
            valor = params["maquina_id"]
            if isinstance(valor, list):
                valor = valor[0]
            maquina_id_qr = int(valor)
        except:
            maquina_id_qr = None

    if maquina_id_qr:
        vista_checklist_qr(maquina_id_qr)
    else:
        vista_checklist_manual()


def vista_checklist_qr(maquina_id_qr):
    
    if st.session_state.get("checklist_completada"):

        resumen = st.session_state.get("resumen_checklist", {})
        maquinas = obtener_maquinas_cached()
        maquinas_dict = {int(m[0]): m for m in maquinas}
        maquina = maquinas_dict.get(maquina_id_qr)
        
        if not maquina:
            st.error("Máquina no encontrada")
            return
        
        st.markdown("""
        <div style="text-align:center; padding:30px;">
            <h2>✅ Checklist completada</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="
            background-color:#000000;
            padding:20px;
            border-radius:10px;
            text-align:center;
            font-size:18px;
        ">
            <b>{maquina[2]}</b>
            {maquina[3]}<br>
            {maquina[8]} - {maquina[7]}<br>
            <b>Fallas detectadas:</b> {resumen.get("fallas", 0)}
        </div>
        """, unsafe_allow_html=True)

        st.success("Registro guardado correctamente")

        st.info("Puede cerrar esta página")

        return

    maquinas = obtener_maquinas_cached()
    #maquina = next((m for m in maquinas if int(m[0]) == maquina_id_qr), None)
    maquinas_dict = {int(m[0]): m for m in maquinas}
    maquina = maquinas_dict.get(maquina_id_qr)
    
    
    
    if not maquina:
        st.error("Máquina no encontrada")
        return

    tipo_maquina = maquina[2]

    # HEADER
    st.markdown("""
    <div style="
        background-color:#0F2A44;
        padding:15px;
        border-radius:10px;
        color:white;
        text-align:center;
        font-size:20px;
        font-weight:bold;
    ">
        📋 CHECKLIST PREOPERACIONAL
    </div>
    """, unsafe_allow_html=True)

    # INFO
    st.markdown(f"""
    <div style="
        background-color:#000000;
        padding:12px;
        border-radius:10px;
        margin-top:10px;
    ">
        <b>{maquina[2]}</b><br>
        {maquina[3]}<br>
        {maquina[8]} - {maquina[7]}
    </div>
    """, unsafe_allow_html=True)

    render_formulario(maquina_id_qr, tipo_maquina, origen="QR", modo="movil")

def vista_checklist_manual():
    st.subheader("Crear registro manual de Checklist")

    maquinas = obtener_maquinas_cached()

    if not maquinas:
        st.warning("Primero debes registrar máquinas.")
        return

    with st.form("form_seleccion_maquina"):

        ciudades = sorted(list(set([m[8] for m in maquinas if m[8] is not None])))
        ciudad = st.selectbox("Ciudad", ciudades)

        maquinas_ciudad = [m for m in maquinas if m[8] == ciudad]

        sedes = sorted(list(set([m[7] for m in maquinas_ciudad if m[7] is not None])))
        sede = st.selectbox("Sede", sedes)

        maquinas_sede = [m for m in maquinas_ciudad if m[7] == sede]

        maquinas_dict = {
            f"{m[1]} | {m[2]} | {m[3]}": m for m in maquinas_sede
        }

        seleccion = st.selectbox("Seleccione la máquina", list(maquinas_dict.keys()))

        submitted = st.form_submit_button("Continuar")

    if not submitted:
        return

    maquina = maquinas_dict.get(seleccion)

    if not maquina:
        st.error("Máquina no encontrada")
        return

    maquina_id = maquina[0]
    tipo_maquina = maquina[2]

    render_formulario(maquina_id, tipo_maquina, origen="Manual", modo="desktop")


def render_formulario(maquina_id, tipo_maquina, origen, modo):
    
    if "form_checklist_key" not in st.session_state:
        st.session_state.form_checklist_key = 0

    fecha = st.date_input("Fecha de inspección")

    categorias = obtener_categorias_cached(tipo_maquina)

    if not categorias:
        st.warning("No hay checklist configurado para este tipo de máquina")
        return
        
    if "form_checklist_key" not in st.session_state:
        st.session_state.form_checklist_key = 0

    with st.form(f"form_checklist_{st.session_state.form_checklist_key}"):

        respuestas = {}

        for cat in categorias:

            st.markdown(f"### 🔧 {cat['nombre']}")

            items = obtener_items_cached(cat["id"])

            for item_data in items:

                item = item_data["nombre"]
                item_id = item_data["id"]

                if modo == "movil":

                    estado = st.radio(
                        item,
                        ["Cumple", "No cumple"],
                        horizontal=True,
                        key=f"estado_{item_id}_{st.session_state.form_checklist_key}"
                    )

                    observacion = ""
                    if estado == "No cumple":
                        observacion = st.text_area(
                            "Observación",
                            key=f"obs_{item_id}_{st.session_state.form_checklist_key}"
                        )

                else:

                    col1, col2, col3 = st.columns([3,3,3])

                    col1.write(item)

                    estado = col2.radio(
                        "",
                        ["Conforme", "No conforme"],
                        horizontal=True,
                        key=f"estado_{item_id}_{st.session_state.form_checklist_key}"
                    )

                    observacion = col3.text_input(
                        "",
                        key=f"obs_{item_id}_{st.session_state.form_checklist_key}"
                    )

                if modo == "movil":
                    conforme = estado == "Cumple"
                    no_conforme = estado == "No cumple"
                else:
                    conforme = estado == "Conforme"
                    no_conforme = estado == "No conforme"

                respuestas[item_id] = (item, conforme, no_conforme, observacion)

        submitted = st.form_submit_button("🚀 Guardar Checklist")

        if submitted:
            
            # VALIDAR OBSERVACIONES
            for item_id, (item, conforme, no_conforme, obs) in respuestas.items():
                if no_conforme and obs.strip() == "":
                    st.error(f"Debes escribir una observación para: {item}")
                    st.stop()

            checklist_id = insertar_checklist(
                maquina_id,
                fecha.isoformat(),
                origen
            )

            st.session_state["ultima_checklist"] = checklist_id

            fallas_detectadas = 0

            for item_id, (item, conforme, no_conforme, obs) in respuestas.items():

                insertar_item_checklist(checklist_id, item, int(conforme), obs, item_id)

                if no_conforme:
                    fallas_detectadas += 1

                    creada, veces = insertar_solicitud(
                        maquina_id,
                        item,
                        obs,
                        "Checklist"
                    )

                    actualizar_estado_por_solicitudes(maquina_id)

                    if not creada:
                        st.info(f"Falla repetida ({veces} veces): {item}")
                
            # 🔥 Guardar estado para modo QR
            st.session_state["checklist_completada"] = True
            st.session_state["resumen_checklist"] = {
                "fallas": fallas_detectadas,
                "maquina_id": maquina_id,
                
            }
            
            #st.session_state.checklist_msg = f"Checklist guardada exitosamente. Fallas detectadas: {fallas_detectadas}"
            # 🔁 Reset form
            st.session_state.form_checklist_key += 1
            
            st.rerun()
            
    if "checklist_msg" in st.session_state:
        st.success(st.session_state.checklist_msg)
        del st.session_state.checklist_msg


           