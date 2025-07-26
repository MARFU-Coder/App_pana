import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from config import CONFIG

def mostrar(conn):
    st.title("Gestión Financiera")
    
    # Obtener datos de finanzas
    try:
        finanzas_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["FINANZAS"]).get_all_records())
    except Exception as e:
        st.error(f"Error al cargar datos financieros: {e}")
        return
    
    # Convertir fechas y montos
    if not finanzas_df.empty:
        finanzas_df['fecha'] = pd.to_datetime(finanzas_df['fecha'])
        finanzas_df['monto'] = pd.to_numeric(finanzas_df['monto'])
    
    # Filtros
    st.sidebar.header("Filtros Financieros")
    fecha_inicio = st.sidebar.date_input(
        "Fecha de inicio",
        value=datetime.now() - timedelta(days=30),
        key="fin_inicio"
    )
    fecha_fin = st.sidebar.date_input(
        "Fecha de fin",
        value=datetime.now()),
        key="fin_fin"
    )
    tipo_seleccionado = st.sidebar.multiselect(
        "Tipo de movimiento",
        options=CONFIG["TIPOS_FINANZAS"],
        default=CONFIG["TIPOS_FINANZAS"]
    )
    categoria_seleccionada = st.sidebar.multiselect(
        "Categoría",
        options=CONFIG["CATEGORIAS_FINANZAS"],
        default=CONFIG["CATEGORIAS_FINANZAS"]
    )
    
    # Aplicar filtros
    if not finanzas_df.empty:
        finanzas_filtradas = finanzas_df[
            (finanzas_df['fecha'].dt.date >= fecha_inicio) &
            (finanzas_df['fecha'].dt.date <= fecha_fin) &
            (finanzas_df['tipo'].isin(tipo_seleccionado)) &
            (finanzas_df['categoria'].isin(categoria_seleccionada))
        ]
    else:
        finanzas_filtradas = pd.DataFrame()
    
    # Resumen financiero
    st.header("Resumen Financiero")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not finanzas_filtradas.empty:
            ingresos = finanzas_filtradas[finanzas_filtradas['tipo'] == 'Ingreso']['monto'].sum()
            st.metric("Total Ingresos", f"${ingresos:,.2f}")
        else:
            st.metric("Total Ingresos", "$0.00")
    
    with col2:
        if not finanzas_filtradas.empty:
            gastos = finanzas_filtradas[finanzas_filtradas['tipo'] == 'Gasto']['monto'].sum()
            st.metric("Total Gastos", f"${gastos:,.2f}")
        else:
            st.metric("Total Gastos", "$0.00")
    
    with col3:
        if not finanzas_filtradas.empty:
            balance = ingresos - gastos
            st.metric("Balance", f"${balance:,.2f}", delta_color="inverse")
        else:
            st.metric("Balance", "$0.00")
    
    # Gráficos
    st.header("Visualización de Datos Financieros")
    
    if not finanzas_filtradas.empty:
        # Gráfico de ingresos vs gastos por período
        st.subheader("Ingresos vs Gastos por Período")
        finanzas_por_fecha = finanzas_filtradas.groupby(['fecha', 'tipo'])['monto'].sum().unstack().reset_index()
        finanzas_por_fecha['fecha'] = finanzas_por_fecha['fecha'].dt.date
        
        fig = px.bar(
            finanzas_por_fecha,
            x='fecha',
            y=['Ingreso', 'Gasto'],
            barmode='group',
            title='Ingresos y Gastos por Día'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de distribución por categoría
        st.subheader("Distribución por Categoría")
        finanzas_por_categoria = finanzas_filtradas.groupby(['tipo', 'categoria'])['monto'].sum().reset_index()
        
        fig = px.sunburst(
            finanzas_por_categoria,
            path=['tipo', 'categoria'],
            values='monto',
            title='Distribución de Ingresos y Gastos por Categoría'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos financieros para mostrar con los filtros actuales")
    
    # Registro manual de movimientos financieros
    st.header("Registro Manual de Movimientos")
    
    with st.form("form_finanzas"):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox(
                "Tipo",
                options=CONFIG["TIPOS_FINANZAS"],
                index=0
            )
            fecha = st.date_input("Fecha", datetime.today())
            categoria = st.selectbox(
                "Categoría",
                options=CONFIG["CATEGORIAS_FINANZAS"],
                index=0
            )
        
        with col2:
            monto = st.number_input("Monto", min_value=0.0, value=0.0, step=0.1)
            detalle = st.text_area("Detalle")
        
        submitted = st.form_submit_button("Registrar Movimiento")
        
        if submitted:
            if monto <= 0:
                st.error("El monto debe ser mayor a cero")
            else:
                nuevo_movimiento = {
                    "tipo": tipo,
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "categoria": categoria,
                    "monto": monto,
                    "detalle": detalle
                }
                
                try:
                    # Agregar a Google Sheets
                    hoja_finanzas = conn.worksheet(CONFIG["HOJAS"]["FINANZAS"])
                    hoja_finanzas.append_row(list(nuevo_movimiento.values()))
                    
                    st.success("Movimiento financiero registrado exitosamente!")
                    st.session_state.ultimo_movimiento = nuevo_movimiento
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar el movimiento: {e}")
    
    # Mostrar último movimiento registrado
    if 'ultimo_movimiento' in st.session_state:
        st.subheader("Último movimiento registrado")
        st.json(st.session_state.ultimo_movimiento)
    
    # Mostrar todos los movimientos filtrados
    st.header("Detalle de Movimientos")
    if not finanzas_filtradas.empty:
        st.dataframe(finanzas_filtradas.sort_values('fecha', ascending=False), use_container_width=True)
    else:
        st.info("No hay movimientos financieros para mostrar con los filtros actuales")
