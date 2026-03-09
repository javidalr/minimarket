# Conexion base de datos

from config.database import obtener_conexion

try:
    conexion = obtener_conexion()
    print('Conexion exitosa a la base de datos')
    conexion.close()
except:
    print(f'Error al conectar: {e}')
