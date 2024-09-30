import sqlite3

# 1. Conectar a la base de datos SQLite
conexion = sqlite3.connect('ropauba.db')
cursor = conexion.cursor()

# 2. Configurar el puerto serie (ajusta 'COM3' al puerto adecuado en tu sistema)
ser = serial.Serial('8080', 9600)  # Cambia COM3 según tu puerto (ej: COM4, COM5)
time.sleep(2)  # Esperar para asegurar que el puerto esté listo

# 3. Leer los datos de la tabla
cursor.execute('SELECT * FROM productos')
productos = cursor.fetchall()

# 4. Enviar los datos por el puerto serie
for producto in productos:
    mensaje = f'ID: {producto[0]}, Nombre: {producto[1]}, Precio: {producto[2]}, Cantidad: {producto[3]}\n'
    ser.write(mensaje.encode())  # Convertir a bytes para enviar por el puerto serie
    time.sleep(1)  # Pausa de 1 segundo entre envíos

# 5. Cerrar la conexión de la base de datos y el puerto serie
cursor.close()
conexion.close()
ser.close()