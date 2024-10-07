from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import timedelta

app = Flask(__name__)

# Función genérica para conectar a la base de datos
def conectar_bd():
    return mysql.connector.connect(
        host="10.9.120.5",  # Cambia por la IP de tu servidor
        port=3306,  # Puerto de MySQL
        user="ropauba",  # Usuario
        password="ropauba111",  # Contraseña
        database="ropauba"  # Base de datos
    )

# Función para convertir los resultados a un formato JSON serializable
def convertir_a_serializable(data):
    serializable_data = []
    for item in data:
        serializable_item = []
        for value in item:
            if isinstance(value, timedelta):
                # Convertir timedelta a segundos
                serializable_item.append(value.total_seconds())
            else:
                serializable_item.append(value)
        serializable_data.append(serializable_item)
    return serializable_data

# Ruta para ver todos los registros de una tabla específica
def obtener_todos_los_registros(tabla):
    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute(f"SELECT * FROM {tabla}")
            resultados = cursor.fetchall()
            cursor.close()
            conexion.close()
            if resultados:
                # Convertir los resultados a un formato JSON serializable
                serializable_resultados = convertir_a_serializable(resultados)
                return jsonify(serializable_resultados)
            else:
                return f"No hay registros en la tabla {tabla}", 200
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500

# Ruta para ver detalles de un registro específico por ID
def obtener_detalles_por_id(tabla, id):
    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute(f"SELECT * FROM {tabla} WHERE id = %s", (id,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()
            if resultado:
                # Convertir el resultado a un formato JSON serializable
                serializable_resultado = convertir_a_serializable([resultado])[0]
                return jsonify(serializable_resultado)
            else:
                return f"No se encontró el registro con ID {id} en la tabla {tabla}", 404
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500


# Rutas para cada tabla
@app.route('/compras')
def mostrar_compras():
    return obtener_todos_los_registros('Compras')

@app.route('/compras/<int:id>')
def detalles_compras(id):
    return obtener_detalles_por_id('Compras', id)

@app.route('/pago')
def mostrar_pago():
    return obtener_todos_los_registros('Pago')

@app.route('/pago/<int:id>')
def detalles_pago(id):
    return obtener_detalles_por_id('Pago', id)

@app.route('/productos')
def mostrar_productos():
    return obtener_todos_los_registros('Productos')

@app.route('/productos/<int:id>')
def detalles_productos(id):
    return obtener_detalles_por_id('Productos', id)

@app.route('/publicaciones')
def mostrar_publicaciones():
    return obtener_todos_los_registros('Publicaciones')

@app.route('/publicaciones/<int:id>')
def detalles_publicaciones(id):
    return obtener_detalles_por_id('Publicaciones', id)

@app.route('/roles')
def mostrar_roles():
    return obtener_todos_los_registros('Roles')

@app.route('/roles/<int:id>')
def detalles_roles(id):
    return obtener_detalles_por_id('Roles', id)

@app.route('/usuariosroles')
def mostrar_usuarios_roles():
    return obtener_todos_los_registros('UsuariosRoles')

@app.route('/usuariosroles/<int:id>')
def detalles_usuarios_roles(id):
    return obtener_detalles_por_id('UsuariosRoles', id)

@app.route('/usuarios')
def mostrar_usuarios():
    return obtener_todos_los_registros('Usuarios')

@app.route('/usuarios/<int:id>')
def detalles_usuarios(id):
    return obtener_detalles_por_id('Usuarios', id)

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
