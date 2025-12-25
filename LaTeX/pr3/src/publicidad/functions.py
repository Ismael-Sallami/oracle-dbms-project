import oracledb
from datetime import datetime

def crear_anuncio_bd(conn, datos):
    cursor = conn.cursor()
    try:
        # Ahora llamamos con 7 parámetros (:1 a :7)
        sql = "BEGIN CONTRATAR_ANUNCIO(:1, :2, :3, :4, :5, :6, :7); END;"
        
        params = [
            datos['id'], 
            datos['titulo'], 
            datos['cuerpo'], 
            datos['enlace'], 
            datos['fechafin'],
            # Si el usuario no escribe nada, enviamos None (NULL en Oracle)
            datos.get('nom_carac') or None,
            datos.get('val_carac') or None
        ]
        
        cursor.execute(sql, params)
        conn.commit()
        return True

    except oracledb.Error as e:
        error_obj = e.args[0]
        print(f"\n❌ Error de Base de Datos: {error_obj.message}")
        return False
    finally:
        cursor.close()

def listar_anuncios_bd(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT IDANUNCIO, TITULO, FECHAFIN FROM ANUNCIO")
        return cursor.fetchall()
    except oracledb.Error as e: 
        print(f"Error al listar: {e}")
        return []
    finally:
        cursor.close()
        

# del trigger 2

def extender_campana_bd(conn, id_anuncio, nueva_fecha):
    cursor = conn.cursor()
    try:
        # Solo actualizamos si la fecha es nueva
        sql = "UPDATE ANUNCIO SET FECHAFIN = :1 WHERE IDANUNCIO = :2"
        cursor.execute(sql, [nueva_fecha, id_anuncio])
        conn.commit()
        
        # rowcount nos dice cuántas filas se han tocado (0 si el ID no existe)
        if cursor.rowcount > 0:
            return True, "Fecha actualizada correctamente."
        else:
            return False, "El ID del anuncio no existe."
            
    except oracledb.Error as e:
        return False, f"Error BD: {e.args[0].message}"
    finally:
        cursor.close()

def eliminar_anuncio_bd(conn, id_anuncio):
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM ANUNCIO WHERE IDANUNCIO = :1"
        cursor.execute(sql, [id_anuncio])
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Anuncio eliminado."
        else:
            return False, "El ID no existe."
    except oracledb.Error as e:
        return False, f"Error BD: {e.args[0].message}"
    finally:
        cursor.close()
        
        
def listar_activos_bd(conn):
    cursor = conn.cursor()
    try:
        # Seleccionamos ID, Título y Fecha Fin de los que NO están caducados
        sql = """
            SELECT IDANUNCIO, TITULO, FECHAFIN 
            FROM ANUNCIO 
            WHERE FECHAFIN >= TRUNC(SYSDATE)
            ORDER BY FECHAFIN ASC
        """
        cursor.execute(sql)
        filas = cursor.fetchall()
        return filas # Devuelve una lista de tuplas
    except oracledb.Error as e:
        print(f"Error listando: {e}")
        return []
    finally:
        cursor.close()