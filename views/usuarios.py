import streamlit as st
from database import (
    crear_usuario, 
    obtener_usuarios,
    eliminar_usuario,
    actualizar_usuario
)

if "edit_user_id" not in st.session_state:
    st.session_state.edit_user_id = None

if "confirm_delete_user" not in st.session_state:
    st.session_state.confirm_delete_user = None

def vista_usuarios():

    st.header("👤 Gestión de Usuarios")

    # =========================
    # CREAR USUARIO
    # =========================
    st.subheader("Crear nuevo usuario")

    col1, col2 = st.columns(2)

    with col1:
        nuevo_usuario = st.text_input("Usuario")

    with col2:
        nuevo_password = st.text_input("Contraseña", type="password")

    rol = st.selectbox("Rol", ["admin", "tecnico", "operario"])

    if st.button("Crear usuario"):

        if not nuevo_usuario or not nuevo_password:
            st.warning("Completa todos los campos")
        else:
            try:
                crear_usuario(nuevo_usuario, nuevo_password, rol)
                st.success("Usuario creado correctamente")
                st.rerun()
            except:
                st.error("El usuario ya existe")

    st.divider()

    st.subheader("Usuarios registrados")

    usuarios = obtener_usuarios()

    if not usuarios:
        st.info("No hay usuarios registrados")
    else:
        for u in usuarios:

            user_id = u[0]
            usuario = u[1]
            rol = u[2]

            col1, col2, col3 = st.columns([4,1,1])

            with col1:
                st.write(f"👤 {usuario} — {rol}")

            with col2:
                if st.button("✏️", key=f"edit_{user_id}"):
                    st.session_state.edit_user_id = user_id

            with col3:
                if st.button("🗑️", key=f"del_{user_id}"):
                    st.session_state.confirm_delete_user = user_id
                    
    # =========================
    # EDITAR USUARIO
    # =========================

    if st.session_state.edit_user_id is not None:

        st.divider()
        st.subheader("✏️ Editar usuario")

        user_id = st.session_state.edit_user_id

        nueva_password = st.text_input("Nueva contraseña (opcional)", type="password", key="edit_pass")

        nuevo_rol = st.selectbox(
            "Nuevo rol",
            ["admin", "tecnico", "operario"],
            key="edit_rol"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Guardar cambios"):

                actualizar_usuario(
                    user_id,
                    nueva_password if nueva_password else None,
                    nuevo_rol
                )

                st.success("Usuario actualizado")
                st.session_state.edit_user_id = None
                st.rerun()

        with col2:
            if st.button("Cancelar"):
                st.session_state.edit_user_id = None
                st.rerun()  
                
    # =========================
    # CONFIRMAR ELIMINAR
    # =========================

    if st.session_state.confirm_delete_user is not None:

        st.warning("⚠️ ¿Seguro que quieres eliminar este usuario?")

        col1, col2 = st.columns(2)

        with col1:
            
            if usuario == st.session_state.usuario:
                st.error("No puedes eliminar tu propio usuario")
            else:
                st.session_state.confirm_delete_user = user_id
                
            if st.button("✅ Sí, eliminar"):

                eliminar_usuario(st.session_state.confirm_delete_user)

                st.success("Usuario eliminado")
                st.session_state.confirm_delete_user = None
                st.rerun()

        with col2:
            if st.button("❌ Cancelar"):
                st.session_state.confirm_delete_user = None
                st.rerun()              
                        
    
    
    
    
    