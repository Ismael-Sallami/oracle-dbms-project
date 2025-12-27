# Eliminamos pyodbc para evitar conflictos de drivers
import oracledb

def enviar_mensaje(conn, id1, id2, mensaje):
    cursor = conn.cursor()
    try:
        # En oracledb los parámetros se pasan como :1, :2, etc. o en una lista
        cursor.execute("SELECT 1 FROM AMISTAD WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)", [id1, id2])
        u1esamigo = cursor.fetchone() is not None
        
        cursor.execute("SELECT 1 FROM AMISTAD WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)", [id2, id1])
        u2esamigo = cursor.fetchone() is not None
        
        if u1esamigo and u2esamigo:
            cursor.execute("""
                SELECT 1 FROM CONVERSA 
                WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2) OR (IDUSUARIO1 = :3 AND IDUSUARIO2 = :4)
            """, [id1, id2, id2, id1])
            hayconver = cursor.fetchone() is not None

            if not hayconver:
                cursor.execute("INSERT INTO CONVERSA (IDUSUARIO1, IDUSUARIO2) VALUES(:1,:2)", [id1, id2])
                cursor.execute("INSERT INTO CONVERSA (IDUSUARIO1, IDUSUARIO2) VALUES(:1,:2)", [id2, id1])
                
            cursor.execute("INSERT INTO MENSAJE (IDUSUARIO1, IDUSUARIO2, MENSAJE) VALUES(:1,:2,:3)", [id1, id2, mensaje])
            conn.commit()
            return True, "Mensaje enviado"
        else:
            return False, "No sois amigos recíprocamente"
        
    except Exception as e: 
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()

def eliminar_mensaje(conn, id_usuario_activo, id_mensaje):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM MENSAJE WHERE IDMENSAJE = :1 AND IDUSUARIO1 = :2", [id_mensaje, id_usuario_activo])
        es_propio = cursor.fetchone() is not None
        
        if es_propio:
            cursor.execute("DELETE FROM MENSAJE WHERE IDMENSAJE = :1", [id_mensaje])
            conn.commit()
            return True, "Mensaje eliminado"
        else:
            return False, "No puedes borrar este mensaje"
    except Exception as e: 
        return False, f"Error: {e}"
    finally:
        cursor.close()

def listar_usuarios(conn, idusuarioactivo, archivados=False):
    cursor = conn.cursor()
    try:
        base_query = """
            SELECT u.IDUSUARIO, u.NOMBREUSUARIO
            FROM USUARIO u
            WHERE u.IDUSUARIO IN (
                SELECT a1.IDUSUARIO2 
                FROM AMISTAD a1
                JOIN AMISTAD a2 ON a1.IDUSUARIO1 = a2.IDUSUARIO2 AND a1.IDUSUARIO2 = a2.IDUSUARIO1
                WHERE a1.IDUSUARIO1 = :1
            )
        """
        
        if archivados:
            query = base_query + " AND u.IDUSUARIO IN (SELECT IDUSUARIO2 FROM ARCHIVADO WHERE IDUSUARIO1 = :2)"
        else:
            query = base_query + " AND u.IDUSUARIO NOT IN (SELECT IDUSUARIO2 FROM ARCHIVADO WHERE IDUSUARIO1 = :2)"

        cursor.execute(query, [idusuarioactivo, idusuarioactivo])
        resultado = cursor.fetchall()
        return [(row[0], row[1]) for row in resultado]

    except Exception as e:
        print(f"Error en listar_usuarios: {e}")
        return []
    finally:
        cursor.close()

def visualizar_conversacion(conn, idusuarioactivo, idusuario2):
    cursor = conn.cursor()
    try:
        query = """
            SELECT m.IDMENSAJE, m.IDUSUARIO1, u.NOMBREUSUARIO, m.MENSAJE
            FROM MENSAJE m
            JOIN USUARIO u ON m.IDUSUARIO1 = u.IDUSUARIO
            WHERE (m.IDUSUARIO1 = :1 AND m.IDUSUARIO2 = :2)
               OR (m.IDUSUARIO1 = :3 AND m.IDUSUARIO2 = :4)
            ORDER BY m.FECHAENVIO ASC
        """
        cursor.execute(query, [idusuarioactivo, idusuario2, idusuario2, idusuarioactivo])
        return cursor.fetchall() 
    except Exception as e: 
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()

def des_archivar_usuario(conn, idusuarioactivo, idusuario2):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM ARCHIVADO WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)", [idusuarioactivo, idusuario2])
        existe = cursor.fetchone() is not None

        if existe:
            cursor.execute("DELETE FROM ARCHIVADO WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)", [idusuarioactivo, idusuario2])
            msg = "Usuario Desarchivado"
        else:
            cursor.execute("INSERT INTO ARCHIVADO (IDUSUARIO1, IDUSUARIO2) VALUES(:1,:2)", [idusuarioactivo, idusuario2])
            msg = "Usuario Archivado"
        conn.commit()
        return True, msg
    except Exception as e: 
        return False, f"Error: {e}"
    finally:
        cursor.close()
