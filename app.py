import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2 import service_account
from datetime import datetime, timedelta

# Configuración general
CONFIG = {
    "GOOGLE_SHEET_NAME": "Panaderia_Integral_DB",
    "HOJAS": {
        "COMPRAS": "hoja_compras",
        "PRODUCCION": "hoja_produccion",
        "VENTAS": "hoja_ventas",
        "STOCK": "hoja_stock",
        "PEDIDOS": "hoja_pedidos",
        "FINANZAS": "hoja_finanzas",
        "PRODUCTOS": "hoja_productos",
        "PROVEEDORES": "hoja_proveedores",
        "CLIENTES": "hoja_clientes"
    },
    "UNIDADES": ["kg", "litro", "unidad", "paquete", "otro"],
    "CATEGORIAS_COMPRAS": ["ingredientes", "limpieza", "embalaje", "otros"],
    "ESTADOS_VENTAS": ["Entregado", "Pendiente"],
    "ESTADOS_PEDIDOS": ["Pendiente", "En Producción", "Entregado"],
    "TIPOS_FINANZAS": ["Gasto", "Ingreso"],
    "CATEGORIAS_FINANZAS": ["venta", "compra", "servicio", "otros"]
}

# Autenticación
def autenticar():
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.sidebar.title("Inicio de Sesión")
        usuario = st.sidebar.text_input("Usuario")
        contraseña = st.sidebar.text_input("Contraseña", type="password")
        
        if st.sidebar.button("Ingresar"):
            # Validación básica (deberías usar una base de datos)
            if usuario == "admin" and contraseña == "admin123":
                st.session_state.autenticado = True
                st.session_state.rol = "admin"
                st.rerun()
            elif usuario == "panadero" and contraseña == "pan123":
                st.session_state.autenticado = True
                st.session_state.rol = "panadero"
                st.rerun()
            elif usuario == "comprador" and contraseña == "compra123":
                st.session_state.autenticado = True
                st.session_state.rol = "comprador"
                st.rerun()
            else:
                st.sidebar.error("Usuario o contraseña incorrectos")
        return False
    return True

# Conexión a Google Sheets
def conectar_google_sheets():
    try:
        credenciales = {
            "type": st.secrets["gcp"]["type"],
            "project_id": st.secrets["gcp"]["project_id"],
            "private_key_id": st.secrets["gcp"]["private_key_id"],
            "private_key": st.secrets["gcp"]["private_key"],
            "client_email": st.secrets["gcp"]["client_email"],
            "client_id": st.secrets["gcp"]["client_id"],
            "auth_uri": st.secrets["gcp"]["auth_uri"],
            "token_uri": st.secrets["gcp"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp"]["client_x509_cert_url"]
        }
        
        credentials = service_account.Credentials.from_service_account_info(
            credenciales,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        
        gc = gspread.authorize(credentials)
        return gc.open(CONFIG["GOOGLE_SHEET_NAME"])
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

# Funciones de módulos
def modulo_compras(conn):
    st.title("📦 Registro de Compras")
    
    try:
        productos = conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records()
        proveedores = conn.worksheet(CONFIG["HOJAS"]["PROVEEDORES"]).get_all_records()
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return
    
    with st.form("form_compras"):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha = st.date_input("Fecha", datetime.today())
            producto = st.selectbox("Producto", [p["nombre"] for p in productos])
            unidad = st.selectbox("Unidad", CONFIG["UNIDADES"])
        
        with col2:
            cantidad = st.number_input("Cantidad", min_value=0.0, value=1.0, step=0.1)
            precio = st.number_input("Precio Unitario", min_value=0.0, value=0.0, step=0.1)
            proveedor = st.selectbox("Proveedor", [p["nombre"] for p in proveedores])
            categoria = st.selectbox("Categoría", CONFIG["CATEGORIAS_COMPRAS"])
        
        if st.form_submit_button("Guardar Compra"):
            if cantidad > 0 and precio > 0:
                try:
                    nueva_compra = [
                        fecha.strftime("%Y-%m-%d"),
                        producto,
                        unidad,
                        cantidad,
                        precio,
                        proveedor,
                        categoria
                    ]
                    
                    conn.worksheet(CONFIG["HOJAS"]["COMPRAS"]).append_row(nueva_compra)
                    st.success("¡Compra registrada!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.error("Cantidad y precio deben ser mayores a cero")

def modulo_produccion(conn):
    st.title("🍞 Registro de Producción")
    
    try:
        productos = conn.worksheet(CONFIG["HOJAS"]["PRODUCTOS"]).get_all_records()
    except Exception as e:
        st.error(f"Error al cargar productos: {e}")
        return
    
    productos_elaborados = [p["nombre"] for p in productos if p.get("es_elaborado", "si") == "si"]
    
    with st.form("form_produccion"):
        fecha = st.date_input("Fecha", datetime.today())
        producto = st.selectbox("Producto Elaborado", productos_elaborados)
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
        
        if st.form_submit_button("Registrar Producción"):
            try:
                nueva_produccion = [
                    fecha.strftime("%Y-%m-%d"),
                    producto,
                    cantidad
                ]
                
                conn.worksheet(CONFIG["HOJAS"]["PRODUCCION"]).append_row(nueva_produccion)
                st.success("¡Producción registrada!")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# (Continúa con los demás módulos de la misma forma...)

# Interfaz principal
def main():
    st.set_page_config(page_title="Panadería Integral", page_icon="🍞", layout="wide")
    
    if not autenticar():
        return
    
    conn = conectar_google_sheets()
    
    st.sidebar.title("Panadería Integral")
    rol = st.session_state.get('rol', 'invitado')
    st.sidebar.write(f"Rol: {rol.capitalize()}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    opciones = []
    if rol in ['admin', 'comprador']: opciones.append("Compras")
    if rol in ['admin', 'panadero']: opciones.append("Producción")
    if rol == 'admin': opciones.extend(["Ventas", "Stock", "Análisis", "Pedidos", "Finanzas"])
    
    modulo = st.sidebar.radio("Menú", opciones)
    
    if modulo == "Compras":
        modulo_compras(conn)
    elif modulo == "Producción":
        modulo_produccion(conn)
    # (Agregar los demás módulos aquí...)

if __name__ == "__main__":
    main()
