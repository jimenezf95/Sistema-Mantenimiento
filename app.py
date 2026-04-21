from database import (crear_usuario, crear_tabla_usuarios)
#crear_tabla_usuarios()
#crear_usuario("admin2", "21100", "admin")

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
    #Historial
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
    #Usuarios
    validar_usuario,
)

from views.maquinaria import (
    vista_registro_maquinaria,
    vista_inventario_maquinas,
    vista_registro_sedes,
    vista_traslados
)

from views.checklists import vista_checklists
from views.solicitudes import vista_solicitudes
from views.mantenimiento import vista_mantenimientos
from views.dashboard_general import vista_dashboard_general
from views.historiales import vista_historial_solicitudes
from views.historiales import vista_historial_mantenimientos
from views.hoja_vida import vista_hoja_vida
from views.dashboard_costos import vista_dashboard_costos
from views.usuarios import vista_usuarios
from views.gestion_checklists import vista_gestion_checklists

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

from config_checklist import checklists_por_tipo
from utils.migrar_checklist import migrar
#migrar()


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
crear_tabla_usuarios()
#crear_usuario("Admin", "21100", "admin")


# =========================
# LOGIN
# =========================

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 Iniciar sesión")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        rol = validar_usuario(usuario, password)

        if rol:
            st.session_state.login = True
            st.session_state.usuario = usuario
            st.session_state.rol = rol
            st.success("Ingreso exitoso")
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

    st.stop()
    




params = st.query_params
modo_qr = "maquina_id" in params


# Título página principal
st.title("Sistema de Gestión de Mantenimiento de Maquinaria")

if modo_qr:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

if modo_qr:
    st.session_state.opcion = "Checklists Diarias"
else:
    if "opcion" not in st.session_state:
        st.session_state.opcion = "Inicio"


        
if not modo_qr:

    st.sidebar.title("Menú del sistema")
    
    
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"Rol: {st.session_state.rol}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
        
    rol = st.session_state.rol      

    # -----------------------------
    # INICIO
    # -----------------------------
    if st.sidebar.button("🏠 Inicio"):
        st.session_state.opcion = "Inicio" 
    # -----------------------------
    # MAQUINARIA
    # -----------------------------   
    with st.sidebar.expander("Maquinaria"):
    
        if rol in ["admin", "tecnico"]:
            if st.button("Inventario de Máquinas"):
                st.session_state.opcion = "Inventario de Máquinas"
                
        if rol == "admin":
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
    
        if rol in ["admin", "tecnico", "operario"]:
            if st.button("Registro de Checklists"):
                st.session_state.opcion = "Registro de Checklists"

        if rol in ["admin", "tecnico"]:
            if st.button("Solicitudes de Mantenimiento"):
                st.session_state.opcion = "Solicitudes de Mantenimiento"

            if st.button("Registro de Mantenimientos"):
                st.session_state.opcion = "Registro de Mantenimientos"
    # -----------------------------
    # REPORTES
    # -----------------------------
    with st.sidebar.expander("Historial"):
                
        if rol in ["admin", "tecnico"]:
            if st.button("Historial de Mantenimientos"):
                st.session_state.opcion = "Historial de Mantenimientos"

            if st.button("Historial de Solicitudes"):
                st.session_state.opcion = "Historial de Solicitudes"
                
            if st.button("Gestión de Checklists"):
                st.session_state.opcion = "Gestión de Checklists"

            if st.button("Hoja de Vida de Equipos"):
                st.session_state.opcion = "Hoja de Vida de Equipos"
    
    
    # -----------------------------
    # ANALISIS
    # -----------------------------        
    with st.sidebar.expander("Análisis"):
    
        if rol in ["admin", "tecnico"]:
            if st.button("Dashboard General"):
                st.session_state.opcion = "Dashboard General"
                
            if st.button("Dashboard de Costos"):
                st.session_state.opcion = "Dashboard de Costos"
                
        if rol == "admin":
            if st.button("Gestión de Usuarios"):
                st.session_state.opcion = "Gestión de Usuarios"


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
    
# Bloque Maquinaría
elif opcion == "Registro de Maquinaria":
    vista_registro_maquinaria()

elif opcion == "Registro de Sedes":
    vista_registro_sedes()

elif opcion == "Inventario de Máquinas":
    vista_inventario_maquinas()

elif opcion == "Control de Traslados":
    vista_traslados()


# Bloque mantenimiento
elif opcion == "Registro de Checklists":
    vista_checklists()

elif opcion == "Solicitudes de Mantenimiento":
    vista_solicitudes()
               
elif opcion == "Registro de Mantenimientos":
    vista_mantenimientos()


# Bloque historial    
elif opcion == "Historial de Solicitudes":
    vista_historial_solicitudes()
    
elif opcion == "Historial de Mantenimientos":
    vista_historial_mantenimientos()

elif opcion == "Hoja de Vida de Equipos":
    vista_hoja_vida()
    
elif opcion == "Gestión de Checklists":
    vista_gestion_checklists()


# Bloque Analisis    
elif opcion == "Dashboard General":
    vista_dashboard_general()
    
elif opcion == "Dashboard de Costos":
    vista_dashboard_costos()
    
elif opcion == "Gestión de Usuarios":
    vista_usuarios()


