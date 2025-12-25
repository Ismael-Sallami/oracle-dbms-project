import pyodbc
from datetime import datetime

def crear_anuncio_bd(conn, datos_anuncio):
    """
    Llama al procedimiento almacenado para crear un anuncio.
    Recibe: conn (conexión), datos_anuncio (diccionario con los valores)
    Devuelve: True si todo fue bien, False si falló.
    """
    cursor = conn.cursor()
    try:
        # Preparamos los parámetros para el procedimiento almacenado
        # El orden debe coincidir con el del PROCEDURE en SQL
        params = (
            datos_anuncio['id'],      # p_idanuncio
            datos_anuncio['titulo'],  # p_titulo
            datos_anuncio['cuerpo'],  # p_cuerpo
            datos_anuncio['enlace'],  # p_enlace
            datos_anuncio['fechafin'] # p_fechafin (objeto datetime)
        )

        # Llamada al procedimiento PL/SQL
        # La sintaxis {CALL ...} es estándar ODBC
        sql = "{CALL CONTRATAR_ANUNCIO(?, ?, ?, ?, ?)}"
        cursor.execute(sql, params)
        
        # Nota: El commit ya lo hace el procedure, pero por seguridad en pyodbc:
        conn.commit() 
        return True

    except pyodbc.Error as e:
        # Aquí capturamos si el Trigger de fechas salta (ORA-20001)
        print(f"\n❌ Error de Base de Datos: {e}")
        return False
    finally:
        cursor.close()

def listar_anuncios_bd(conn):
    """
    Recupera todos los anuncios para mostrarlos.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IDANUNCIO, TITULO, FECHAFIN FROM ANUNCIO")
        rows = cursor.fetchall()
        return rows
    except pyodbc.Error as e:
        print(f"Error al listar: {e}")
        return []
    finally:
        cursor.close()