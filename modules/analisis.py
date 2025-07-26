import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from config import CONFIG

def mostrar(conn):
    st.title("Análisis y Reportes")
    
    # Obtener datos para análisis
    try:
        compras_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["COMPRAS"]).get_all_records())
        ventas_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["VENTAS"]).get_all_records())
        produccion_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["PRODUCCION"]).get_all_records())
        finanzas_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["FINANZAS"]).get_all_records())
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    # Convertir fechas y valores numéricos
    for df in [compras_df, ventas_df, produccion_df, finanzas_df]:
        if not df.empty and 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
    
    if not compras_df.empty:
        compras_df['total'] = compras_df['cantidad'] * compras_df['precio_unitario']
    
    if not ventas_df.empty:
        ventas_df['total'] = ventas_df['cantidad'] * ventas_df['precio']
    
    # Filtros de fecha
    st.sidebar.header("Filtros")
    fecha_inicio = st.sidebar.date_input(
        "Fecha de inicio",
        value=datetime.now() - timedelta(days=30)
    )
    fecha_fin = st.sidebar.date_input(
        "Fecha de fin",
        value=datetime.now()
    )
    
    # Aplicar filtros
    def filtrar_por_fecha(df):
        if not df.empty and 'fecha' in df.columns:
            return df[(df['fecha'].dt.date >= fecha_inicio) & (df['fecha'].dt.date <= fecha_fin)]
        return df
    
    compras_filtradas = filtrar_por_fecha(compras_df)
    ventas_filtradas = filtrar_por_fecha(ventas_df)
    produccion_filtrada = filtrar_por_fecha(produccion_df)
    finanzas_filtradas = filtrar_por_fecha(finanzas_df)
    
    # Métricas clave
    st.header("Métricas Clave")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not ventas_filtradas.empty:
            total_ventas = ventas_filtradas['total'].sum()
            st.metric("Total Ventas", f"${total_ventas:,.2f}")
        else:
            st.metric("Total Ventas", "$0.00")
    
    with col2:
        if not compras_filtradas.empty:
            total_compras = compras_filtradas['total'].sum()
            st.metric("Total Compras", f"${total_compras:,.2f}")
        else:
            st.metric("Total Compras", "$0.00")
    
    with col3:
        if not finanzas_filtradas.empty:
            ingresos = finanzas_filtradas[finanzas_filtradas['tipo'] == 'Ingreso']['monto'].sum()
            gastos = finanzas_filtradas[finanzas_filtradas['tipo'] == 'Gasto']['monto'].sum()
            balance = ingresos - gastos
            st.metric("Balance", f"${balance:,.2f}")
        else:
            st.metric("Balance", "$0.00")
    
    # Gráficos
    st.header("Visualizaciones")
    
    if not ventas_filtradas.empty:
        st.subheader("Ventas por Producto")
        ventas_por_producto = ventas_filtradas.groupby('producto')['total'].sum().reset_index()
        fig = px.bar(
            ventas_por_producto,
            x='producto',
            y='total',
            title='Ventas Totales por Producto'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if not compras_filtradas.empty:
        st.subheader("Compras por Categoría")
        compras_por_categoria = compras_filtradas.groupby('categoria')['total'].sum().reset_index()
        fig = px.pie(
            compras_por_categoria,
            names='categoria',
            values='total',
            title='Distribución de Compras por Categoría'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if not produccion_filtrada.empty:
        st.subheader("Producción Mensual")
        produccion_filtrada['mes'] = produccion_filtrada['fecha'].dt.to_period('M').astype(str)
        produccion_mensual = produccion_filtrada.groupby('mes')['cantidad'].sum().reset_index()
        fig = px.line(
            produccion_mensual,
            x='mes',
            y='cantidad',
            title='Producción Mensual'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Exportar reporte
    st.header("Exportar Reporte")
    if st.button("Generar Reporte PDF"):
        st.warning("Funcionalidad de exportación a PDF no implementada aún")
        # Aquí iría el código para generar un PDF con los datos y gráficos
