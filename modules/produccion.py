import streamlit as st
from datetime import datetime
import pandas as pd
from config import CONFIG

def mostrar(conn):
    st.title("Registro de Producción")
    
    # Obtener datos necesarios
    try:
        productos_df = conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records()
        produccion_df = conn.worksheet(CONFIG["HOJAS"]["PRODUCCION"]).get_all_records()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    # Filtrar solo productos elaborados
    productos_elaborados = [p["nombre"] for p in productos_df if p.get("es_elaborado", "si") == "si"]
    
    # Formulario de producción
    with st.form("form_produccion"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha", datetime.today())
            producto = st.selectbox(
                "Producto Elaborado",
                options=productos_elaborados,
                index=0
            )
        
        with col2:
            cantidad = st.number_input("Cantidad Horneada", min_value=1, value=1, step=1)
        
        submitted = st.form_submit_button("Guardar Producción")
        
        if submitted:
            nueva_produccion = {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "producto": producto,
                "cantidad": cantidad
            }
            
            try:
                # Agregar a Google Sheets
                hoja_produccion = conn.worksheet(CONFIG["HOJAS"]["PRODUCCION"])
                hoja_produccion.append_row(list(nueva_produccion.values()))
                
                # Actualizar stock
                actualizar_stock(conn, producto, cantidad)
                
                st.success("Producción registrada exitosamente!")
                st.session_state.ultima_produccion = nueva_produccion
            except Exception as e:
                st.error(f"Error al guardar la producción: {e}")
    
    # Mostrar última producción registrada
    if 'ultima_produccion' in st.session_state:
        st.subheader("Última producción registrada")
        st.json(st.session_state.ultima_produccion)
    
    # Mostrar historial de producción
    st.subheader("Historial de Producción")
    if produccion_df:
        st.dataframe(pd.DataFrame(produccion_df))
    else:
        st.info("No hay producción registrada aún")

def actualizar_stock(conn, producto, cantidad):
    """Actualiza el stock del producto elaborado"""
    try:
        hoja_stock = conn.worksheet(CONFIG["HOJAS"]["STOCK"])
        stock_df = pd.DataFrame(hoja_stock.get_all_records())
        
        if producto in stock_df["producto"].values:
            # Producto existe en stock, actualizar cantidad
            idx = stock_df[stock_df["producto"] == producto].index[0]
            stock_actual = int(stock_df.at[idx, "stock_actual"])
            nuevo_stock = stock_actual + cantidad
            
            hoja_stock.update_cell(idx + 2, 2, nuevo_stock)  # +2 porque 1 es header y pandas index desde 0
        else:
            # Producto nuevo, agregar fila
            nuevo_registro = {
                "producto": producto,
                "stock_actual": cantidad,
                "stock_proyectado": cantidad
            }
            hoja_stock.append_row(list(nuevo_registro.values()))
    except Exception as e:
        raise Exception(f"Error al actualizar stock: {e}")
