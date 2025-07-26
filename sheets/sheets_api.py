import gspread
from google.oauth2 import service_account
import streamlit as st
from config import CONFIG
import pandas as pd

def conectar_google_sheets():
    """
    Establece la conexión con Google Sheets utilizando las credenciales de secrets.toml
    
    Returns:
        gspread.client.Client: Cliente autorizado de Google Sheets
    """
    try:
        # Cargar credenciales desde secrets.toml
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
        
        # Crear credenciales de servicio
        credentials = service_account.Credentials.from_service_account_info(
            credenciales,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        
        # Conectar con Google Sheets
        gc = gspread.authorize(credentials)
        
        # Verificar que la hoja de cálculo existe
        try:
            spreadsheet = gc.open(CONFIG["GOOGLE_SHEET_NAME"])
            return spreadsheet
        except gspread.SpreadsheetNotFound:
            st.error(f"No se encontró la hoja de cálculo: {CONFIG['GOOGLE_SHEET_NAME']}")
            st.stop()
        except Exception as e:
            st.error(f"Error al acceder a la hoja de cálculo: {e}")
            st.stop()
    
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        st.stop()

def obtener_datos(conn, hoja_nombre):
    """
    Obtiene todos los registros de una hoja específica como lista de diccionarios
    
    Args:
        conn: Conexión a Google Sheets
        hoja_nombre (str): Nombre de la hoja a leer
        
    Returns:
        list: Lista de diccionarios con los datos de la hoja
    """
    try:
        worksheet = conn.worksheet(hoja_nombre)
        return worksheet.get_all_records()
    except Exception as e:
        st.error(f"Error al leer datos de {hoja_nombre}: {e}")
        return []

def guardar_datos(conn, hoja_nombre, datos):
    """
    Guarda datos en una hoja específica de Google Sheets
    
    Args:
        conn: Conexión a Google Sheets
        hoja_nombre (str): Nombre de la hoja a escribir
        datos (list): Lista de diccionarios con los datos a guardar
    """
    try:
        worksheet = conn.worksheet(hoja_nombre)
        
        # Limpiar hoja existente (excepto encabezados)
        if len(worksheet.get_all_values()) > 1:
            worksheet.delete_rows(2, len(worksheet.get_all_values()))
        
        # Agregar nuevos datos
        if datos:
            # Convertir lista de diccionarios a lista de listas
            valores = [list(datos[0].keys())]  # Encabezados
            valores.extend([list(d.values()) for d in datos])
            
            worksheet.update(values=valores)
    except Exception as e:
        st.error(f"Error al guardar datos en {hoja_nombre}: {e}")
        raise
