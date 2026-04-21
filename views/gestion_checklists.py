import streamlit as st

from database import (
    obtener_categorias,
    obtener_items,
    crear_categoria,
    crear_item,
    editar_item,
    desactivar_item,
    obtener_checklists_paginados,
    contar_checklists,
    eliminar_checklist,
    obtener_maquinas,
    obtener_checklists_filtrados,
    contar_checklists_filtrados,
    obtener_detalle_checklist
)

from database import obtener_checklists_export
from utils.export import generar_excel_checklists


def vista_gestion_checklists():

    st.header("🛠 Gestión de Checklists")

    # =========================
    # TOGGLE EDIT MODE
    # =========================
    if "modo_edicion_checklist" not in st.session_state:
        st.session_state.modo_edicion_checklist = False

    col1, col2 = st.columns([2,1])

    with col1:
        if st.button("✏️ Editar Checklists"):
            st.session_state.modo_edicion_checklist = not st.session_state.modo_edicion_checklist
            st.rerun()

    if st.session_state.modo_edicion_checklist:
        st.warning("Modo edición activo")

        render_editor_checklists()   # 👈 separamos lógica

    st.divider()

    # =========================
    # HISTORIAL
    # =========================
    render_historial_checklists()


def render_editor_checklists():

    st.header("🛠 Gestión de Checklists")

    # =========================
    # SELECCIÓN TIPO MAQUINA
    # =========================
    TIPOS_MAQUINA = [
        "Compactadora",
        "Montacargas",
        "Cizalladora",
        "Briqueteadora",
        "Herramienta Manual y Potencia",
        "Equipo Oxicorte",
        "Otro"
    ]

    tipo_maquina = st.selectbox("Tipo de máquina", TIPOS_MAQUINA)

    if not tipo_maquina:
        return

    st.divider()

    # =========================
    # CREAR NUEVA CATEGORÍA
    # =========================
    with st.expander("➕ Crear nueva categoría"):

        nombre_categoria = st.text_input("Nombre de la categoría")
        orden_categoria = st.number_input("Orden", min_value=0, step=1)

        if st.button("Crear categoría"):

            if nombre_categoria.strip() == "":
                st.error("El nombre no puede estar vacío")
            else:
                crear_categoria(nombre_categoria, tipo_maquina, orden_categoria)
                st.success("Categoría creada")
                st.rerun()

    # =========================
    # LISTAR CATEGORÍAS
    # =========================
    categorias = obtener_categorias(tipo_maquina)

    if not categorias:
        st.warning("No hay categorías creadas")
        return

    for cat in categorias:

        st.subheader(f"📂 {cat['nombre']}")

        # =========================
        # CREAR ITEM
        # =========================
        with st.expander(f"➕ Agregar item en {cat['nombre']}"):

            nuevo_item = st.text_input(
                "Nombre del item",
                key=f"nuevo_item_{cat['id']}"
            )

            orden_item = st.number_input(
                "Orden",
                min_value=0,
                step=1,
                key=f"orden_item_{cat['id']}"
            )

            if st.button("Agregar item", key=f"btn_add_{cat['id']}"):

                if nuevo_item.strip() == "":
                    st.error("El item no puede estar vacío")
                else:
                    crear_item(cat["id"], nuevo_item, orden_item)
                    st.success("Item agregado")
                    st.rerun()

        # =========================
        # LISTAR ITEMS
        # =========================
        items = obtener_items(cat["id"])

        if not items:
            st.info("No hay items en esta categoría")
            continue

        for item in items:

            col1, col2, col3 = st.columns([4,1,1])

            with col1:
                st.write(item["nombre"])

            # ✏️ EDITAR
            with col2:
                if st.button("✏️", key=f"edit_{item['id']}"):
                    st.session_state[f"editando_{item['id']}"] = True

            # ❌ DESACTIVAR
            with col3:
                if st.button("🗑️", key=f"del_{item['id']}"):
                    desactivar_item(item["id"])
                    st.success("Item desactivado")
                    st.rerun()

            # =========================
            # MODO EDICIÓN
            # =========================
            if st.session_state.get(f"editando_{item['id']}"):

                nuevo_nombre = st.text_input(
                    "Nuevo nombre",
                    value=item["nombre"],
                    key=f"input_edit_{item['id']}"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Guardar", key=f"save_{item['id']}"):
                        editar_item(item["id"], nuevo_nombre)
                        st.success("Item actualizado")
                        del st.session_state[f"editando_{item['id']}"]
                        st.rerun()

                with col2:
                    if st.button("Cancelar", key=f"cancel_{item['id']}"):
                        del st.session_state[f"editando_{item['id']}"]
                        st.rerun()

        

def render_historial_checklists():

    st.subheader("📋 Historial de Checklists")

    # =========================
    # PAGINACIÓN
    # =========================
    if "pagina_checklists" not in st.session_state:
        st.session_state.pagina_checklists = 0

    LIMIT = 10
    OFFSET = st.session_state.pagina_checklists * LIMIT

    maquinas = obtener_maquinas()

    # =========================
    # FILTROS 🔥 (PRIMERO)
    # =========================
    tipo_filtro = st.selectbox(
        "Filtrar por",
        ["Sin filtro", "Fecha", "Tipo de máquina", "Máquina específica"]
    )

    fecha_inicio = None
    fecha_fin = None
    tipo_maquina = None
    maquina_id = None

    if tipo_filtro == "Fecha":
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde")
        with col2:
            fecha_fin = st.date_input("Hasta")

    elif tipo_filtro == "Tipo de máquina":
        tipos = sorted(list(set([m[2] for m in maquinas])))
        tipo_maquina = st.selectbox("Tipo", tipos)

    elif tipo_filtro == "Máquina específica":
        maquinas_dict = {
            f"{m[1]} | {m[2]} | {m[3]}": m[0] for m in maquinas
        }
        seleccion = st.selectbox("Máquina", list(maquinas_dict.keys()))
        maquina_id = maquinas_dict.get(seleccion)

    # =========================
    # RESET PAGINACIÓN SI CAMBIA FILTRO
    # =========================
    if "filtro_anterior" not in st.session_state:
        st.session_state.filtro_anterior = None

    filtro_actual = (tipo_filtro, fecha_inicio, fecha_fin, tipo_maquina, maquina_id)

    if filtro_actual != st.session_state.filtro_anterior:
        st.session_state.pagina_checklists = 0
        st.session_state.filtro_anterior = filtro_actual

    # =========================
    # CONSULTA DB 🔥 (DESPUÉS)
    # =========================
    checklists = obtener_checklists_filtrados(
        LIMIT,
        OFFSET,
        fecha_inicio,
        fecha_fin,
        tipo_maquina,
        maquina_id
    )

    total = contar_checklists_filtrados(
        fecha_inicio,
        fecha_fin,
        tipo_maquina,
        maquina_id
    )
    
    

    if not checklists:
        st.info("No hay registros")
        return

    for c in checklists:

        checklist_id = c[0]
        fecha = c[1]
        maquina_id_registro = c[2]

        maquina = next((m for m in maquinas if m[0] == maquina_id_registro), None)

        nombre_maquina = f"{maquina[2]} - {maquina[3]}" if maquina else "Desconocida"

        col1, col2, col3 = st.columns([4,1,1])

        with col1:
            st.write(f"🛠 {nombre_maquina} | 📅 {fecha}")
            
        with col2:
            if st.button("👁", key=f"view_{checklist_id}_{st.session_state.pagina_checklists}"):
                st.session_state["ver_checklist"] = checklist_id

        with col3:
            if st.button("🗑️", key=f"hist_del_{checklist_id}_{st.session_state.pagina_checklists}"):
                st.session_state[f"confirm_{checklist_id}"] = True

        if st.session_state.get("ver_checklist") == checklist_id:

            detalle = obtener_detalle_checklist(checklist_id)


            # Filtrar solo no conformes
            no_conformes = [(item, obs) for item, cumple, obs in detalle if not cumple]

            st.markdown("### 🔍 Detalle del checklist")

            # Caso 1: SIN FALLAS
            if len(no_conformes) == 0:
                st.success("✅ No se encontraron no conformidades en esta checklist")

            # Caso 2: CON FALLAS
            else:
                st.error(f"⚠️ Se encontraron {len(no_conformes)} no conformidades")

                for item, obs in no_conformes:
                    st.write(f"❌ {item}")
                    if obs:
                        st.write(f"📝 {obs}")
                    st.divider()

            if st.button("Cerrar", key=f"close_{checklist_id}"):
                del st.session_state["ver_checklist"]
                st.rerun()
        
        
        
        
        
        
        
        # =========================
        # CONFIRMACIÓN
        # =========================
        if st.session_state.get(f"confirm_{checklist_id}"):

            st.warning("¿Seguro que deseas eliminar este checklist?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Sí", key=f"hist_yes_{checklist_id}_{st.session_state.pagina_checklists}"):
                    eliminar_checklist(checklist_id)
                    st.success("Checklist eliminada")
                    del st.session_state[f"confirm_{checklist_id}"]
                    st.rerun()

            with col2:
                if st.button("❌ No", key=f"hist_no_{checklist_id}_{st.session_state.pagina_checklists}"):
                    del st.session_state[f"confirm_{checklist_id}"]
                    st.rerun()

    # =========================
    # CONTROLES PAGINACIÓN
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Anterior"):
            if st.session_state.pagina_checklists > 0:
                st.session_state.pagina_checklists -= 1
                st.rerun()

    with col2:
        if st.button("Siguiente ➡️"):
            if OFFSET + LIMIT < total:
                st.session_state.pagina_checklists += 1
                st.rerun()
                
    total_paginas = (total // LIMIT) + (1 if total % LIMIT > 0 else 0)
    pagina_actual = st.session_state.pagina_checklists + 1

    st.markdown(f"Página {pagina_actual} de {total_paginas} | Total registros: {total}")

    
    
    st.divider()
    st.subheader("📥 Exportar checklists")

    if st.button("Exportar historial de checklists"):

        # TEXTO Y NOMBRE DINÁMICO
        if tipo_filtro == "Máquina específica":
            texto = "para máquina seleccionada"
            nombre = "checklists_maquina"

        elif tipo_filtro == "Tipo de máquina":
            texto = f"para {tipo_maquina}"
            nombre = f"checklists_{tipo_maquina}"

        elif tipo_filtro == "Fecha":
            texto = f"de {fecha_inicio} a {fecha_fin}"
            nombre = f"checklists_{fecha_inicio}_{fecha_fin}"

        else:
            texto = "completo"
            nombre = "checklists_completo"

        st.session_state.confirmar_export_checklists = True
        st.session_state.nombre_archivo_checklists = nombre
        st.session_state.texto_export_checklists = texto
    
    if st.session_state.get("confirmar_export_checklists"):

        st.warning(
            f"¿Desea descargar el historial de checklists {st.session_state.texto_export_checklists}?"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Descargar"):

                data = obtener_checklists_export(
                    fecha_inicio,
                    fecha_fin,
                    tipo_maquina,
                    maquina_id
                )

                st.session_state.excel_checklists = generar_excel_checklists(data)
                st.session_state.confirmar_export_checklists = False

        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirmar_export_checklists = False
                st.rerun()
    
    if st.session_state.get("excel_checklists"):

        st.download_button(
            label="⬇️ Descargar Excel de checklists",
            data=st.session_state.excel_checklists,
            file_name=f"{st.session_state.nombre_archivo_checklists}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    
    



   
    
    
    