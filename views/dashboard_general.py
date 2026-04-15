import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import (
    calcular_disponibilidad,
    obtener_resumen_general,
    obtener_alertas,
    obtener_ranking_maquinas,
    obtener_top_fallas,
    obtener_ultimos_mantenimientos_dashboard,
    obtener_top_fallas_por_maquina
)

def vista_dashboard_general_1():
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

def vista_dashboard_general():
    st.header("Dashboard General de Mantenimiento")
    
    # =========================
    # KPI PRINCIPAL
    # =========================
    st.subheader("Resumen general")
    
    resumen = obtener_resumen_general()
    disponibilidad = calcular_disponibilidad()

    total_maquinas = sum(resumen.values())
    maquinas_falla = resumen["Operativa con falla"] + resumen["Fuera de servicio"]

    porcentaje_falla = (maquinas_falla / total_maquinas * 100) if total_maquinas > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Disponibilidad", f"{disponibilidad}%")
    col2.metric("Total máquinas", total_maquinas)
    col3.metric("% con fallas", f"{porcentaje_falla:.1f}%")

    
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🟢 Operativas", resumen["Operativa"])
    col2.metric("🟡 Con falla", resumen["Operativa con falla"])
    col3.metric("🔧 En mantenimiento", resumen["En mantenimiento"])
    col4.metric("🔴 Fuera de servicio", resumen["Fuera de servicio"])

    st.divider()
    # barra visual
    st.progress(int(disponibilidad))
    
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
        for i, row in df.sort_values(by="Fallas", ascending=False).iterrows():

            st.write(
                f"🔴 {row['Nombre']} — {int(row['Fallas'])} fallas"
            )
            
    st.divider()
            
    # =========================
    # FALLAS MÁS FRECUENTES
    # =========================
    st.subheader("Fallas más recurrentes")
    fallas = obtener_top_fallas_por_maquina()

    if not fallas:
        st.info("No hay fallas registradas.")
    else:
        # Preparar datos
        items = [f[0] for f in fallas]
        valores = [f[1] for f in fallas]

        df_fallas = pd.DataFrame({
            "Falla": items,
            "Cantidad": valores
        })

        # Ordenar (importante)
        df_fallas = pd.DataFrame(fallas, columns=["Tipo", "Equipo", "Falla", "Cantidad"])

        # 🔥 Crear nombre combinado
        df_fallas["Label"] = df_fallas["Falla"]
        df_fallas = df_fallas.sort_values(by="Cantidad", ascending=True).head(10)
            
        # Usar gráfico nativo
        st.bar_chart(
            df_fallas.set_index("Label")["Cantidad"]
        )
        
    max_val = max([f[3] for f in fallas]) if fallas else 1

    for f in fallas:

        nombre = f"{f[0]} {f[1]} - {f[2]}"
        total = f[3]

        porcentaje = int((total / max_val) * 100)

        st.markdown(f"**{nombre}** ({total})")
        st.progress(porcentaje)

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
    
    



