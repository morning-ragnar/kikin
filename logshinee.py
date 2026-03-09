from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import sys
from functools import wraps

app = Flask(__name__)
# Configuración de mensajes flash para la interfaz de usuario
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura' 
app.config['SESSION_TYPE'] = 'filesystem' # Configuración de sesión necesaria para 'logged_in'

# --- Configuración de la base de datos ---
# NOTA: Asegúrate de que estos datos coincidan con tu configuración local de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'tiendita'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

mysql = MySQL(app)

# ----------------- Decorador de Autenticación -----------------

def login_required(f):
    """
    Decorador que verifica si el usuario ha iniciado sesión. 
    Si no, lo redirige a la página de login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica si la clave 'logged_in' existe en la sesión y es True
        if not session.get('logged_in'):
            flash('Por favor, inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- Funciones Auxiliares -----------------

# Función auxiliar para asegurar que 'unitario' es un float, crucial para Jinja
def convert_unitario_to_float(compras):
    """Convierte el campo 'unitario' de cada compra a float."""
    # Maneja si 'compras' es un solo diccionario (de una búsqueda/edición) o una lista
    if isinstance(compras, dict):
        compras_list = [compras]
    elif isinstance(compras, list):
        compras_list = compras
    else:
        return compras # Devuelve si no es lista ni diccionario

    for compra in compras_list:
        if 'unitario' in compra:
            try:
                # Si el campo es un objeto Decimal (típico de MySQLdb) o una cadena, lo convertimos a float.
                compra['unitario'] = float(compra['unitario'])
            except (TypeError, ValueError):
                # En caso de error de conversión, establece 0.0 para evitar fallos.
                compra['unitario'] = 0
    
    # Devuelve el diccionario original si era un diccionario, o la lista modificada
    return compras_list[0] if isinstance(compras, dict) and compras_list else compras_list

def get_compra(id_compra):
    """Función auxiliar para obtener una compra por su ID primario."""
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_compra, nombre, marca, modelo, presentacion, proveedor, unitario FROM compras WHERE id_compra= %s", (id_compra,))
    compra = cursor.fetchone()
    cursor.close()
    
    if compra:
        # Convertir a float antes de devolver
        compra = convert_unitario_to_float(compra)
    
    return compra


# ----------------- Rutas de Autenticación -----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión del usuario."""
    if request.method == 'POST':
        # --- Credenciales de prueba (deben ser almacenadas de forma segura en una aplicación real) ---
        USERNAME = 'admin'
        PASSWORD = 'password'
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['username'] = username # Guarda el nombre de usuario para mostrarlo en index.html
            flash('¡Sesión iniciada correctamente!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales inválidas. Inténtalo de nuevo.', 'error')
            return render_template('login.html')
            
    # Si es GET, simplemente muestra la página de login
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

# ----------------- Rutas de Gestión (Protegidas) -----------------

@app.route('/')
@login_required # Protege esta ruta
def index():
    """Muestra el formulario y la lista de compras existentes."""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_compra, nombre, marca, modelo, presentacion, proveedor, unitario FROM compras ORDER BY id_compra DESC")
        compras = cursor.fetchall()
        cursor.close()
        
        # Convierte el campo unitario para el listado
        compras = convert_unitario_to_float(compras)
        
        # Pasa None para 'compra_a_editar' si no estamos en modo edición
        return render_template('index.html', compras=compras, search_query=None, compra_a_editar=None)
    except Exception as e:
        print(f"Error al conectar/consultar la base de datos: {e}", file=sys.stderr)
        # Muestra un mensaje de error de conexión en el HTML
        return render_template('index.html', error_msg=f"Error de conexión a la base de datos. Detalles: {e}", compras=[], compra_a_editar=None)

