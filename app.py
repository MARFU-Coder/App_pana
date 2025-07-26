import streamlit as st
from modules import compras, produccion, ventas, stock, analisis, admin, pedidos, finanzas
from sheets.sheets_api import conectar_google_sheets

# Configuración de la página
st.set_page_config(
    page_title="Panadería Integral",
    page_icon="🍞",
    layout="wide"
)

# Autenticación básica (simplificada para el ejemplo)
def autenticar():
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.sidebar.title("Inicio de Sesión")
        usuario = st.sidebar.text_input("Usuario")
        contraseña = st.sidebar.text_input("Contraseña", type="password")
        
        if st.sidebar.button("Ingresar"):
            # Aquí deberías validar contra una base de datos o lista de usuarios
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
try:
    conn = conectar_google_sheets()
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# Interfaz principal
if autenticar():
    st.sidebar.title("Panadería Integral")
    st.sidebar.image("https://via.placeholder.com/150x50?text=Logo+Panaderia", width=150)
    
    # Menú según rol
    rol = st.session_state.get('rol', 'invitado')
    st.sidebar.write(f"Rol: {rol.capitalize()}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    opciones_menu = []
    
    if rol in ['admin', 'comprador']:
        opciones_menu.append("Compras")
    if rol in ['admin', 'panadero']:
        opciones_menu.append("Producción")
    if rol in ['admin']:
        opciones_menu.append("Ventas")
    if rol in ['admin', 'panadero', 'comprador']:
        opciones_menu.append("Stock")
    if rol in ['admin']:
        opciones_menu.append("Análisis")
        opciones_menu.append("Administración")
        opciones_menu.append("Pedidos")
        opciones_menu.append("Finanzas")
    
    seleccion = st.sidebar.radio("Menú", opciones_menu)
    
    # Mostrar módulo seleccionado
    if seleccion == "Compras":
        compras.mostrar(conn)
    elif seleccion == "Producción":
        produccion.mostrar(conn)
    elif seleccion == "Ventas":
        ventas.mostrar(conn)
    elif seleccion == "Stock":
        stock.mostrar(conn)
    elif seleccion == "Análisis":
        analisis.mostrar(conn)
    elif seleccion == "Administración":
        admin.mostrar(conn)
    elif seleccion == "Pedidos":
        pedidos.mostrar(conn)
    elif seleccion == "Finanzas":
        finanzas.mostrar(conn)
