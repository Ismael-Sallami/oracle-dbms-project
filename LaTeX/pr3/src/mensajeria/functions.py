from . import cifrado

def enviar_mensaje(conn, id1, id2, mensaje):
    # Comprobamos que el mensaje no exceda el limite
    if len(mensaje) > 300:
        return False, "El mensaje excede los 300 caracteres permitidos"
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM AMISTAD WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)", [id1, id2])
        u1esamigo = cursor.fetchone() is not None
        
        cursor.execute("SELECT 1 FROM AMISTAD WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)", [id2, id1])
        u2esamigo = cursor.fetchone() is not None
        
        if u1esamigo and u2esamigo:
            # Ciframos el mensaje
            mensaje_cifrado = cifrado.cipher_suite.encrypt(mensaje.encode()).decode()
            #  Aquí, funciona el trigger, si no existe la conversación, la crea
            cursor.execute("INSERT INTO MENSAJE (IDUSUARIO1, IDUSUARIO2, MENSAJE) VALUES(:1,:2,:3)", [id1, id2, mensaje_cifrado])
            conn.commit()
            return True, "Mensaje enviado"
        else:
            return False, "No sois amigos recíprocamente"
        
    except Exception as e: 
        # ESTO ES LO IMPORTANTE: Muestra el error exacto en la consola
        print("\n--- ERROR AL ENVIAR MENSAJE ---")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Detalle del error: {e}")
        print("-------------------------------\n")
        
        # Hacemos rollback por seguridad si hubo error en la base de datos
        conn.rollback() 
        return False, str(e)
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
        # Definimos si buscamos en ARCHIVADOS o no
        filtro_archivado = "IN" if archivados else "NOT IN"
        
        query = f"""
            SELECT 
                u.IDUSUARIO, 
                u.NOMBREUSUARIO,
                -- Si no hay mensajes, ponemos una fecha antigua para que vayan al final
                NVL(um.ULTIMA_FECHA, TO_DATE('01-01-1900', 'DD-MM-YYYY')) as FECHA_ORDEN,
                -- Contamos cuántos mensajes tiene sin leer el usuario activo de este contacto
                NVL(um.MENSAJES_SIN_LEER, 0) as PENDIENTES
            FROM USUARIO u
            -- Subconsulta para obtener estadísticas de la conversación
            LEFT JOIN (
                SELECT 
                    CASE WHEN IDUSUARIO1 = :1 THEN IDUSUARIO2 ELSE IDUSUARIO1 END as ID_CONTACTO,
                    MAX(FECHAENVIO) as ULTIMA_FECHA,
                    SUM(CASE WHEN IDUSUARIO2 = :1 AND BITVISTO = 'N' THEN 1 ELSE 0 END) as MENSAJES_SIN_LEER
                FROM MENSAJE
                WHERE IDUSUARIO1 = :1 OR IDUSUARIO2 = :1
                GROUP BY CASE WHEN IDUSUARIO1 = :1 THEN IDUSUARIO2 ELSE IDUSUARIO1 END
            ) um ON u.IDUSUARIO = um.ID_CONTACTO
            -- 2. Filtros de amistad recíproca y archivados
            WHERE u.IDUSUARIO IN (
                SELECT a1.IDUSUARIO2 
                FROM AMISTAD a1
                JOIN AMISTAD a2 ON a1.IDUSUARIO1 = a2.IDUSUARIO2 AND a1.IDUSUARIO2 = a2.IDUSUARIO1
                WHERE a1.IDUSUARIO1 = :1
            )
            AND u.IDUSUARIO {filtro_archivado} (SELECT IDUSUARIO2 FROM ARCHIVADO WHERE IDUSUARIO1 = :1)
            -- ORDEN: Primero los que tienen mensajes sin leer, luego por fecha más reciente
            ORDER BY PENDIENTES DESC, FECHA_ORDEN DESC
        """

        cursor.execute(query, [idusuarioactivo]*7)
        resultado = cursor.fetchall()
        
        # Devolvemos ID, Nombre y el contador de Pendientes
        return [(row[0], row[1], row[3]) for row in resultado]

    except Exception as e:
        print(f"Error en listar_usuarios SQL: {e}")
        return []
    finally:
        cursor.close()

def visualizar_conversacion(conn, idusuarioactivo, idusuario2):
    cursor = conn.cursor()
    try:
        # Actualizamos los mensajes a visto
        query_update = """
            UPDATE MENSAJE 
            SET BITVISTO = 'Y' 
            WHERE IDUSUARIO1 = :1 AND IDUSUARIO2 = :2 AND BITVISTO = 'N'
        """
        cursor.execute(query_update, [idusuario2, idusuarioactivo])
        conn.commit()

        # Obtenemos los mensajes cifrados
        query = """
            SELECT m.IDMENSAJE, m.IDUSUARIO1, u.NOMBREUSUARIO, m.MENSAJE, m.FECHAENVIO, m.BITVISTO
            FROM MENSAJE m
            JOIN USUARIO u ON m.IDUSUARIO1 = u.IDUSUARIO
            WHERE (m.IDUSUARIO1 = :1 AND m.IDUSUARIO2 = :2)
               OR (m.IDUSUARIO1 = :3 AND m.IDUSUARIO2 = :4)
            ORDER BY m.FECHAENVIO ASC
        """
        cursor.execute(query, [idusuarioactivo, idusuario2, idusuario2, idusuarioactivo])
        filas = cursor.fetchall()
        
        # Desciframos los mensajes
        conversacion_final = []
        for row in filas:
            id_msg, id_u1, nombre, msg_db, fecha, visto = row
            
            try:
                # Intentamos descifrar el contenido
                # .encode() pasa el string a bytes, decrypt descifra, .decode() vuelve a string
                msg_descifrado = cifrado.cipher_suite.decrypt(msg_db.encode()).decode()
            except Exception:
                # Si no se puede descifrar (mensaje antiguo en texto plano o error de llave)
                # mantenemos el texto original para no perder la historia
                msg_descifrado = msg_db 

            # Añadimos la información del mensaje ya descifrada
            conversacion_final.append((id_msg, id_u1, nombre, msg_descifrado, fecha, visto))

        return conversacion_final 
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