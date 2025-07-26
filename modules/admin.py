import streamlit as st
import pandas as pd
from config import CONFIG

def mostrar(conn):
    st.title("Administración del Sistema")
    
    # Pestañas para diferentes funciones administrativas
    tab1, tab2, tab3 = st.tabs(["Productos", "Proveedores", "Clientes"])
    
    with tab1:
        gestionar_productos(conn)
    
    with tab2:
        gestionar_proveedores(conn)
    
    with tab3:
        gestionar_clientes(conn)

def gestionar_productos(conn):
    st.header("Gestión de Productos")
    
    try:
        productos_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records())
    except Exception as e:
        st.error(f"Error al cargar productos: {e}")
        return
    
    # Mostrar productos existentes
    st.subheader("Productos Registrados")
    if not productos_df.empty:
        st.dataframe(productos_df, use_container_width=True)
    else:
        st.info("No hay productos registrados aún")
    
    # Formulario para agregar/editar producto
    st.subheader("Agregar/Editar Producto")
    
    with st.form("form_producto"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del Producto")
            es_elaborado = st.selectbox(
                "Tipo de Producto",
                options=["Materia Prima", "Producto Elaborado"],
                index=1
            )
            unidad = st.selectbox(
                "Unidad de Medida",
                options=CONFIG["UNIDADES"],
                index=0
            )
        
        with col2:
            stock_minimo = st.number_input("Stock Mínimo Recomendado", min_value=0, value=1)
            precio_sugerido = st.number_input("Precio Sugerido", min_value=0.0, value=0.0, step=0.1)
            descripcion = st.text_area("Descripción")
        
        submitted = st.form_submit_button("Guardar Producto")
        
        if submitted:
            if not nombre:
                st.error("El nombre del producto es obligatorio")
            else:
                nuevo_producto = {
                    "nombre": nombre,
                    "es_elaborado": "si" if es_elaborado == "Producto Elaborado" else "no",
                    "unidad": unidad,
                    "stock_minimo": stock_minimo,
                    "precio_sugerido": precio_sugerido,
                    "descripcion": descripcion
                }
                
                try:
                    hoja_productos = conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"])
                    
                    # Verificar si el producto ya existe
                    if nombre in productos_df["nombre"].values:
                        # Actualizar producto existente
                        idx = productos_df[productos_df["nombre"] == nombre].index[0]
                        for i, (key, value) in enumerate(nuevo_producto.items(), start=1):
                            hoja_productos.update_cell(idx + 2, i, value)
                        st.success("Producto actualizado exitosamente!")
                    else:
                        # Agregar nuevo producto
                        hoja_productos.append_row(list(nuevo_producto.values()))
                        st.success("Producto agregado exitosamente!")
                except Exception as e:
                    st.error(f"Error al guardar el producto: {e}")

def gestionar_proveedores(conn):
    st.header("Gestión de Proveedores")
    
    try:
        proveedores_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["PROVEEDORES"]).get_all_records())
    except Exception as e:
        st.error(f"Error al cargar proveedores: {e}")
        return
    
    # Mostrar proveedores existentes
    st.subheader("Proveedores Registrados")
    if not proveedores_df.empty:
        st.dataframe(proveedores_df, use_container_width=True)
    else:
        st.info("No hay proveedores registrados aún")
    
    # Formulario para agregar/editar proveedor
    st.subheader("Agregar/Editar Proveedor")
    
    with st.form("form_proveedor"):
        nombre = st.text_input("Nombre del Proveedor")
        contacto = st.text_input("Contacto (teléfono/email)")
        productos = st.text_area("Productos que provee")
        direccion = st.text_input("Dirección")
        notas = st.text_area("Notas adicionales")
        
        submitted = st.form_submit_button("Guardar Proveedor")
        
        if submitted:
            if not nombre:
                st.error("El nombre del proveedor es obligatorio")
            else:
                nuevo_proveedor = {
                    "nombre": nombre,
                    "contacto": contacto,
                    "productos": productos,
                    "direccion": direccion,
                    "notas": notas
                }
                
                try:
                    hoja_proveedores = conn.worksheet(CONFIG["HOJAS"]["PROVEEDORES"])
                    
                    # Verificar si el proveedor ya existe
                    if not proveedores_df.empty and nombre in proveedores_df["nombre"].values:
                        # Actualizar proveedor existente
                        idx = proveedores_df[proveedores_df["nombre"] == nombre].index[0]
                        for i, (key, value) in enumerate(nuevo_proveedor.items(), start=1):
                            hoja_proveedores.update_cell(idx + 2, i, value)
                        st.success("Proveedor actualizado exitosamente!")
                    else:
                        # Agregar nuevo proveedor
                        hoja_proveedores.append_row(list(nuevo_proveedor.values()))
                        st.success("Proveedor agregado exitosamente!")
                except Exception as e:
                    st.error(f"Error al guardar el proveedor: {e}")

def gestionar_clientes(conn):
    st.header("Gestión de Clientes")
    
    try:
        clientes_df = pd.DataFrame(conn.worksheet(CONFIG["HOJAS"]["CLIENTES"]).get_all_records())
    except Exception as e:
        st.error(f"Error al cargar clientes: {e}")
        return
    
    # Mostrar clientes existentes
    st.subheader("Clientes Registrados")
    if not clientes_df.empty:
        st.dataframe(clientes_df, use_container_width=True)
    else:
        st.info("No hay clientes registrados aún")
    
    # Formulario para agregar/editar cliente
    st.subheader("Agregar/Editar Cliente")
    
    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del Cliente")
            contacto = st.text_input("Contacto (teléfono/email)")
        
        with col2:
            frecuencia = st.selectbox(
                "Frecuencia de Compra",
                options=["Ocasional", "Semanal", "Quincenal", "Mensual", "Frecuente"],
                index=0
            )
            preferencias = st.text_area("Preferencias de Productos")
        
        submitted = st.form_submit_button("Guardar Cliente")
        
        if submitted:
            if not nombre:
                st.error("El nombre del cliente es obligatorio")
            else:
                nuevo_cliente = {
                    "nombre": nombre,
                    "contacto": contacto,
                    "frecuencia": frecuencia,
                    "preferencias": preferencias
                }
                
                try:
                    hoja_clientes = conn.worksheet(CONFIG["HOJAS"]["CLIENTES"])
                    
                    # Verificar si el cliente ya existe
                    if not clientes_df.empty and nombre in clientes_df["nombre"].values:
                        # Actualizar cliente existente
                        idx = clientes_df[clientes_df["nombre"] == nombre].index[0]
                        for i, (key, value) in enumerate(nuevo_cliente.items(), start=1):
                            hoja_clientes.update_cell(idx + 2, i, value)
                        st.success("Cliente actualizado exitosamente!")
                    else:
                        # Agregar nuevo cliente
                        hoja_clientes.append_row(list(nuevo_cliente.values()))
                        st.success("Cliente agregado exitosamente!")
                except Exception as e:
                    st.error(f"Error al guardar el cliente: {e}")
