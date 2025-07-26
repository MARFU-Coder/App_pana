import streamlit as st
from datetime import datetime
import pandas as pd
from config import CONFIG

def mostrar(conn):
    st.title("Registro de Compras")
    
    # Obtener datos necesarios
    try:
        productos_df = conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records()
        proveedores_df = conn.worksheet(CONFIG["HOJAS"]["PROVEEDORES"]).get_all_records()
        compras_df = conn.worksheet(CONFIG["HOJAS"]["COMPRAS"]).get_all_records()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    # Formulario de compras
    with st.form("form_compras"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha", datetime.today())
            producto = st.selectbox(
                "Producto",
                options=[p["nombre"] for p in productos_df],
                index=0
            )
            unidad = st.selectbox(
                "Unidad",
                options=CONFIG["UNIDADES"],
                index=0
            )
        
        with col2:
            cantidad = st.number_input("Cantidad", min_value=0.0, value=1.0, step=0.1)
            precio_unitario = st.number_input("Precio Unitario", min_value=0.0, value=0.0, step=0.1)
            proveedor = st.selectbox(
                "Proveedor",
                options=[p["nombre"] for p in proveedores_df],
                index=0
            )
            categoria = st.selectbox(
                "Categoría",
                options=CONFIG["CATEGORIAS_COMPRAS"],
                index=0
            )
        
        submitted = st.form_submit_button("Guardar Compra")
        
        if submitted:
            if cantidad <= 0 or precio_unitario <= 0:
                st.error("Cantidad y precio unitario deben ser mayores a cero")
            else:
                nueva_compra = {
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "producto": producto,
                    "unidad": unidad,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "proveedor": proveedor,
                    "categoria": categoria
                }
                
                try:
                    # Agregar a Google Sheets
                    hoja_compras = conn.worksheet(CONFIG["HOJAS"]["COMPRAS"])
                    hoja_compras.append_row(list(nueva_compra.values()))
                    
                    # Registrar en finanzas
                    hoja_finanzas = conn.worksheet(CONFIG["HOJAS"]["FINANZAS"])
                    nueva_finanza = {
                        "tipo": "Gasto",
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "categoria": "compra",
                        "monto": cantidad * precio_unitario,
                        "detalle": f"Compra de {cantidad} {unidad} de {producto} a {proveedor}"
                    }
                    hoja_finanzas.append_row(list(nueva_finanza.values()))
                    
                    st.success("Compra registrada exitosamente!")
                    st.session_state.ultima_compra = nueva_compra
                except Exception as e:
                    st.error(f"Error al guardar la compra: {e}")
    
    # Mostrar última compra registrada
    if 'ultima_compra' in st.session_state:
        st.subheader("Última compra registrada")
        st.json(st.session_state.ultima_compra)
    
    # Mostrar historial de compras
    st.subheader("Historial de Compras")
    if compras_df:
        st.dataframe(pd.DataFrame(compras_df))
    else:
        st.info("No hay compras registradas aún")
