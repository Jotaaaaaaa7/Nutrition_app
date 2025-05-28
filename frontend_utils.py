import requests
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
from typing import List, Optional


# Configuración de la API
API_URL = "http://127.0.0.1:8000"

# Funciones de comunicación con la API
@st.cache_data(ttl=60)
def fetch_data(endpoint):
    """Función para obtener datos desde la API con caché"""
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en la API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def post_data(endpoint, data):
    """Enviar datos a la API (POST)"""
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Error al crear: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def update_data(endpoint, data):
    """Actualizar datos en la API (PUT)"""
    try:
        response = requests.put(f"{API_URL}{endpoint}", json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error al actualizar: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def delete_data(endpoint):
    """Eliminar datos de la API (DELETE)"""
    try:
        response = requests.delete(f"{API_URL}{endpoint}")
        if response.status_code in [200, 204]:
            return True
        else:
            st.error(f"Error al eliminar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return False


def clear_caches():
    """Limpiar todas las cachés después de cambios"""
    fetch_data.clear()
