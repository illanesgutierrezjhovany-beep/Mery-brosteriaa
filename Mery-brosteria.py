
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
def registrar_venta_db(producto, precio, cantidad):
    conn = sqlite3.connect('ventas_pollo.db', check_same_thread=False)
    cursor = conn.cursor()
    fecha = datetime.now(bolivia_tz).strftime("%Y-%m-%d %H:%M:%S")
    total = precio * cantidad
    cursor.execute("INSERT INTO ventas (fecha, producto, precio, cantidad, total) VALUES (?, ?, ?, ?, ?)",
                   (fecha, producto, precio, cantidad, total))
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

# Estilos CSS personalizados
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
    </style>
''', unsafe_allow_html=True)

# Título Principal
st.title("🍗 Brostería Doña Mery - Sistema de Ventas")
st.markdown("---")

# Barra Lateral (Navegación)
menu_opcion = st.sidebar.selectbox(
    "Menú de Navegación",
    ["🛒 Registrar Venta", "📊 Dashboard y KPIs", "📋 Historial y Administración", "📥 Descargar Excel Profesional"]
)

df_ventas = obtener_ventas()

# ----------------------------------------------------
# 1. REGISTRAR VENTA DIRECTA
# ----------------------------------------------------
if menu_opcion == "🛒 Registrar Venta":
    st.header("🛒 Registrar Nueva Venta")
    
    col1, col2 = st.columns(2)
    
    with col1:
        producto_seleccionado = st.selectbox("Seleccione el Plato o Bebida", list(MENU_ITEMS.keys()))
        precio_unitario = MENU_ITEMS[producto_seleccionado]
        st.info(f"Precio Unitario: **{precio_unitario:.2f} Bs**")
    
    with col2:
        cantidad = st.number_input("Cantidad", min_value=1, max_value=100, value=1, step=1)
        total_pagar = precio_unitario * cantidad
        st.success(f"Total a Pagar: **{total_pagar:.2f} Bs**")
    
    if st.button("🚀 Registrar Venta"):
        registrar_venta_db(producto_seleccionado, precio_unitario, cantidad)
        st.success(f"✅ ¡Venta registrada con éxito! (**{producto_seleccionado}** x{cantidad} = **{total_pagar:.2f} Bs**)")

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
        kpi2.metric("🧾 Ventas Registradas", f"{total_ventas_realizadas}")
        kpi3.metric("🏆 Producto Más Vendido", f"{plato_favorito}")
        
        st.markdown("---")
        st.subheader("📈 Resumen de Ventas por Producto (Bs)")
        
        ventas_por_producto = df_ventas.groupby('producto')['total'].sum().reset_index()
        ventas_por_producto['total'] = ventas_por_producto['total'].round(2)
        ventas_por_producto = ventas_por_producto.sort_values(by='total', ascending=False)
        
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            st.bar_chart(ventas_por_producto.set_index('producto')['total'], use_container_width=True)
        with col_g2:
            st.markdown("**Totales por ítem:**")
            st.dataframe(ventas_por_producto.set_index('producto'), use_container_width=True)

# ----------------------------------------------------
# 3. HISTORIAL Y ADMINISTRACIÓN
# ----------------------------------------------------
elif menu_opcion == "📋 Historial y Administración":
    st.header("📋 Historial Completo y Gestión de Ventas")
    
    if df_ventas.empty:
        st.warning("⚠️ No hay registros en la base de datos.")
    else:
        st.dataframe(df_ventas, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚙️ Panel de Control y Seguridad")
        
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            st.markdown("#### ❌ Eliminar Venta por ID")
            id_a_borrar = st.number_input("Ingrese el ID de la venta a eliminar", min_value=1, step=1, value=1)
            if st.button("Eliminar Venta Específica"):
                if id_a_borrar in df_ventas['id'].values:
                    eliminar_venta_db(id_a_borrar)
                    st.success(f"✅ Venta con ID #{id_a_borrar} eliminada correctamente.")
                    st.rerun()
                else:
                    st.error("❌ El ID ingresado no existe.")
                    
        with col_del2:
            st.markdown("#### ⚠️ Zona de Cierre de Día (Reinicio)")
            st.warning("Usa esta opción al finalizar el día para limpiar las ventas si lo deseas.")
            if st.button("🚨 Reiniciar Todas las Ventas del Día"):
                reiniciar_ventas_db()
                st.success("✅ Se han reiniciado todas las ventas correctamente.")
                st.rerun()

# ----------------------------------------------------
# 4. DESCARGAR EXCEL PROFESIONAL (Con Tablas Resumen y Gráfico Integrado)
# ----------------------------------------------------
elif menu_opcion == "📥 Descargar Excel Profesional":
    st.header("📥 Descargar Reporte de Ventas Avanzado en Excel")
    
    if df_ventas.empty:
        st.warning("⚠️ No hay datos para exportar.")
    else:
        st.markdown("Este reporte genera un archivo de Excel profesional estructurado con el detalle de ventas, la tabla resumen por producto y los ingresos totales del día listos para la administración.")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 1. Hoja principal de detalle de ventas
            df_ventas.to_excel(writer, index=False, sheet_name='Detalle_Ventas')
            
            # 2. Tabla resumen por producto con ingresos totales
            resumen_prod = df_ventas.groupby('producto').agg(
                Cantidad_Total=('cantidad', 'sum'),
                Ingresos_Totales=('total', 'sum')
            ).reset_index()
            resumen_prod['Ingresos_Totales'] = resumen_prod['Ingresos_Totales'].round(2)
            resumen_prod.to_excel(writer, index=False, sheet_name='Resumen_Por_Producto')
            
            # Obtener workbook para insertar el gráfico nativo de Excel y formato profesional
            workbook = writer.book
            
            # Crear una hoja de resumen ejecutivo con los ingresos totales del día
            ws_resumen = workbook.create_sheet(title="Cierre_Total")
            ws_resumen.append(["BROSTERÍA DOÑA MERY - CIERRE DE INGRESOS"])
            ws_resumen.append([])
            ws_resumen.append(["Concepto", "Monto Total (Bs)"])
            total_dia = df_ventas['total'].sum()
            ws_resumen.append(["Ingresos Totales del Día", round(total_dia, 2)])
            ws_resumen.append(["Total Tickets / Ventas", len(df_ventas)])

            # Agregar un gráfico de barras integrado directamente en Excel
            from openpyxl.chart import BarChart, Reference
            chart = BarChart()
            chart.type = "col"
            chart.style = 10
            chart.title = "Ingresos Totales por Producto (Bs)"
            chart.y_axis.title = "Bolivianos (Bs)"
            chart.x_axis.title = "Productos"

            # Referencias para el gráfico basadas en la hoja 'Resumen_Por_Producto'
            ws_prod_ref = workbook['Resumen_Por_Producto']
            data = Reference(ws_prod_ref, min_col=2, min_row=1, max_row=len(resumen_prod) + 1)
            cats = Reference(ws_prod_ref, min_col=1, min_row=2, max_row=len(resumen_prod) + 1)
            
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            
            # Añadir el gráfico a la hoja de resumen ejecutivo
            ws_resumen.add_chart(chart, "D2")

        excel_data = output.getvalue()
        
        st.download_button(
            label="📊 Descargar Excel Profesional con Gráficos y Resumen (.xlsx)",
            data=excel_data,
            file_name=f"reporte_completo_donamery_{datetime.now(bolivia_tz).strftime('%Y-%m-%d_%H-%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
