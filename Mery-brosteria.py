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
    return True  # Está expirado
  return False


# --- BLOQUEO ---
if verificar_licencia():
  st.set_page_config(page_title="Prueba Finalizada", page_icon="🔒")

  st.title("🔒 Prueba gratuita finalizada")
  st.error("El tiempo de uso gratuito de este software ha concluido.")

  st.markdown("""
    ---
    ### ⚠️ Aviso importante
    Si desea habilitar el software, por favor **comuníquese con el desarrollador** para activar su licencia.
    """)

  # Cambia el número por el tuyo en formato internacional
  whatsapp_url = (
      "https://wa.me/591XXXXXXXX?text=Hola,%20necesito%20habilitar%20el%20software"
      "porque%20la%20prueba%20gratuita%20finalizó."
  )
  st.markdown(
      f"""
    <div style="text-align: center; margin-top: 30px;">
        <a href="{whatsapp_url}" target="_blank" 
           style="background-color: #25D366; color: white; padding: 15px 30px; 
           text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 18px;">
           💬 Comuníquese con el desarrollador
        </a>
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.stop()  # Detiene la ejecución para que no se vea el sistema

# ==========================================
# AQUÍ COMIENZA TU SISTEMA DE VENTAS
# ==========================================
st.title("🛒 Sistema de Ventas")
st.write("Bienvenido, el sistema está operativo.")
