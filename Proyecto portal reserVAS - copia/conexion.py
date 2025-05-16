from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import json
from decimal import Decimal
import logging
import bcrypt  # Importamos bcrypt

# --- Configuración ---
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app) # Habilita CORS para todas las rutas

db_config = {
    'host': 'localhost',   # Formato correcto
    'user': 'root',
    'password': '',
    'database': 'reserva_cafe_db'
}

# --- Configuración de logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# --- Función auxiliar para conexión a BD ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        conn.autocommit = False
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Error de conexión a la BD: {err}")
        return None

# --- Función auxiliar para convertir Decimal a float para JSON ---
def default_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Objeto de tipo {type(obj)} no es serializable por JSON")

# --- Ruta para servir el archivo HTML principal ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# --- Rutas de la API ---
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No se recibieron datos'}), 400

    email = data.get('email')
    password = data.get('contrasena')
    dni = data.get('dni')

    if not email or not password or not dni:
        return jsonify({'message': 'Faltan campos obligatorios'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    registro_exitoso = insertar_cliente(email, hashed_password, dni)

    if registro_exitoso == 1:
        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    else:
        return jsonify({'message': 'Error al registrar el usuario'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No se recibieron datos para el login'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Faltan el email o la contraseña'}), 400

    usuario = obtener_usuario_por_email_login(email)

    if usuario:
        stored_password_hash = usuario[1].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
            return jsonify({'message': 'Login exitoso', 'email': usuario[0]}), 200
        else:
            return jsonify({'message': 'Credenciales incorrectas'}), 401
    else:
        return jsonify({'message': 'Usuario no encontrado'}), 404

@app.route('/reservar_mesa', methods=['POST'])
def realizar_reserva():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No se recibieron datos de la reserva'}), 400

    fecha = data.get('fecha')
    hora = data.get('hora')
    numero_personas = data.get('numero_personas')

    if not fecha or not hora or not numero_personas:
        return jsonify({'message': 'Faltan campos obligatorios para la reserva'}), 400

    reserva_exitosa = reservar_mesa(fecha, hora, int(numero_personas))

    if reserva_exitosa == 1:
        return jsonify({'message': 'Reserva realizada con éxito'}), 201
    else:
        return jsonify({'message': 'Error al realizar la reserva'}), 500

if __name__ =='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

def insertar_cliente(email, contrasena, dni):
    logger.info('Intentando insertar cliente')
    conexion = get_db_connection()
    if conexion is None:
        logger.error('Error de conexión a la BD')
        return 0
    cursor = conexion.cursor()
    query = "INSERT INTO Usuarios (email, contrasena, dni) VALUES (%s, %s, %s)"
    valores = (email, contrasena, dni)
    try:
        cursor.execute(query, valores)
        conexion.commit()
        logger.info(f'Cliente insertado con email: {email}')
        return 1
    except mysql.connector.Error as error:
        logger.error(f'Error al insertar cliente: {error}')
        conexion.rollback()
        return 0
    finally:
        cursor.close()
        conexion.close()

def obtener_usuarios():
    logger.info('Intentando obtener usuarios')
    conexion = get_db_connection()
    if conexion is None:
        logger.error('Error de conexión a la BD')
        return None
    cursor = conexion.cursor()
    query = "SELECT email, contrasena, dni, fecha_registro FROM Usuarios"
    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
        logger.info('Usuarios obtenidos con éxito')
        return resultados
    except mysql.connector.Error as error:
        logger.error(f'Error al obtener usuarios: {error}')
        return None
    finally:
        cursor.close()
        conexion.close()

def reservar_mesa(fecha, hora, numero_personas):
    logger.info('Intentando realizar reserva')
    conexion = get_db_connection()
    if conexion is None:
        logger.error('Error de conexión a la BD')
        return 0
    cursor = conexion.cursor()
    query = "INSERT INTO reservas (fecha, hora, numero_personas) VALUES (%s, %s, %s)"
    valores = (fecha, hora, numero_personas)
    try:
        cursor.execute(query, valores)
        conexion.commit()
        logger.info(f'Reserva realizada para el {fecha} a las {hora} para {numero_personas} personas.')
        return 1
    except mysql.connector.Error as error:
        logger.error(f'Error al realizar la reserva: {error}')
        conexion.rollback()
        return 0
    finally:
        cursor.close()
        conexion.close()

def obtener_cafes(es_dietetico=None):
    logger.info('Intentando obtener cafés')
    conexion = get_db_connection()
    if conexion is None:
        logger.error('Error de conexión a la BD')
        return None
    cursor = conexion.cursor()
    query = "SELECT nombre, descripcion, es_dietetico, precio FROM cafes"
    parametros = []
    if es_dietetico is not None:
        query += " WHERE es_dietetico = %s"
        parametros.append(1 if es_dietetico else 0)
    try:
        cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        logger.info('Cafés obtenidos con éxito')
        return resultados
    except mysql.connector.Error as error:
        logger.error(f'Error al obtener los cafés: {error}')
        return None
    finally:
        cursor.close()
        conexion.close()

def obtener_usuario_por_email_login(email):
    conexion = get_db_connection()
    if conexion is None:
        return None
    cursor = conexion.cursor()
    query = "SELECT email, contrasena, dni, fecha_registro FROM Usuarios WHERE email = %s"
    valores = (email,)
    try:
        cursor.execute(query, valores)
        usuario = cursor.fetchone()
        return usuario
    except mysql.connector.Error as error:
        print(f"Error al buscar el usuario con email {email}:", error)
        return None
    finally:
        cursor.close()
        conexion.close()

# Ejemplo de cómo usar la función:
if __name__ == '__main__':
    email_login = "test@example.com"   # Reemplaza con un email existente en tu BD
    usuario = obtener_usuario_por_email_login(email_login)
    if usuario:
        print(f"Usuario encontrado:")
        print(f"Email: {usuario[0]}, Contraseña (hasheada): {usuario[1]}, DNI: {usuario[2]}, Fecha de Registro: {usuario[3]}")
        # Aquí deberías comparar la contraseña ingresada con usuario[1] usando bcrypt.check_password_hash()
    else:
        print(f"No se encontró ningún usuario con el email '{email_login}'.")