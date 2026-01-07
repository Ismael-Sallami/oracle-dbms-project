def enviar_reporte(conn, id_objetivo, tipo, id_denunciado, motivo, contenido_original=""):
    # Seguridad: Verificar sesión activa
    if not hasattr(conn, 'id_usuario_actual') or conn.id_usuario_actual is None:
        print("Error: No se puede reportar sin una sesión activa.")
        return False

    contenido_para_prueba = contenido_original

    # Intentar descifrar solo si es un mensaje y parece estar cifrado
    if tipo == 'MENSAJE' and contenido_original:
        try:
            # Fernet lanza error si el texto no es un token válido
            contenido_para_prueba = cifrado.cipher_suite.decrypt(contenido_original.encode()).decode()
        except Exception:
            # Si falla el descifrado, asumimos que es texto plano o cifrado incompatible
            contenido_para_prueba = contenido_original

    sql = """
    INSERT INTO REPORTE (
        ID_DENUNCIANTE, ID_DENUNCIADO, ID_PUB, ID_MENSAJE, 
        TIPO_CONTENIDO, CONTENIDO_PRUEBA, MOTIVO
    ) VALUES (:1, :2, :3, :4, :5, :6, :7)
    """
    
    id_pub = id_objetivo if tipo == 'PUBLICACION' else None
    id_mensaje = id_objetivo if tipo == 'MENSAJE' else None
    
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (
            conn.id_usuario_actual,
            id_denunciado, 
            id_pub, 
            id_mensaje, 
            tipo, 
            contenido_para_prueba, 
            motivo
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error al insertar reporte: {e}")
        try:
            conn.rollback() # CORRECCIÓN: Rollback directo sobre conn
        except:
            pass
        return False
    finally:
        if cursor:
            cursor.close()

def listar_todos_los_reportes(conn):
    sql = """
    SELECT 
        r.IDREPORTE,
        u1.NOMBREUSUARIO AS DENUNCIANTE,
        u2.NOMBREUSUARIO AS DENUNCIADO_NOMBRE, -- Nombre para mostrar
        r.TIPO_CONTENIDO,
        r.MOTIVO,
        r.CONTENIDO_PRUEBA,
        r.ID_PUB,
        r.ID_MENSAJE,
        r.ID_DENUNCIADO  -- <--- AÑADIMOS EL ID NUMÉRICO AQUÍ (índice 8)
    FROM REPORTE r
    JOIN USUARIO u1 ON r.ID_DENUNCIANTE = u1.IDUSUARIO
    JOIN USUARIO u2 ON r.ID_DENUNCIADO = u2.IDUSUARIO
    ORDER BY r.IDREPORTE DESC
    """
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        reportes = cursor.fetchall()
        return reportes
    except Exception as e:
        print(f"Error al listar reportes: {e}")
        return []
    finally:
        if cursor:
            cursor.close()

def obtener_detalle_publicacion(conn, id_p):
    sql = "SELECT NOMBRE, DESCRIPCION, CATEGORIA, IMAGEN, FECHACREACION FROM PUBLICACION WHERE IDPUBLICACION = :1"
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (id_p,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener detalle de publicación: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
            
def eliminar_publicacion_bd(conn, id_u, id_p):
    try:
        from publicaciones import functions as pub_funcs
        
        cursor = conn.cursor()
        
        exito = pub_funcs.eliminar_publicacion(cursor, id_u, id_p)
        
        if exito:
            conn.commit()
            return True
        else:
            conn.rollback()
            return False
    except Exception as e:
        print(f"Error en eliminar_publicacion_bd: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if 'cursor' in locals(): cursor.close()

def eliminar_reporte(conn, id_r):

    sql = "DELETE FROM REPORTE WHERE IDREPORTE = :1"
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, [id_r])
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar reporte: {e}")
        conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
