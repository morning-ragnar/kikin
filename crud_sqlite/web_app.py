import streamlit as st
import sqlite3
import pandas as pd

# 1. Configuración de la página
st.set_page_config(
    page_title="Gestor de Inventario Pro",
    page_icon="📦",
    layout="wide"
)

# 2. Funciones de Base de Datos
def conectar():
    # check_same_thread=False es vital para aplicaciones web con SQLite
    return sqlite3.connect('inventario_web.db', check_same_thread=False)

def crear_tabla():
    with conectar() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                nombre TEXT NOT NULL, 
                precio REAL NOT NULL, 
                stock INTEGER NOT NULL
            )
        ''')

crear_tabla()

# 3. Interfaz Lateral (Sidebar)
st.sidebar.title("Navegación 🧭")
menu = ["📊 Ver Inventario", "➕ Agregar Producto", "⚙️ Gestionar Registros"]
opcion = st.sidebar.radio("Ir a:", menu)

# --- OPCIÓN: VER INVENTARIO ---
if opcion == "📊 Ver Inventario":
    st.title("📊 Estado del Inventario")
    
    with conectar() as conn:
        df = pd.read_sql_query("SELECT * FROM productos ORDER BY id DESC", conn)
    
    if not df.empty:
        # Cálculo de métricas rápidas
        df['Valor Total'] = df['precio'] * df['stock']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Productos", len(df))
        col2.metric("Stock Total", df['stock'].sum())
        col3.metric("Valor del Inventario", f"${df['Valor Total'].sum():,.2f}")
        
        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no hay productos en la base de datos. ¡Agrega uno en el menú lateral!")

# --- OPCIÓN: AGREGAR PRODUCTO ---
elif opcion == "➕ Agregar Producto":
    st.title("➕ Registrar Nuevo Producto")
    
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del artículo:")
            precio = st.number_input("Precio unitario:", min_value=0.0, format="%.2f")
        with col2:
            stock = st.number_input("Cantidad inicial en stock:", min_value=0, step=1)
        
        enviar = st.form_submit_button("Guardar en Base de Datos")
        
        if enviar:
            if nombre:
                with conectar() as conn:
                    conn.execute('INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)', 
                                 (nombre, precio, stock))
                st.success(f"✅ ¡{nombre} ha sido registrado!")
            else:
                st.error("⚠️ El nombre no puede estar vacío.")

# --- OPCIÓN: ACTUALIZAR/ELIMINAR ---
elif opcion == "⚙️ Gestionar Registros":
    st.title("⚙️ Panel de Gestión")
    
    with conectar() as conn:
        df = pd.read_sql_query("SELECT * FROM productos", conn)
    
    if not df.empty:
        # Selector de producto con ID único para evitar errores
        opciones = [f"{row['id']} | {row['nombre']}" for index, row in df.iterrows()]
        seleccion = st.selectbox("Busca el producto que deseas modificar:", opciones)
        
        id_elegido = int(seleccion.split(" | ")[0])
        datos_prod = df[df['id'] == id_elegido].iloc[0]
        
        st.divider()
        
        col_edit, col_del = st.columns([2, 1])
        
        with col_edit:
            st.subheader("📝 Editar Información")
            # Usamos keys únicas (f"input_{id}") para que Streamlit no se confunda
            edit_nom = st.text_input("Nombre:", value=datos_prod['nombre'], key=f"n_{id_elegido}")
            edit_pre = st.number_input("Precio:", value=float(datos_prod['precio']), key=f"p_{id_elegido}")
            edit_stk = st.number_input("Stock:", value=int(datos_prod['stock']), key=f"s_{id_elegido}")
            
            if st.button("💾 Aplicar Cambios", use_container_width=True):
                with conectar() as conn:
                    conn.execute('UPDATE productos SET nombre=?, precio=?, stock=? WHERE id=?', 
                                 (edit_nom, edit_pre, edit_stk, id_elegido))
                st.success("¡Datos actualizados correctamente!")
                st.rerun()

        with col_del:
            st.subheader("🗑️ Eliminar")
            st.write("Esta operación borrará el registro de forma permanente.")
            if st.button("Eliminar definitivamente", type="primary", use_container_width=True):
                with conectar() as conn:
                    conn.execute('DELETE FROM productos WHERE id=?', (id_elegido,))
                st.warning(f"Producto ID {id_elegido} eliminado.")
                st.rerun()
    else:
        st.info("No hay datos disponibles para gestionar.")