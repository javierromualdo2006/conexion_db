from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Ruta para mostrar todos los usuarios
@app.route('/usuarios')
def mostrar_Usuarios():
    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(
            host="10.9.120.5",  # Cambia por la IP de tu servidor
            port=3306,  # Puerto de MySQL
            user="ropauba",  # Usuario
            password="ropauba111",  # Contraseña
            database="ropauba"  # Base de datos
        )

        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM Usuarios")
            resultados = cursor.fetchall()

            # Cerrar el cursor y la conexión
            cursor.close()
            conexion.close()

            # Si hay resultados, devolverlos como JSON
            if resultados:
                return jsonify(resultados)
            else:
                return "No hay usuarios que mostrar", 200

    except Error as e:
        # Devolver mensaje de error si falla la conexión
        return f"Error al conectar a la base de datos: {e}", 500

    # Si algo falla inesperadamente, devolvemos un mensaje genérico
    return "Error inesperado", 500

# Ruta para mostrar detalles de un usuario específico por su ID
@app.route('/usuarios/<int:id>')
def detalles_usuario(id):
    try:
        # Conexión a la base de datos
        conexion = mysql.connector.connect(
            host="10.9.120.5",  # Cambia por la IP de tu servidor
            port=3306,  # Puerto de MySQL
            user="ropauba",  # Usuario
            password="ropauba111",  # Contraseña
            database="ropauba"  # Base de datos
        )

        if conexion.is_connected():
            cursor = conexion.cursor()
            # Consulta SQL para obtener los detalles de un usuario específico
            cursor.execute("SELECT * FROM Usuarios WHERE id = %s", (id,))
            resultado = cursor.fetchone()

            # Cerrar el cursor y la conexión
            cursor.close()
            conexion.close()

            # Si se encuentra el usuario, devolver los detalles como JSON
            if resultado:
                return jsonify(resultado)
            else:
                return f"No se encontró el usuario con ID {id}", 404

    except Error as e:
        # Devolver mensaje de error si falla la conexión
        return f"Error al conectar a la base de datos: {e}", 500

    # Si algo falla inesperadamente, devolvemos un mensaje genérico
    return "Error inesperado", 500

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
