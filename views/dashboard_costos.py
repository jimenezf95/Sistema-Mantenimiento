import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from database import *



def vista_dashboard_costos():

    st.header("Dashboard de Costos")

    # =========================
    # KPIs
    # =========================

    total, promedio, cantidad, ultima_fecha = obtener_kpis_costos()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total invertido", f"${int(total):,}".replace(",", "."))
    col2.metric("Promedio costo", f"${int(promedio):,}".replace(",", "."))
    col3.metric("Registros", cantidad)
    col4.metric("Último gasto", ultima_fecha)

    st.divider()    

    st.subheader("📅 Tendencia de costos por mes")

    datos_mes = obtener_costos_por_mes()

    if not datos_mes:
        st.info("No hay datos para mostrar")
    else:

        df_mes = pd.DataFrame(datos_mes, columns=["Mes", "Total"])

        # Convertir fecha
        df_mes["Mes"] = pd.to_datetime(df_mes["Mes"])
        df_mes = df_mes.sort_values(by="Mes")

        # Formato texto bonito
        df_mes["Mes_str"] = df_mes["Mes"].dt.strftime("%Y-%m")

        # 🔥 Crear gráfica
        fig = px.line(
            df_mes,
            x="Mes_str",
            y="Total",
            markers=True,  # 🔥 puntos
            title="Evolución de costos"
        )

        # 🔥 Formato hover (MUY IMPORTANTE)
        fig.update_traces(
            hovertemplate="Mes: %{x}<br>Costo: $%{y:,.0f}"
        )

        # 🔥 Mejorar diseño
        fig.update_layout(
            xaxis_title="Mes",
            yaxis_title="Costo",
            hovermode="x unified"
        )
        
        fig.update_traces(
            hovertemplate="Mes: %{x}<br>Costo: $%{y:,.0f}".replace(",", ".")
        )
        fig.update_traces(mode="lines+markers")
        fig.update_traces(line=dict(color="#1f77b4", width=3))

        # 🔥 Mostrar
        st.plotly_chart(fig, use_container_width=True)
    
    #for _, row in df_mes.iterrows():
        #total_fmt = f"{int(row['Total']):,}".replace(",", ".")
        #st.write(f"{row['Mes']} — ${total_fmt}")
    
    st.divider()    
    # =========================
    # RANKING DE COSTOS
    # =========================

    st.subheader("🏆 Máquinas con mayor costo")

    ranking = obtener_ranking_costos_maquinas()

    if not ranking:
        st.info("No hay datos de costos")
    else:

        col1, col2, col3 = st.columns(3)

        for i, r in enumerate(ranking[:3]):

            tipo = r[0]
            equipo = r[1]
            total = r[2]

            total_fmt = f"{int(total):,}".replace(",", ".")

            nombre = f"{tipo} {equipo}"

            if i == 0:
                col1.metric("🥇 Top 1", nombre, f"${total_fmt}")
            elif i == 1:
                col2.metric("🥈 Top 2", nombre, f"${total_fmt}")
            elif i == 2:
                col3.metric("🥉 Top 3", nombre, f"${total_fmt}")
                
        #for r in ranking:
            #st.write(f"🔴 {r[0]} {r[1]} — ${int(r[2]):,}".replace(",", "."))
    
    st.divider()    
        
        
    
    
    modo = st.radio(
        "Filtrar por",
        ["Sin filtro", "Fecha", "Tipo de máquina", "Máquina", "Tipo de costo"]
    )

    fecha_inicio = None
    fecha_fin = None
    tipo = None
    maquina = None
    tipo_costo = None
    
    maquinas = obtener_maquinas()

    
    if modo == "Fecha":

        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Desde")
        with col2:
            fecha_fin = st.date_input("Hasta")
            
    elif modo == "Tipo de máquina":

        tipos = ["Todos"] + sorted(list(set([m[2] for m in maquinas])))
        tipo = st.selectbox("Tipo de máquina", tipos)
        
    elif modo == "Máquina":

        # primero tipo
        tipos = ["Todos"] + sorted(list(set([m[2] for m in maquinas])))
        tipo = st.selectbox("Tipo de máquina", tipos)

        # filtrar máquinas
        if tipo == "Todos":
            maquinas_filtradas = maquinas
        else:
            maquinas_filtradas = [m for m in maquinas if m[2] == tipo]

        maquinas_dict = {
            f"{m[2]} {m[3]}": m[3] for m in maquinas_filtradas
        }

        maquina_sel = st.selectbox("Máquina", ["Todas"] + list(maquinas_dict.keys()))

        maquina = maquinas_dict.get(maquina_sel, None)    
        
    elif modo == "Tipo de costo":

        tipos_costos = ["Todos", "Repuestos", "Insumos", "Mano de obra", "Sin costo"]
        tipo_costo = st.selectbox("Tipo de costo", tipos_costos)
    
    
    
        
    costos = obtener_costos_filtrados(
        fecha_inicio,
        fecha_fin,
        tipo,
        maquina,
        tipo_costo
    )
    
    
    total_filtrado = sum([c[5] for c in costos]) if costos else 0

    st.subheader(f"💰 Total: ${int(total_filtrado):,}".replace(",", "."))
    
    for c in costos:

        fecha = c[0]
        tipo_m = c[1]
        equipo = c[2]
        tipo_c = c[3]
        desc = c[4]
        total = c[5]

        total_fmt = f"{int(total):,}".replace(",", ".")
        
        st.markdown(f"""
        **{tipo_m} {equipo}**  
        {tipo_c} — {desc}  
        💰 ${total_fmt} | 📅 {fecha}
        """)
        
    st.subheader("Costos por tipo")

    if costos:

        df = pd.DataFrame(costos, columns=["Fecha", "Tipo", "Equipo", "TipoCosto", "Desc", "Total"])

        df_tipo = df.groupby("TipoCosto")["Total"].sum().sort_values()

        st.bar_chart(df_tipo)
    else:
        st.info("No hay datos para graficar")

    