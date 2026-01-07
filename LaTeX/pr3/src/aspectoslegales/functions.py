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
        # CORRECCIÓN: Usar conn directamente, no conn.conexion
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