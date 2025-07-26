import streamlit as st
from datetime import datetime
import pandas as pd
from config import CONFIG

def mostrar(conn):
    st.title("Gestión de Pedidos")
    
    # Obtener datos necesarios
    try:
        pedidos_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["PEDIDOS"]).get_all_records())
        clientes_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["CLIENTES"]).get_all_records())
        productos_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records())
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    # Filtrar solo productos elaborados
    productos_elaborados = [p["nombre"] for p in productos_df if p.get("es_elaborado", "si") == "si"]
    
    # Mostrar pedidos existentes
    st.subheader("Pedidos Registrados")
    if not pedidos_df.empty:
        # Agregar filtros
        estados = st.multiselect(
            "Filtrar por estado",
            options=CONFIG["ESTADOS_PEDIDOS"],
            default=CONFIG["ESTADOS_PEDIDOS"]
        )
        
        pedidos_filtrados = pedidos_df[pedidos_df["estado"].isin(estados)]
        st.dataframe(pedidos_filtrados, use_container_width=True)
        
        # Actualizar estado de pedidos
        st.subheader("Actualizar Estado de Pedido")
        
        pedido_seleccionado = st.selectbox(
            "Seleccionar Pedido",
            options=pedidos_df["producto"] + " - " + pedidos_df["cliente"] + " (" + pedidos_df["fecha"] + ")",
            index=0
        )
        
        nuevo_estado = st.selectbox(
            "Nuevo Estado",
            options=CONFIG["ESTADOS_PEDIDOS"],
            index=0
        )
        
        if st.button("Actualizar Estado"):
            try:
                # Obtener índice del pedido seleccionado
                idx = pedidos_df[
                    (pedidos_df["producto"] + " - " + pedidos_df["cliente"] + " (" + pedidos_df["fecha"] + ")" == pedido_seleccionado)
                ].index[0]
                
                # Actualizar en Google Sheets
                hoja_pedidos = conn.worksheet(CONFIG["HOJAS"]["PEDIDOS"])
                hoja_pedidos.update_cell(idx + 2, 5, nuevo_estado)  # Columna 5 es 'estado'
                
                st.success("Estado del pedido actualizado exitosamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar el pedido: {e}")
    else:
        st.info("No hay pedidos registrados aún")
    
    # Formulario para nuevo pedido
    st.subheader("Nuevo Pedido")
    
    with st.form("form_pedido"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha del Pedido", datetime.today())
            cliente = st.selectbox(
                "Cliente",
                options=[c["nombre"] for c in clientes_df],
                index=0
            )
        
        with col2:
            producto = st.selectbox(
                "Producto Solicitado",
                options=productos_elaborados,
                index=0
            )
            cantidad = st.number_input("Cantidad", min_value=1, value=1, step=1)
        
        submitted = st.form_submit_button("Registrar Pedido")
        
        if submitted:
            nuevo_pedido = {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "cliente": cliente,
                "producto": producto,
                "cantidad": cantidad,
                "estado": "Pendiente"
            }
            
            try:
                # Agregar a Google Sheets
                hoja_pedidos = conn.worksheet(CONFIG["HOJAS"]["PEDIDOS"])
                hoja_pedidos.append_row(list(nuevo_pedido.values()))
                
                st.success("Pedido registrado exitosamente!")
                st.session_state.ultimo_pedido = nuevo_pedido
                st.rerun()
            except Exception as e:
                st.error(f"Error al registrar el pedido: {e}")
    
    # Mostrar último pedido registrado
    if 'ultimo_pedido' in st.session_state:
        st.subheader("Último pedido registrado")
        st.json(st.session_state.ultimo_pedido)
