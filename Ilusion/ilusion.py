import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid
import io

# --- CONFIGURACIÓN BASE DE DATOS ---
DB_NAME = "ilusion_v3.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Inventario: Producto + Modelo + Color forman la identidad
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventario 
                          (producto TEXT, modelo TEXT, color TEXT, stock INTEGER, precio REAL,
                           PRIMARY KEY (producto, modelo, color))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas 
                          (id TEXT, fecha TEXT, producto TEXT, modelo TEXT, color TEXT, cantidad INTEGER, total REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS apartados 
                          (id TEXT, cliente TEXT, producto TEXT, modelo TEXT, color TEXT, cantidad INTEGER, fecha TEXT)''')
        conn.commit()

def run_query(query, params=()):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

def get_df(table_name):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

# --- INICIALIZACIÓN ---
st.set_page_config(page_title="Ilusion - Control de Inventario", layout="wide")
init_db()

# --- LÓGICA DE ALERTAS ---
def check_low_stock():
    df = get_df("inventario")
    low_stock = df[df['stock'] < 2]
    return low_stock

# --- INTERFAZ ---
st.title("👙 Sistema Ilusion: Gestión de Lencería")

# Notificaciones de Stock Bajo
alertas = check_low_stock()
if not alertas.empty:
    st.error(f"⚠️ ¡ATENCIÓN! Tienes {len(alertas)} productos con stock crítico (menos de 2 unidades).")

menu = ["📦 Inventario", "💰 Ventas", "📝 Apartados", "📊 Cierre de Caja", "📥 Importar/Exportar", "🛠 Admin Catálogo"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- 1. INVENTARIO ---
if choice == "📦 Inventario":
    st.header("Inventario de Mercancía")
    df_inv = get_df("inventario")
    
    # Formateo condicional para resaltar stock bajo
    def color_stock(val):
        color = 'red' if val < 2 else 'white'
        return f'color: {color}; font-weight: bold'

    if not df_inv.empty:
        st.dataframe(df_inv.style.map(color_stock, subset=['stock']), use_container_width=True)
    else:
        st.info("El inventario está vacío. Ve a 'Admin Catálogo' para empezar.")

# --- 2. VENTAS ---
elif choice == "💰 Ventas":
    st.header("Nueva Venta")
    df_inv = get_df("inventario")
    
    if df_inv.empty:
        st.warning("No hay productos disponibles.")
    else:
        # Creamos una etiqueta amigable para el selectbox
        df_inv['display'] = df_inv['producto'] + " - " + df_inv['modelo'] + " (" + df_inv['color'] + ")"
        
        with st.form("venta_form"):
            seleccion = st.selectbox("Seleccione Producto/Modelo/Color", df_inv['display'])
            cant = st.number_input("Cantidad", min_value=1, step=1)
            btn_vender = st.form_submit_button("Finalizar Venta")
            
            if btn_vender:
                # Extraer datos del producto seleccionado
                row = df_inv[df_inv['display'] == seleccion].iloc[0]
                if row['stock'] >= cant:
                    id_v = str(uuid.uuid4())[:6].upper()
                    # Descontar
                    run_query("UPDATE inventario SET stock = stock - ? WHERE producto = ? AND modelo = ? AND color = ?", 
                              (cant, row['producto'], row['modelo'], row['color']))
                    # Registrar
                    run_query("INSERT INTO ventas VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (id_v, datetime.now().strftime("%Y-%m-%d"), row['producto'], row['modelo'], row['color'], cant, cant * row['precio']))
                    st.success(f"Venta #{id_v} registrada con éxito.")
                else:
                    st.error("No hay suficiente stock para esta variante.")

# --- 3. APARTADOS ---
elif choice == "📝 Apartados":
    st.header("Control de Apartados")
    t1, t2 = st.tabs(["Crear Apartado", "Ver/Cancelar"])
    
    with t1:
        df_inv = get_df("inventario")
        df_inv['display'] = df_inv['producto'] + " - " + df_inv['modelo'] + " (" + df_inv['color'] + ")"
        with st.form("ap_form"):
            cli = st.text_input("Nombre de la Clienta")
            sel_ap = st.selectbox("Producto a Apartar", df_inv['display'])
            c_ap = st.number_input("Cantidad", min_value=1)
            if st.form_submit_button("Confirmar Apartado"):
                row_ap = df_inv[df_inv['display'] == sel_ap].iloc[0]
                id_ap = "AP-" + str(uuid.uuid4())[:4].upper()
                run_query("UPDATE inventario SET stock = stock - ? WHERE producto = ? AND modelo = ? AND color = ?", 
                          (c_ap, row_ap['producto'], row_ap['modelo'], row_ap['color']))
                run_query("INSERT INTO apartados VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (id_ap, cli, row_ap['producto'], row_ap['modelo'], row_ap['color'], c_ap, datetime.now().strftime("%Y-%m-%d")))
                st.success(f"Apartado {id_ap} guardado.")

    with t2:
        df_ap = get_df("apartados")
        st.dataframe(df_ap, use_container_width=True)
        if not df_ap.empty:
            id_canc = st.selectbox("ID para Cancelar", df_ap['id'])
            if st.button("❌ Revertir Apartado"):
                info = df_ap[df_ap['id'] == id_canc].iloc[0]
                run_query("UPDATE inventario SET stock = stock + ? WHERE producto = ? AND modelo = ? AND color = ?", 
                          (int(info['cantidad']), info['producto'], info['modelo'], info['color']))
                run_query("DELETE FROM apartados WHERE id = ?", (id_canc,))
                st.rerun()

# --- 4. CIERRE DE CAJA ---
elif choice == "📊 Cierre de Caja":
    st.header("Cierre Diario")
    df_v = get_df("ventas")
    hoy = datetime.now().strftime("%Y-%m-%d")
    v_hoy = df_v[df_v['fecha'] == hoy]
    
    if not v_hoy.empty:
        st.metric("Total Recaudado Hoy", f"${v_hoy['total'].sum():,.2f}")
        st.dataframe(v_hoy, use_container_width=True)
        # Exportar
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            v_hoy.to_excel(writer, index=False, sheet_name='Cierre')
        st.download_button("📥 Descargar Reporte Hoy", output.getvalue(), f"Cierre_{hoy}.xlsx")
    else:
        st.info("Sin movimientos hoy.")

# --- 5. IMPORTAR/EXPORTAR ---
elif choice == "📥 Importar/Exportar":
    st.header("Manejo de Base de Datos (Excel)")
    st.subheader("Importar Catálogo Masivo")
    st.info("Formato requerido: producto, modelo, color, stock, precio")
    file = st.file_uploader("Subir Excel", type=["xlsx"])
    if file:
        df_new = pd.read_excel(file)
        if st.button("🚀 Sobrescribir Inventario"):
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute("DELETE FROM inventario")
                df_new.to_sql('inventario', conn, if_exists='append', index=False)
            st.success("Inventario actualizado.")

# --- 6. ADMIN ---
elif choice == "🛠 Admin Catálogo":
    st.header("Control de Existencias")
    with st.form("manual_crud"):
        col1, col2, col3 = st.columns(3)
        p_n = col1.text_input("Producto (ej. Brasier)")
        p_m = col2.text_input("Modelo (ej. 1234)")
        p_c = col3.text_input("Color")
        p_s = st.number_input("Stock", min_value=0)
        p_p = st.number_input("Precio", min_value=0.0)
        
        if st.form_submit_button("Guardar/Actualizar Producto"):
            run_query("INSERT OR REPLACE INTO inventario VALUES (?, ?, ?, ?, ?)", (p_n, p_m, p_c, p_s, p_p))
            st.success("Producto actualizado en el sistema.")