@app.route('/add', methods=['POST'])
@login_required # Protege esta ruta
def add():
    """Inserta una nueva compra en la base de datos."""
    if request.method == 'POST':
        try:
            id_compra = request.form['id_compra']
            nombre = request.form['nombre']
            marca = request.form['marca']
            modelo = request.form['modelo']
            presentacion = request.form['presentacion']
            proveedor = request.form['proveedor']
            # Aseguramos que 'unitario' se convierta a float antes de insertarlo en la DB
            unitario = float(request.form['unitario']) 
            
            cursor = mysql.connection.cursor()
            query = """
            INSERT INTO compras (id_compra, nombre, marca, modelo, presentacion, proveedor, unitario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_compra, nombre, marca, modelo, presentacion, proveedor, unitario))
            mysql.connection.commit()
            cursor.close()

            flash('Compra agregada exitosamente', 'success')
            return redirect(url_for('index'))

        except ValueError:
            flash('Error: El costo unitario debe ser un número válido.', 'error')
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error al procesar la compra: {e}", file=sys.stderr)
            flash(f'Error al agregar compra: {e}', 'error')
            return redirect(url_for('index'))

@app.route('/edit/<int:compra_id>')
@login_required # Protege esta ruta
def edit(compra_id):
    """Carga los datos de una compra específica para mostrarlos en el formulario de edición."""
    compra_a_editar = get_compra(compra_id)
    
    if not compra_a_editar:
        flash('Registro de compra no encontrado.', 'error')
        return redirect(url_for('index'))
    
    # Obtenemos la lista completa para mostrarla debajo del formulario de edición
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_compra, nombre, marca, modelo, presentacion, proveedor, unitario FROM compras ORDER BY id_compra DESC")
        compras = cursor.fetchall()
        compras = convert_unitario_to_float(compras)
        cursor.close()
    except Exception as e:
        print(f"Error al obtener listado de compras en edición: {e}", file=sys.stderr)
        compras = [] # Pasa una lista vacía si hay error en la obtención del listado

    # Renderizamos la página principal, pero pasamos la compra a editar
    return render_template('index.html', compras=compras, search_query=None, compra_a_editar=compra_a_editar)

@app.route('/update/<int:compra_id>', methods=['POST'])
@login_required # Protege esta ruta
def update(compra_id):
    """Procesa el envío del formulario de edición y actualiza el registro."""
    if request.method == 'POST':
        try:
            # Los datos vienen del formulario de edición
            id_compra = request.form['id_compra']
            nombre = request.form['nombre']
            marca = request.form['marca']
            modelo = request.form['modelo']
            presentacion = request.form['presentacion']
            proveedor = request.form['proveedor']
            unitario = float(request.form['unitario']) # Convertimos a float
            
            cursor = mysql.connection.cursor()
            query = """
            UPDATE compras SET 
                id_compra = %s,
                nombre = %s, 
                marca = %s, 
                modelo = %s, 
                presentacion = %s, 
                proveedor = %s, 
                unitario = %s
            WHERE id_compra= %s
            """
            # El orden de los argumentos DEBE coincidir con el orden de los %s en la query
            cursor.execute(query, (id_compra, nombre, marca, modelo, presentacion, proveedor, unitario, compra_id))
            mysql.connection.commit()
            cursor.close()
            
            flash('Compra actualizada exitosamente', 'success')
            return redirect(url_for('index'))

        except ValueError:
            flash('Error: El costo unitario debe ser un número válido.', 'error')
            # Redirigir de vuelta a la página de edición para que el usuario pueda corregir
            return redirect(url_for('edit', compra_id=compra_id)) 
        except Exception as e:
            print(f"Error al actualizar la compra: {e}", file=sys.stderr)
            flash(f'Error al actualizar compra: {e}', 'error')
            return redirect(url_for('edit', compra_id=compra_id))

@app.route('/delete/<int:compra_id>', methods=['POST'])
@login_required # Protege esta ruta
def delete(compra_id):
    """Elimina un registro de compra de la base de datos."""
    try:
        cursor = mysql.connection.cursor()
        # La consulta DELETE utiliza el id_compra pasado en la URL
        cursor.execute("DELETE FROM compras WHERE id_compra = %s", (compra_id,))
        mysql.connection.commit()
        cursor.close()

        # Mensaje flash para el usuario, usando la categoría 'danger'
        flash(f'Compra ID {compra_id} eliminada exitosamente.', 'danger')
    except Exception as e:
        print(f"Error al eliminar la compra: {e}", file=sys.stderr)
        flash(f'Error al eliminar la compra ID {compra_id}: {e}', 'error')
        
    # Redirigir a la página principal para ver el listado actualizado
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
@login_required # Protege esta ruta
def search():
    """Busca una compra por id_compra y muestra los resultados."""
    search_query = request.args.get('id_compra')

    if not search_query:
        return redirect(url_for('index'))

    try:
        cursor = mysql.connection.cursor()
        query = "SELECT id_compra, nombre, marca, modelo, presentacion, proveedor, unitario FROM compras WHERE id_compra = %s"
        cursor.execute(query, (search_query,))
        
        results = cursor.fetchall()
        cursor.close()
        
        results = convert_unitario_to_float(results)

        if results:
            flash(f'Se encontró {len(results)} compra(s) con ID "{search_query}"', 'info')
        else:
            flash(f'No se encontraron compras con ID "{search_query}"', 'warning')
        
        # Pasa None para 'compra_a_editar' en la búsqueda
        return render_template('index.html', compras=results, search_query=search_query, compra_a_editar=None)

    except Exception as e:
        print(f"Error en la búsqueda de la base de datos: {e}", file=sys.stderr)
        flash('Error al realizar la búsqueda en la base de datos.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
app.run(host='0.0.0.0', port=5000)




