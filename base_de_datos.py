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


# Función para verificar si un usuario es administrador
def es_administrador(user_id):
    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("SELECT rol FROM Usuarios WHERE id = %s", (user_id,))
            resultado = cursor.fetchone()
            cursor.close()
            conexion.close()

            # Suponemos que el rol 'administrador' está identificado como 'admin' en la columna `rol`
            if resultado and resultado[0] == 'admin':
                return True
    except Error as e:
        print(f"Error al verificar el rol: {e}")
    return False

# Ruta para eliminar un usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    # Obtener el user_id del encabezado de la solicitud
    user_id = request.headers.get('user_id')

    # Validar que user_id se haya enviado en los encabezados
    if not user_id:
        return jsonify({'error': 'Se requiere autenticación'}), 401

    # Verificar si el usuario es administrador
    if not es_administrador(user_id):
        # Si el usuario no es administrador, solo puede eliminar su propia cuenta
        if int(user_id) != id:
            return jsonify({'error': 'Acceso denegado: solo puedes eliminar tu propia cuenta'}), 403

    # Realizar la eliminación
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
    # Obtener el user_id del encabezado de la solicitud para verificar su rol
    user_id = request.headers.get('user_id')
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

# Ruta para crear un usuario en la tabla Usuarios, verificando que el correo no exista
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    datos = request.json
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    contraseña = datos.get('contraseña')

    if not (nombre and correo and contraseña):
        return jsonify({'error': 'Faltan datos para crear el usuario'}), 400

    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()

            # Verificar si el correo ya existe
            cursor.execute("SELECT id FROM Usuarios WHERE correo = %s", (correo,))
            usuario_existente = cursor.fetchone()
            
            if usuario_existente:
                cursor.close()
                conexion.close()
                return jsonify({'error': 'El correo ya está en uso'}), 409

            # Si el correo no existe, crear el usuario
            cursor.execute(
                "INSERT INTO Usuarios (nombre, correo, contraseña) VALUES (%s, %s, %s)",
                (nombre, correo, contraseña)
            )
            conexion.commit()
            nuevo_id = cursor.lastrowid
            cursor.close()
            conexion.close()
            return jsonify({'mensaje': 'Usuario creado con éxito', 'id': nuevo_id}), 201
    except Error as e:
        return jsonify({'error': f"Error al conectar a la base de datos: {e}"}), 500
    return jsonify({'error': 'Error inesperado'}), 500

# Rutas para agregar registros en la tabla Publicaciones
@app.route('/publicaciones', methods=['POST'])
def crear_publicacion():
    datos = request.json
    titulo = datos.get('titulo')
    contenido = datos.get('contenido')
    autor_id = datos.get('autor_id')

    if not (titulo and contenido and autor_id):
        return "Faltan datos para crear la publicación", 400

    try:
        conexion = conectar_bd()
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO Publicaciones (titulo, contenido, autor_id) VALUES (%s, %s, %s)",
                (titulo, contenido, autor_id)
            )
            conexion.commit()
            nueva_id = cursor.lastrowid
            cursor.close()
            conexion.close()
            return jsonify({'mensaje': 'Publicación creada con éxito', 'id': nueva_id}), 201
    except Error as e:
        return f"Error al conectar a la base de datos: {e}", 500
    return "Error inesperado", 500



# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
