import streamlit as st

from database import (
    obtener_maquinas,
    obtener_solicitudes_pendientes_por_maquina,
    registrar_mantenimiento,
    actualizar_estado_maquina,
    insertar_costo,
    obtener_costos_por_mantenimiento,
    obtener_mantenimientos_por_maquina
)

ESTADOS_OPERACION = [
    "Operativa",
    "Operativa con falla",
    "En mantenimiento",
    "Fuera de servicio"
]

def vista_mantenimientos():
    
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
        
    if "costos_temp" not in st.session_state:
        st.session_state.costos_temp = []

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
            error = False

            if not solicitudes_seleccionadas:
                st.error("Debe seleccionar al menos una solicitud.")
                error = True

            if not st.session_state.costos_temp:
                st.error("Debe agregar al menos un costo.")
                error = True
            
            # 🔥 SOLO SI NO HAY ERROR → GUARDAR    
            if not error:

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

                # -------------------------
                # GUARDAR COSTOS
                # -------------------------
                for c in st.session_state.costos_temp:
                    insertar_costo(
                        mantenimiento_id,
                        c["tipo"],
                        c["descripcion"],
                        c["cantidad"],
                        c["costo_unitario"]
                    )

                # LIMPIAR CAMPOS
                for key in ["desc_mo", "desc_rep", "desc_sc", "cant_rep", "costo_rep", "costo_mo"]:
                    if key in st.session_state:
                        del st.session_state[key]
                
                #  LIMPIAR COSTOS        
                st.session_state.costos_temp = []

                st.success("Mantenimiento registrado correctamente")
                # Limpiar cache 
                st.cache_data.clear()
                # Resetear formulario
                st.session_state.form_mantenimiento_key += 1

                st.rerun()
            
    
    
    
    st.subheader("💰 Costos del mantenimiento")

    tipo_costo = st.selectbox(
        "Tipo de costo",
        ["Mano de obra", "Repuestos", "Insumos", "Sin costo"],
        key="tipo_costo"
    )

    # -------------------------
    # DETECTAR CAMBIO DE TIPO
    # -------------------------
    if "tipo_costo_prev" not in st.session_state:
        st.session_state.tipo_costo_prev = tipo_costo

    if st.session_state.tipo_costo_prev != tipo_costo:

        # LIMPIAR CAMPOS
        for key in ["desc_mo", "desc_rep", "desc_sc", "cant_rep", "costo_rep", "costo_mo"]:
            if key in st.session_state:
                del st.session_state[key]

        st.session_state.tipo_costo_prev = tipo_costo

    # -------------------------
    # CAMPOS DINÁMICOS
    # -------------------------
    # Valores por defecto
    cantidad = 1
    costo_unitario = 0

    if tipo_costo == "Mano de obra":
        descripcion_costo = st.text_input("Descripción (obligatoria)", key="desc_mo")

        cantidad = 1  # fijo
        st.number_input("Cantidad", value=1, disabled=True)

        costo_unitario = st.text_input("Valor mano de obra", key="costo_mo")

    elif tipo_costo in ["Repuestos", "Insumos"]:
        descripcion_costo = st.text_input("Nombre del ítem", key="desc_rep")

        cantidad = st.number_input(
            "Cantidad",
            min_value=1,
            step=1,
            format="%d",
            key="cant_rep"
        )

        costo_unitario = st.text_input("Costo unitario", key="costo_rep")

    elif tipo_costo == "Sin costo":
        descripcion_costo = st.text_input("Descripción (obligatoria)", key="desc_sc")

        cantidad = 1
        costo_unitario = 0

        st.number_input("Cantidad", value=1, disabled=True)
        st.text_input("Costo", value="0", disabled=True)

    # -------------------------
    # BOTÓN AGREGAR COSTO
    # -------------------------
    agregar_costo = st.button("➕ Agregar costo")

    if agregar_costo:
        # VALIDACIONES
        if tipo_costo == "Mano de obra":
            if not descripcion_costo.strip():
                st.error("Debe agregar una descripción para la mano de obra")
                st.stop()

        elif tipo_costo in ["Repuestos", "Insumos"]:
            if not descripcion_costo.strip():
                st.error("Debe agregar el nombre del ítem")
                st.stop()
            if cantidad <= 0:
                st.error("La cantidad debe ser mayor a 0")
                st.stop()

        elif tipo_costo == "Sin costo":
            if not descripcion_costo.strip():
                st.error("Debe agregar una descripción")
                st.stop()
                
        # -------------------------
        # EVITAR DUPLICADOS
        # -------------------------
        if tipo_costo in ["Repuestos", "Insumos"]:

            for c in st.session_state.costos_temp:
                if (
                    c["tipo"] == tipo_costo and
                    c["descripcion"].strip().lower() == descripcion_costo.strip().lower()
                ):
                    st.error("Este ítem ya fue agregado")
                    st.stop()
                
        def limpiar_numero(valor):
            valor = valor.replace(".", "").replace(",", "")
            return float(valor) if valor else 0

        # Convertir costo a número
        costo_unitario = limpiar_numero(str(costo_unitario))
        
        # -------------------------
        # VALIDACIONES DE NEGOCIO
        # -------------------------

        if tipo_costo in ["Repuestos", "Insumos"]:
            if costo_unitario <= 0:
                st.error("Los repuestos/insumos deben tener un costo mayor a 0")
                st.stop()

        if tipo_costo == "Mano de obra":
            # puede ser 0 o mayor, pero ya validamos descripción antes
            pass

        if tipo_costo == "Sin costo":
            costo_unitario = 0
            cantidad = 1
        
        
        # FORMATEAR TEXTO
        def formatear_texto(texto):
            return texto.strip().capitalize()

        descripcion_costo = formatear_texto(descripcion_costo)

        # GUARDAR EN MEMORIA
        st.session_state.costos_temp.append({
            "tipo": tipo_costo,
            "descripcion": descripcion_costo,
            "cantidad": cantidad,
            "costo_unitario": costo_unitario
        })

        st.success("Costo agregado correctamente")
        st.rerun()
    
    if st.session_state.costos_temp:

        st.markdown("### 📋 Costos agregados")
        
        # -------------------------
        # TOTAL EN TIEMPO REAL
        # -------------------------
        total_mantenimiento = 0

        for c in st.session_state.costos_temp:
            cantidad = float(c["cantidad"])
            costo_unitario = float(c["costo_unitario"])
            total_mantenimiento += cantidad * costo_unitario

        total_formateado = f"{total_mantenimiento:,.0f}".replace(",", ".")

        st.markdown(f"## 💰 Total mantenimiento: ${total_formateado}")
        #st.metric("", f"${total_formateado}")

        for i, c in enumerate(st.session_state.costos_temp):

            col1, col2 = st.columns([4,1])

            with col1:
                cantidad = float(c["cantidad"])
                costo_unitario = float(c["costo_unitario"])
                total = cantidad * costo_unitario
                total_formateado = f"{total:,.0f}".replace(",", ".")
                st.write(f"{c['tipo']} - {c['descripcion']} → ${total_formateado}")

            with col2:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.costos_temp.pop(i)
                    st.rerun()
                    

                
                
                
                