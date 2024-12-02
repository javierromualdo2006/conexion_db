from flask import Flask, jsonify, request, render_template
import mysql.connector
from mysql.connector import Error
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Función para conectar a la base de datos
def conectar_bd():
    return mysql.connector.connect(
        host="10.9.120.5",  # Cambia por la IP de tu servidor
        port=3306,  # Puerto de MySQL
        user="ropauba",  # Usuario
        password="ropauba111",  # Contraseña
        database="ropauba"  # Base de datos
    )

# Función para verificar si un usuario es administrador
def es_administrador(user_id):
    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = """
SELECT * FROM Usuarios u 
JOIN UsuariosRoles ur ON ur.id_Usuario = u.id
JOIN Roles r ON ur.id_Roles = r.id 
WHERE u.id = %s AND r.Nombre_Rol = "Administrador";
"""
            cursor.execute(consulta, (user_id,))
            cursor.fetchall()
            resultado = cursor.rowcount != 0
            cursor.close()
            conexion.close()
            return resultado
    except Error as e:
        print(f"Error al verificar el rol: {e}")
        return False


# Ruta para eliminar una publicación, solo accesible para administradores
@app.route('/api/publicaciones/<int:id>', methods=['DELETE'])
def eliminar_publicacion(id):
    user_id = request.headers.get('User-Id')

    if not user_id or not es_administrador(user_id):
        return jsonify({'error': 'Acceso denegado: se requiere rol de administrador'}), 403

    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Publicaciones WHERE id = %s", (id,))
            conexion.commit()
            filas_afectadas = cursor.rowcount
            cursor.close()
            conexion.close()

            if filas_afectadas > 0:
                return jsonify({'mensaje': 'Publicación eliminada con éxito'}), 200
            else:
                return f"No se encontró la publicación con ID {id}", 404
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500

###############################################################################################################

@app.route('/api/publicaciones', methods=['POST'])
def crear_publicacion():
    datos = request.json
    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = """
                INSERT INTO Publicaciones (titulo, descripcion, precio, id_producto)
                VALUES (%s, %s, %s, %s)
            """
            valores = (datos['titulo'], datos['descripcion'], datos['precio'], datos['id_producto'])
            cursor.execute(consulta, valores)
            conexion.commit()
            cursor.close()
            conexion.close()
            return jsonify({'mensaje': 'Publicación creada con éxito'}), 201
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500

@app.route('/api/usuarios', methods=['POST'])
def registrar_usuario():
    datos = request.json
    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = """
                INSERT INTO Usuarios (nombre, email, contraseña, rol)
                VALUES (%s, %s, %s, %s)
            """
            valores = (datos['nombre'], datos['email'], datos['contraseña'], datos['rol'])
            cursor.execute(consulta, valores)
            conexion.commit()
            cursor.close()
            conexion.close()
            return jsonify({'mensaje': 'Usuario registrado con éxito'}), 201
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500

################################################################################################################

# Rutas de renderizado con templates

@app.route('/vista_publicaciones', methods=['GET'])
def vista_publicaciones_html():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_publicacion, titulo, descripcion, id_Productos, id_Usuarios, Imagen, Precio, Stock FROM vista_publicaciones")
        publicaciones = cursor.fetchall()

        cursor.close()
        conexion.close()
        return render_template('vista_publicaciones.html', publicaciones=publicaciones)
    except Error as e:
        return render_template('error.html', error_message=f"Error al obtener las publicaciones: {str(e)}")

from flask import jsonify

@app.route('/publicaciones', methods=['GET'])
def publicaciones():
    try:
        # Conexión a la base de datos
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_Productos, titulo, imagen, descripcion FROM Publicaciones")
        publicaciones = cursor.fetchall()

        # Cerrar la conexión y devolver las publicaciones como JSON
        cursor.close()
        conexion.close()
        return jsonify(publicaciones)

    except Error as e:
        # En caso de error, devuelve un JSON con el mensaje de error
        return jsonify({"error": f"Error al obtener las publicaciones: {str(e)}"}), 500

@app.route('/usuarios', methods=['GET'])
def usuarios_html():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, email, rol FROM Usuarios")
        usuarios = cursor.fetchall()

        cursor.close()
        conexion.close()
        return render_template('usuarios.html', usuarios=usuarios)
    except Error as e:
        return render_template('error.html', error_message=f"Error al obtener los usuarios: {str(e)}")

###############################################################################################################

if __name__ == '__main__':
    app.run(debug=True)
