import streamlit as st
from datetime import datetime, timedelta
import json
import os

# --- CONFIGURACIÓN ---
DIAS_PRUEBA = 10
ARCHIVO_CONFIG = "licencia.json"

def verificar_licencia():
    if not os.path.exists(ARCHIVO_CONFIG):
        # Crear fecha de inicio si es la primera vez
        datos = {"fecha_instalacion": datetime.now().isoformat()}
        with open(ARCHIVO_CONFIG, "w") as f:
            json.dump(datos, f)
        return False
    
    with open(ARCHIVO_CONFIG, "r") as f:
        datos = json.load(f)
    
    fecha_instalacion = datetime.fromisoformat(datos["fecha_instalacion"])
    if datetime.now() - fecha_instalacion > timedelta(days=DIAS_PRUEBA):
        return True # Está expirado
    return False

# --- BLOQUEO ---
if verificar_licencia():
    st.set_page_config(page_title="Acceso Restringido", page_icon="🔒")
    
    st.title("🔒 Sistema Bloqueado")
    st.error("El periodo de prueba gratuita ha finalizado.")
    
    st.markdown("""
    ---
    ### ⚠️ Aviso importante
    El acceso a este software ha sido restringido debido a que el tiempo de uso gratuito ha concluido.
    
    Si usted desea **habilitar el software** de forma permanente o extender su licencia, por favor **comuníquese con el desarrollador** a cargo.
    """)
    
    # Botón de contacto
    st.markdown("""
    <div style="text-align: center; margin-top: 30px;">
        <a href="https://wa.me/591XXXXXXXX?text=Hola,%20quisiera%20habilitar%20el%20software%20de%20ventas%20que%20ya%20venció." 
           style="background-color: #007bff; color: white; padding: 15px 30px; 
           text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 18px;">
           📞 Contactar al Desarrollador
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop() # Esto detiene todo el código que sigue

# ==========================================
# AQUÍ COMIENZA TU SISTEMA (SOLO SE VE SI NO ESTÁ BLOQUEADO)
# ==========================================
st.title("🛒 Sistema de Ventas")
st.write("Bienvenido, el sistema está operativo.")
