import pyodbc

def enviar_mensaje(conn, id1, id2, mensaje):
    cursor = conn.cursor()
    try:
        # Lógica de Savepoint omitida para simplificar compatibilidad dependiendo del driver, 
        # pero mantenemos la lógica de transacción.
        cursor.execute("SELECT 1 FROM AMISTAD WHERE (IDUSUARIO1 = ? AND IDUSUARIO2 = ?)", (id1, id2))
        u1esamigo = cursor.fetchone() is not None
        cursor.execute("SELECT 1 FROM AMISTAD WHERE (IDUSUARIO1 = ? AND IDUSUARIO2 = ?)", (id2, id1))
        u2esamigo = cursor.fetchone() is not None
       
        if u1esamigo and u2esamigo:
            cursor.execute("""
                SELECT 1 FROM CONVERSA 
                WHERE (IDUSUARIO1 = ? AND IDUSUARIO2 = ?) OR (IDUSUARIO1 = ? AND IDUSUARIO2 = ?)
            """, (id1, id2, id2, id1))
            hayconver = cursor.fetchone() is not None

            if not hayconver:
                cursor.execute("INSERT INTO CONVERSA (IDUSUARIO1, IDUSUARIO2) VALUES(?,?)", (id1, id2))
                cursor.execute("INSERT INTO CONVERSA (IDUSUARIO1, IDUSUARIO2) VALUES(?,?)", (id2, id1))
                
            cursor.execute("INSERT INTO MENSAJE (IDUSUARIO1, IDUSUARIO2, MENSAJE) VALUES(?,?,?)", (id1, id2, mensaje))
            conn.commit()
            return True, "Mensaje enviado"
        else:
            return False, "No sois amigos recíprocamente"
        
    except pyodbc.Error as e: 
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()

def eliminar_mensaje(conn, id_usuario_activo, id_mensaje):
    cursor = conn.cursor()
    try:
        # Verificamos que el mensaje exista y pertenezca al usuario activo
        cursor.execute("SELECT 1 FROM MENSAJE WHERE IDMENSAJE = ? AND IDUSUARIO1 = ?", (id_mensaje, id_usuario_activo))
        es_propio = cursor.fetchone() is not None
        
        if es_propio:
            cursor.execute("DELETE FROM MENSAJE WHERE IDMENSAJE = ?", (id_mensaje,))
            conn.commit()
            return True, "Mensaje eliminado"
        else:
            return False, "No puedes borrar este mensaje (no es tuyo o no existe)"
    except pyodbc.Error as e: 
        return False, f"Error: {e}"
    finally:
        cursor.close()

def listar_usuarios(conn, idusuarioactivo, archivados=False):
    cursor = conn.cursor()
    try:
        # Buscamos usuarios que son amigos recíprocos:
        # (idusuarioactivo sigue a U e idusuarioactivo es seguido por U)
        base_query = """
            SELECT u.IDUSUARIO, u.NOMBREUSUARIO
            FROM USUARIO u
            WHERE u.IDUSUARIO IN (
                SELECT a1.IDUSUARIO2 
                FROM AMISTAD a1
                JOIN AMISTAD a2 ON a1.IDUSUARIO1 = a2.IDUSUARIO2 AND a1.IDUSUARIO2 = a2.IDUSUARIO1
                WHERE a1.IDUSUARIO1 = ?
            )
        """
        
        if archivados:
            # Solo los que están en la tabla ARCHIVADO
            query = base_query + " AND u.IDUSUARIO IN (SELECT IDUSUARIO2 FROM ARCHIVADO WHERE IDUSUARIO1 = ?)"
            params = (idusuarioactivo, idusuarioactivo)
        else:
            # Solo los que NO están en la tabla ARCHIVADO
            query = base_query + " AND u.IDUSUARIO NOT IN (SELECT IDUSUARIO2 FROM ARCHIVADO WHERE IDUSUARIO1 = ?)"
            params = (idusuarioactivo, idusuarioactivo)

        cursor.execute(query, params)
        resultado = cursor.fetchall()
        return [(row[0], row[1]) for row in resultado]

    except pyodbc.Error as e:
        print(f"Error en listar_usuarios: {e}")
        return []
    finally:
        cursor.close()

def visualizar_conversacion(conn, idusuarioactivo, idusuario2):
    cursor = conn.cursor()
    try:
        # NOTA: Necesitamos 'm.IDMENSAJE' para poder borrarlo después
        query = """
            SELECT m.IDMENSAJE, m.IDUSUARIO1, u.NOMBREUSUARIO, m.MENSAJE
            FROM MENSAJE m
            JOIN USUARIO u ON m.IDUSUARIO1 = u.IDUSUARIO
            WHERE (m.IDUSUARIO1 = ? AND m.IDUSUARIO2 = ?)
               OR (m.IDUSUARIO1 = ? AND m.IDUSUARIO2 = ?)
            ORDER BY m.FECHAENVIO ASC
        """
        cursor.execute(query, (idusuarioactivo, idusuario2, idusuario2, idusuarioactivo))
        return cursor.fetchall() # Retorna filas crudas [(id_msg, id_remitente, nombre, texto), ...]
    except pyodbc.Error as e: 
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()

def des_archivar_usuario(conn, idusuarioactivo, idusuario2):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM ARCHIVADO WHERE (IDUSUARIO1 = ? AND IDUSUARIO2 = ?)", (idusuarioactivo, idusuario2))
        existe = cursor.fetchone() is not None

        if existe:
            cursor.execute("DELETE FROM ARCHIVADO WHERE (IDUSUARIO1 = ? AND IDUSUARIO2 = ?)",(idusuarioactivo, idusuario2))
            msg = "Usuario Desarchivado"
        else:
            cursor.execute("INSERT INTO ARCHIVADO (IDUSUARIO1, IDUSUARIO2) VALUES(?,?)", (idusuarioactivo, idusuario2))
            msg = "Usuario Archivado"
        conn.commit()
        return True, msg
    except pyodbc.Error as e: 
        return False, f"Error: {e}"
    finally:
        cursor.close()