import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import pytz
import io

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Ventas - Brostería Doña Mery",
    page_icon="🍗",
    layout="wide"
)

# Zona horaria exacta de Bolivia
bolivia_tz = pytz.timezone('America/La_Paz')

# Inicializar Base de Datos SQLite (Persistente 100%)
def init_db():
    conn = sqlite3.connect('ventas_pollo.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente TEXT,
            producto TEXT,
            precio REAL,
            cantidad INTEGER,
            total REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Funciones de base de datos
def registrar_venta_db(cliente, producto, precio, cantidad):
    conn = sqlite3.connect('ventas_pollo.db', check_same_thread=False)
    cursor = conn.cursor()
    fecha = datetime.now(bolivia_tz).strftime("%Y-%m-%d %H:%M:%S")
    total = precio * cantidad
    cursor.execute("INSERT INTO ventas (fecha, cliente, producto, precio, cantidad, total) VALUES (?, ?, ?, ?, ?, ?)",
                   (fecha, cliente, producto, precio, cantidad, total))
    conn.commit()
    conn.close()

def obtener_ventas():
    conn = sqlite3.connect('ventas_pollo.db', check_same_thread=False)
    df = pd.read_sql("SELECT * FROM ventas", conn)
    conn.close()
    return df

def eliminar_venta_db(id_venta):
    conn = sqlite3.connect('ventas_pollo.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas WHERE id = ?", (id_venta,))
    conn.commit()
    conn.close()

def reiniciar_ventas_db():
    conn = sqlite3.connect('ventas_pollo.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ventas")
    conn.commit()
    conn.close()

# Menú oficial con alitas separadas y precios en Bs
MENU_ITEMS = {
    "Alitas BBQ": 18.0,
    "Alitas Miel Mostaza": 18.0,
    "Alitas Picante": 18.0,
    "Pollo a la broster": 15.0,
    "Pollo al spiedo": 15.0,
    "Pollo escolar": 13.0,
    "Gaseosas": 6.0,
    "Mini": 2.50,
    "Refresco en vaso": 2.50,
    "Jugo del valle": 15.0
}

# Estilos CSS personalizados para el ticket y la interfaz
st.markdown('''
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #ff4b4b;
        color: white;
    }
    .stButton>button:hover {
        background-color: #e03e3e;
        color: white;
    }
    .ticket-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border: 2px dashed #ff4b4b;
        font-family: monospace;
        margin-top: 20px;
        color: #000000;
    }
    </style>
''', unsafe_allow_html=True)

# Título Principal
st.title("🍗 Brostería Doña Mery - Sistema de Ventas y Tickets")
st.markdown("---")

# Barra Lateral (Navegación)
menu_opcion = st.sidebar.selectbox(
    "Menú de Navegación",
    ["🛒 Registrar Venta y Tickets", "📊 Dashboard y KPIs", "📋 Historial y Administración", "📥 Descargar Excel"]
)

df_ventas = obtener_ventas()

# ----------------------------------------------------
# 1. REGISTRAR VENTA Y TICKETS
# ----------------------------------------------------
if menu_opcion == "🛒 Registrar Venta y Tickets":
    st.header("🛒 Registrar Nueva Venta")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("Nombre del Cliente", placeholder="Ej. Carlos o Maldonado")
        producto_seleccionado = st.selectbox("Seleccione el Plato o Bebida", list(MENU_ITEMS.keys()))
        precio_unitario = MENU_ITEMS[producto_seleccionado]
        st.info(f"Precio Unitario: **{precio_unitario:.2f} Bs**")
    
    with col2:
        cantidad = st.number_input("Cantidad", min_value=1, max_value=100, value=1, step=1)
        total_pagar = precio_unitario * cantidad
        st.success(f"Total a Pagar: **{total_pagar:.2f} Bs**")
    
    if st.button("🚀 Registrar Venta y Emitir Ticket"):
        if not cliente.strip():
            st.error("⚠️ Por favor ingrese el nombre del cliente.")
        else:
            registrar_venta_db(cliente.strip(), producto_seleccionado, precio_unitario, cantidad)
            df_actualizado = obtener_ventas()
            ultimo_id = df_actualizado.iloc[-1]['id'] if not df_actualizado.empty else 1
            fecha_actual = datetime.now(bolivia_tz).strftime("%Y-%m-%d %H:%M:%S")
            
            st.success(f"¡Venta registrada con éxito! Ticket #{ultimo_id} generado.")
            
            # Mostrar Ticket Bonito en Pantalla
            st.markdown(f"""
            <div class="ticket-box">
                <h3 style="text-align: center; color: #ff4b4b; margin: 0;">BROSTERÍA DOÑA MERY</h3>
                <p style="text-align: center; margin: 2px 0; font-size: 0.85em; color: #555;">¡El mejor sabor tradicional!</p>
                <p style="text-align: center; margin: 5px 0;">------------------------------------------------</p>
                <p><b>Ticket N°:</b> {ultimo_id}</p>
                <p><b>Fecha y Hora:</b> {fecha_actual}</p>
                <p><b>Cliente:</b> {cliente.strip().upper()}</p>
                <p><b>Producto:</b> {producto_seleccionado} (x{cantidad})</p>
                <p style="font-size: 1.2em; color: #333;"><b>Total Pagado: {total_pagar:.2f} Bs</b></p>
                <p style="text-align: center; margin: 5px 0;">------------------------------------------------</p>
                <p style="text-align: center; color: #666; font-size: 0.9em;">¡Gracias por su preferencia, vuelva pronto!</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 **Tip para imprimir:** Presiona `Ctrl + P` (en computadora) o usa el menú de compartir de tu celular para imprimir este ticket en tu impresora térmica.")

# ----------------------------------------------------
# 2. DASHBOARD Y KPIS
# ----------------------------------------------------
elif menu_opcion == "📊 Dashboard y KPIs":
    st.header("📊 Dashboard General - Brostería Doña Mery")
    
    if df_ventas.empty:
        st.warning("⚠️ Todavía no hay ventas registradas para mostrar métricas.")
    else:
        df_ventas['total'] = pd.to_numeric(df_ventas['total'], errors='coerce')
        total_ingresos = df_ventas['total'].sum()
        total_ventas_realizadas = len(df_ventas)
        plato_favorito = df_ventas['producto'].mode()[0] if not df_ventas.empty else "N/A"
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("💰 Ingresos Totales", f"{total_ingresos:.2f} Bs")
        kpi2.metric("🧾 Tickets Emitidos", f"{total_ventas_realizadas}")
        kpi3.metric("🏆 Producto Más Vendido", f"{plato_favorito}")
        
        st.markdown("---")
        st.subheader("📈 Ventas Totales por Producto (Bs)")
        
        ventas_por_producto = df_ventas.groupby('producto')['total'].sum().reset_index()
        ventas_por_producto['total'] = ventas_por_producto['total'].round(2)
        
        st.bar_chart(ventas_por_producto.set_index('producto')['total'])

# ----------------------------------------------------
# 3. HISTORIAL Y ADMINISTRACIÓN (ELIMINAR POR ID / REINICIAR)
# ----------------------------------------------------
elif menu_opcion == "📋 Historial y Administración":
    st.header("📋 Historial Completo y Gestión de Tickets")
    
    if df_ventas.empty:
        st.warning("⚠️ No hay registros en la base de datos.")
    else:
        st.dataframe(df_ventas, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚙️ Panel de Control y Seguridad")
        
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            st.markdown("#### ❌ Eliminar Venta por ID")
            id_a_borrar = st.number_input("Ingrese el ID del Ticket a eliminar", min_value=1, step=1, value=1)
            if st.button("Eliminar Ticket Específico"):
                if id_a_borrar in df_ventas['id'].values:
                    eliminar_venta_db(id_a_borrar)
                    st.success(f"✅ Ticket #{id_a_borrar} eliminado correctamente.")
                    st.rerun()
                else:
                    st.error("❌ El ID ingresado no existe.")
                    
        with col_del2:
            st.markdown("#### ⚠️ Zona de Peligro (Reinicio Total)")
            st.warning("Esto borrará todo el historial acumulado permanentemente.")
            if st.button("🚨 Reiniciar Todas las Ventas"):
                reiniciar_ventas_db()
                st.success("✅ Se han reiniciado todas las ventas del sistema.")
                st.rerun()

# ----------------------------------------------------
# 4. DESCARGAR EXCEL
# ----------------------------------------------------
elif menu_opcion == "📥 Descargar Excel":
    st.header("📥 Descargar Reporte de Ventas en Excel")
    
    if df_ventas.empty:
        st.warning("⚠️ No hay datos para exportar.")
    else:
        st.markdown("Haz clic en el botón de abajo para descargar tu reporte completo con todas las ventas registradas.")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_ventas.to_excel(writer, index=False, sheet_name='Ventas_DonaMery')
        excel_data = output.getvalue()
        
        st.download_button(
            label="📊 Descargar Reporte en Excel (.xlsx)",
            data=excel_data,
            file_name=f"ventas_dona_mery_{datetime.now(bolivia_tz).strftime('%Y-%m-%d_%H-%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
