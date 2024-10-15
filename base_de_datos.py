from flask import Flask, jsonify, request
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

# Función para convertir los resultados a un formato JSON serializable con nombres de columnas
def convertir_a_serializable(cursor, data):
    columnas = [desc[0] for desc in cursor.description]  # Obtener los nombres de las columnas
    serializable_data = []
    for item in data:
        serializable_item = {}
        for col_name, value in zip(columnas, item):
            if isinstance(value, timedelta):
                # Convertir timedelta a segundos
                serializable_item[col_name] = value.total_seconds()
            else:
                serializable_item[col_name] = value
        serializable_data.append(serializable_item)
    return serializable_data

# Ruta para ver todos los registros de una tabla específica con paginación
def obtener_todos_los_registros(tabla):
    try:
        page = request.args.get('page', 1, type=int)  # Obtener número de página, por defecto es 1
        page_size = request.args.get('page_size', 12, type=int)  # Tamaño de página, por defecto 10
        offset = (page - 1) * page_size  # Calcular el offset

        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()

            # Consulta para obtener los registros con paginación
            cursor.execute(f"SELECT * FROM {tabla} LIMIT %s OFFSET %s", (page_size, offset))
            resultados = cursor.fetchall()

            # Consulta para contar el número total de registros en la tabla
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            total_registros = cursor.fetchone()[0]  # Total de registros en la tabla

            if resultados:
                # Convertir los resultados a un formato JSON serializable
                serializable_resultados = convertir_a_serializable(cursor, resultados)
                cursor.close()
                conexion.close()

                # Devolver los datos paginados y metadatos adicionales como página, tamaño y total
                return jsonify({
                    'page': page,
                    'page_size': page_size,
                    'total_registros': total_registros,
                    'total_paginas': (total_registros + page_size - 1) // page_size,  # Calcular total de páginas
                    'data': serializable_resultados
                })
            else:
                cursor.close()
                conexion.close()
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
            if resultado:
                # Convertir el resultado a un formato JSON serializable
                serializable_resultado = convertir_a_serializable(cursor, [resultado])[0]
                cursor.close()
                conexion.close()
                return jsonify(serializable_resultado)
            else:
                cursor.close()
                conexion.close()
                return f"No se encontró el registro con ID {id} en la tabla {tabla}", 404
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500


# Rutas para cada tabla con paginación
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
