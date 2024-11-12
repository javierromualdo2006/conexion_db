from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# Función genérica para conectar a la base de datos
def conectar_bd():
    return mysql.connector.connect(
        host="10.9.120.5",  # Cambia por la IP de tu servidor
        port=3306,  # Puerto de MySQL
        user="ropauba",  # Usuario
        password="ropauba111",  # Contraseña
        database="ropauba"  # Base de datos
    )

###############################################################################################################

@app.route('/vista_publicaciones', methods=['GET'])
def vista_publicaciones():
   try:
       conexion = conectar_bd()
       cursor = conexion.cursor(dictionary=True)
       cursor.execute("SELECT id_publicacion, titulo, descripcion, id_Productos, id_Usuarios, Imagen, Precio, Stock FROM vista_publicaciones")
       publicaciones = cursor.fetchall()
      
       # Imprime los datos para verificar que contienen Precio y Stock
       print(publicaciones)


       cursor.close()
       conexion.close()
       return jsonify(publicaciones), 200
   except Error as e:
       return jsonify({"error": f"Error al obtener las publicaciones: {str(e)}"}), 500

################################################################################################################

# Ruta para eliminar un usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    user_id = request.headers.get('user_id')

    if not user_id:
        return jsonify({'error': 'Se requiere autenticación'}), 401

    if not es_administrador(user_id):
        if int(user_id) != id:
            return jsonify({'error': 'Acceso denegado: solo puedes eliminar tu propia cuenta'}), 403

    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM Usuarios WHERE id = %s", (id,))
            conexion.commit()
            filas_afectadas = cursor.rowcount
            cursor.close()
            conexion.close()

            if filas_afectadas > 0:
                return jsonify({'mensaje': 'Usuario eliminado con éxito'}), 200
            else:
                return f"No se encontró el usuario con ID {id}", 404
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500

# Ruta para eliminar una publicación, solo accesible para administradores
@app.route('/publicaciones/<int:id>', methods=['DELETE'])
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


# Ruta para crear una nueva publicación
@app.route('/publicaciones', methods=['POST'])
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

# Ruta para registrar un nuevo usuario
@app.route('/usuarios', methods=['POST'])
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

# Función para convertir los resultados a un formato JSON serializable
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

# Función para verificar si un usuario es administrador
def es_administrador(user_id):
    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            consulta = """
SELECT * FROM Usuarios u JOIN UsuariosRoles ur ON ur.id_Usuario = u.id
JOIN Roles r ON ur.id_Roles = r.id WHERE u.id = %s AND r.Nombre_Rol = "Administrador";
"""
            cursor.execute(consulta, (user_id,))
            cursor.fetchall()
            resultado = cursor.rowcount != 0
            cursor.close()
            conexion.close()
            # Suponemos que el rol 'administrador' está identificado como 'admin' en la columna `rol`
            return resultado
    except Error as e:
        print(f"Error al verificar el rol: {e}")
        return False

# Función para obtener registros con paginación
def obtener_todos_los_registros(tabla):
    try:
        page = request.args.get('page', 1, type=int)  # Obtener número de página, por defecto es 1
        page_size = request.args.get('page_size', 12, type=int)  # Tamaño de página, por defecto 12
        offset = (page - 1) * page_size  # Calcular el offset

        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()

            # Consulta para obtener los registros con paginación
            if tabla in tablas_con_paginacion:
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

                    # Devolver los datos paginados y metadatos adicionales
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
            else:
                # Si la tabla no necesita paginación, simplemente selecciona todo
                cursor.execute(f"SELECT * FROM {tabla}")
                resultados = cursor.fetchall()
                serializable_resultados = convertir_a_serializable(cursor, resultados)
                cursor.close()
                conexion.close()

                return jsonify({'data': serializable_resultados}), 200
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500

# Función para obtener detalles por ID
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

###############################################################################################################

# Rutas para cada tabla con paginación
tablas_con_paginacion = ['']

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

if __name__ == '__main__':
    app.run(debug=True)