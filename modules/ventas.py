import streamlit as st
from datetime import datetime
import pandas as pd
from config import CONFIG

def mostrar(conn):
    st.title("Registro de Ventas")
    
    # Obtener datos necesarios
    try:
        productos_df = conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records()
        clientes_df = conn.worksheet(CONFIG["HOJAS"]["CLIENTES"]).get_all_records()
        ventas_df = conn.worksheet(CONFIG["HOJAS"]["VENTAS"]).get_all_records()
        stock_df = conn.worksheet(CONFIG["HOJAS"]["STOCK"]).get_all_records()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    # Filtrar solo productos elaborados con stock
    productos_elaborados = [p["nombre"] for p in productos_df if p.get("es_elaborado", "si") == "si"]
    stock_disponible = {row["producto"]: int(row["stock_actual"]) for row in stock_df if row["producto"] in productos_elaborados}
    
    # Formulario de ventas
    with st.form("form_ventas"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha", datetime.today())
            producto = st.selectbox(
                "Producto Vendido",
                options=[p for p in productos_elaborados if stock_disponible.get(p, 0) > 0],
                index=0
            )
            cliente = st.selectbox(
                "Cliente",
                options=[c["nombre"] for c in clientes_df],
                index=0
            )
        
        with col2:
            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                max_value=stock_disponible.get(producto, 1),
                value=1,
                step=1
            )
            precio = st.number_input("Precio", min_value=0.0, value=0.0, step=0.1)
            estado = st.selectbox(
                "Estado",
                options=CONFIG["ESTADOS_VENTAS"],
                index=0
            )
        
        submitted = st.form_submit_button("Guardar Venta")
        
        if submitted:
            if cantidad <= 0 or precio <= 0:
                st.error("Cantidad y precio deben ser mayores a cero")
            else:
                nueva_venta = {
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "producto": producto,
                    "cantidad": cantidad,
                    "precio": precio,
                    "cliente": cliente,
                    "estado": estado
                }
                
                try:
                    # Agregar a Google Sheets
                    hoja_ventas = conn.worksheet(CONFIG["HOJAS"]["VENTAS"])
                    hoja_ventas.append_row(list(nueva_venta.values()))
                    
                    # Actualizar stock
                    actualizar_stock(conn, producto, -cantidad)
                    
                    # Registrar en finanzas
                    hoja_finanzas = conn.worksheet(CONFIG["HOJAS"]["FINANZAS"])
                    nueva_finanza = {
                        "tipo": "Ingreso",
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "categoria": "venta",
                        "monto": cantidad * precio,
                        "detalle": f"Venta de {cantidad} {producto} a {cliente}"
                    }
                    hoja_finanzas.append_row(list(nueva_finanza.values()))
                    
                    st.success("Venta registrada exitosamente!")
                    st.session_state.ultima_venta = nueva_venta
                except Exception as e:
                    st.error(f"Error al guardar la venta: {e}")
    
    # Mostrar última venta registrada
    if 'ultima_venta' in st.session_state:
        st.subheader("Última venta registrada")
        st.json(st.session_state.ultima_venta)
    
    # Mostrar historial de ventas
    st.subheader("Historial de Ventas")
    if ventas_df:
        st.dataframe(pd.DataFrame(ventas_df))
    else:
        st.info("No hay ventas registradas aún")

def actualizar_stock(conn, producto, cantidad):
    """Actualiza el stock del producto"""
    try:
        hoja_stock = conn.worksheet(CONFIG["HOJAS"]["STOCK"])
        stock_df = pd.DataFrame(hoja_stock.get_all_records())
        
        if producto in stock_df["producto"].values:
            idx = stock_df[stock_df["producto"] == producto].index[0]
            stock_actual = int(stock_df.at[idx, "stock_actual"])
            nuevo_stock = stock_actual + cantidad
            
            hoja_stock.update_cell(idx + 2, 2, nuevo_stock)  # +2 porque 1 es header y pandas index desde 0
    except Exception as e:
        raise Exception(f"Error al actualizar stock: {e}")
