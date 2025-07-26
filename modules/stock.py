import streamlit as st
import pandas as pd
from config import CONFIG

def mostrar(conn):
    st.title("Gestión de Stock")
    
    # Obtener datos de stock
    try:
        stock_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["STOCK"]).get_all_records())
        productos_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records())
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    # Unir con información de productos
    if not stock_df.empty and not productos_df.empty:
        stock_df = stock_df.merge(
            productos_df[["nombre", "stock_minimo"]],
            left_on="producto",
            right_on="nombre",
            how="left"
        ).drop(columns=["nombre"])
    
    # Mostrar stock actual
    st.subheader("Stock Actual")
    if not stock_df.empty:
        # Resaltar productos con stock bajo
        def resaltar_bajo_stock(row):
            stock_minimo = float(row.get("stock_minimo", 0))
            stock_actual = float(row["stock_actual"])
            
            if stock_actual <= stock_minimo:
                return ['background-color: #ffcccc'] * len(row)
            elif stock_actual <= stock_minimo * 1.5:
                return ['background-color: #fff3cd'] * len(row)
            else:
                return [''] * len(row)
        
        st.dataframe(
            stock_df.style.apply(resaltar_bajo_stock, axis=1),
            use_container_width=True
        )
        
        # Alertas de stock bajo
        productos_bajo_stock = stock_df[
            (stock_df["stock_actual"].astype(float) <= stock_df["stock_minimo"].astype(float))
        ]
        
        if not productos_bajo_stock.empty:
            st.warning("⚠️ Alertas de Stock Bajo")
            for _, producto in productos_bajo_stock.iterrows():
                st.error(
                    f"{producto['producto']}: Stock actual {producto['stock_actual']} "
                    f"(mínimo recomendado: {producto['stock_minimo']})"
                )
    else:
        st.info("No hay productos en stock aún")
    
    # Proyección de stock
    st.subheader("Proyección de Stock")
    if not stock_df.empty:
        # Aquí podrías agregar lógica más compleja de proyección
        st.dataframe(
            stock_df[["producto", "stock_actual", "stock_proyectado"]],
            use_container_width=True
        )
    else:
        st.info("No hay datos de proyección disponibles")
