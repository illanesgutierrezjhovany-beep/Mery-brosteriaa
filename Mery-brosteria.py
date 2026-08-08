from datetime import datetime, timedelta
import json
import os
import streamlit as st

# --- CONFIGURACIÓN ---
DIAS_PRUEBA = 10
ARCHIVO_CONFIG = "licencia.json"


def verificar_licencia():
  if not os.path.exists(ARCHIVO_CONFIG):
    datos = {"fecha_instalacion": datetime.now().isoformat()}
    with open(ARCHIVO_CONFIG, "w") as f:
      json.dump(datos, f)
    return False

  with open(ARCHIVO_CONFIG, "r") as f:
    datos = json.load(f)

  fecha_instalacion = datetime.fromisoformat(datos["fecha_instalacion"])
  if datetime.now() - fecha_instalacion > timedelta(days=DIAS_PRUEBA):
    return True
  return False


# --- BLOQUEO ---
if verificar_licencia():
  st.set_page_config(page_title="Sistema Bloqueado", page_icon="🔒")

  st.error(
      "El sistema de uso gratuito finalizó. Por favor contactarse con el"
      " desarrollador."
  )

  whatsapp_url = (
      "https://wa.me/591XXXXXXXX?text=Hola,%20el%20sistema%20de%20uso%20gratuito"
      "%20finalizó,%20necesito%20contactarme%20para%20habilitarlo."
  )
  st.markdown(
      f"""
    <div style="text-align: center; margin-top: 40px;">
        <a href="{whatsapp_url}" target="_blank" 
           style="background-color: #25D366; color: white; padding: 15px 30px; 
           text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 18px;">
           💬 Contactarse con el desarrollador
        </a>
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.stop()

# ==========================================
# AQUÍ VA TU SISTEMA DE VENTAS NORMAL
# ==========================================
st.title("🛒 Sistema de Ventas")
st.write("Bienvenido, el sistema está operativo.")
