import uuid
import datetime
import oracledb
def _now_date():
    return datetime.datetime.now()

# -------------------------------------------------------------------
# RF4.1: Crear usuario
# -------------------------------------------------------------------
def crear_usuario(conn, nombre_usuario, correo, contrasena, imagen_perfil=None, biografia=None):
    """
    RF4.1 (Crear usuario): nombre, correo, contraseña, opcional imagen/biografía. :contentReference[oaicite:5]{index=5}
    Restricciones recomendables (prácticas): username/email únicos.
    """
    cursor = conn.cursor()
    try:
        # Comprobaciones mínimas
        if not nombre_usuario or not nombre_usuario.strip():
            return False, "Nombre de usuario no puede estar vacío"
        if not correo or not correo.strip():
            return False, "Correo no puede estar vacío"
        if not contrasena or not contrasena.strip():
            return False, "Contraseña no puede estar vacía"

        cursor.execute("SELECT 1 FROM USUARIO WHERE LOWER(NOMBREUSUARIO) = LOWER(:1)", [nombre_usuario])
        if cursor.fetchone():
            return False, "Nombre de usuario ya existe"

        cursor.execute("SELECT 1 FROM USUARIO WHERE LOWER(CORREO) = LOWER(:1)", [correo])
        if cursor.fetchone():
            return False, "Correo ya existe"

        id_usuario = uuid.uuid4().hex  

        cursor.execute("""
            INSERT INTO USUARIO (IDUSUARIO, NOMBREUSUARIO, CORREO, CONTRASENA, IMAGENPERFIL, BIOGRAFIA, FECHACREACION, ELIMINADO)
            VALUES (:1,:2,:3,:4,:5,:6,:7, 0)
        """, [id_usuario, nombre_usuario, correo, contrasena, imagen_perfil, biografia, fecha_creacion])

        conn.commit()
        return True, f"Usuario creado (ID={id_usuario})"

    except Exception as e:
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()


# -------------------------------------------------------------------
# RF4.2: Modificar usuario
# -------------------------------------------------------------------
def modificar_usuario(conn, id_usuario, nombre_usuario=None, correo=None, contrasena=None, imagen_perfil=None, biografia=None):
    """
    RF4.2 (Modificar usuario): permite modificar datos del perfil. :contentReference[oaicite:6]{index=6}
    """
    cursor = conn.cursor()
    try:
        # Verificar que existe y no está eliminado
        cursor.execute("SELECT 1 FROM USUARIO WHERE IDUSUARIO = :1 AND NVL(ELIMINADO,0) = 0", [id_usuario])
        if not cursor.fetchone():
            return False, "Usuario no existe o está eliminado"

        # Si no viene nada que modificar, salimos
        if all(v is None for v in [nombre_usuario, correo, contrasena, imagen_perfil, biografia]):
            return False, "No hay cambios para aplicar"

        # Unicidad opcional si se cambia nombre/correo
        if nombre_usuario is not None:
            if not nombre_usuario.strip():
                return False, "Nombre de usuario no puede estar vacío"
            cursor.execute("""
                SELECT 1 FROM USUARIO
                WHERE LOWER(NOMBREUSUARIO) = LOWER(:1) AND IDUSUARIO <> :2
            """, [nombre_usuario, id_usuario])
            if cursor.fetchone():
                return False, "Nombre de usuario ya existe"

        if correo is not None:
            if not correo.strip():
                return False, "Correo no puede estar vacío"
            cursor.execute("""
                SELECT 1 FROM USUARIO
                WHERE LOWER(CORREO) = LOWER(:1) AND IDUSUARIO <> :2
            """, [correo, id_usuario])
            if cursor.fetchone():
                return False, "Correo ya existe"

        # Construcción dinámica del UPDATE (para no pisar campos que no se tocan)
        sets = []
        params = []

        def add_set(col, val):
            sets.append(f"{col} = :{len(params)+1}")
            params.append(val)

        if nombre_usuario is not None: add_set("NOMBREUSUARIO", nombre_usuario)
        if correo is not None: add_set("CORREO", correo)
        if contrasena is not None: add_set("CONTRASENA", contrasena)
        if imagen_perfil is not None: add_set("IMAGENPERFIL", imagen_perfil)
        if biografia is not None: add_set("BIOGRAFIA", biografia)

        add_set("FECHAMODIFICACION", _now_date())

        params.append(id_usuario)
        sql = f"UPDATE USUARIO SET {', '.join(sets)} WHERE IDUSUARIO = :{len(params)}"
        cursor.execute(sql, params)

        conn.commit()
        return True, "Usuario modificado"

    except Exception as e:
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()


# -------------------------------------------------------------------
# RF4.3: Eliminar usuario
# -------------------------------------------------------------------


def eliminar_usuario(conn, id_usuario, contrasena):
    cursor = conn.cursor()
    try:
        # Verificar credenciales
        cursor.execute("""
            SELECT 1 FROM USUARIO
            WHERE IDUSUARIO = :1 AND CONTRASENA = :2
        """, [id_usuario, contrasena])

        if cursor.fetchone() is None:
            return False, "Credenciales incorrectas o usuario no existe"

        # Borrado físico con cascade
        cursor.execute("DELETE FROM USUARIO WHERE IDUSUARIO = :1", [id_usuario])
        conn.commit()

        return True, "Usuario eliminado definitivamente (con borrado en cascada)"

    except Exception as e:
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()


  

# -------------------------------------------------------------------
# RF4.4: Bloquear / Desbloquear usuario (toggle)
# -------------------------------------------------------------------
def bloquear_desbloquear_usuario(conn, id_emisor, id_objetivo):
    """
    RF4.4 (Bloquear usuario): bloquea a otro usuario (y lo ideal: toggle para desbloquear). :contentReference[oaicite:9]{index=9}
    RS4.1 no auto-bloqueo, RS4.2 usuario existente/no eliminado, RS4.3 no duplicar,
    RS4.5 solo quien bloqueó puede desbloquear. :contentReference[oaicite:10]{index=10}
    """
    cursor = conn.cursor()
    try:
        if id_emisor == id_objetivo:
            return False, "No puedes bloquearte a ti mismo"

        # Comprobar que objetivo existe y no está eliminado
        cursor.execute("SELECT 1 FROM USUARIO WHERE IDUSUARIO = :1 AND NVL(ELIMINADO,0) = 0", [id_objetivo])
        if not cursor.fetchone():
            return False, "Usuario objetivo no existe o está eliminado"

        # ¿Ya existe bloqueo emisor->objetivo?
        cursor.execute("""
            SELECT 1 FROM BLOQUEO
            WHERE IDUSUARIO1 = :1 AND IDUSUARIO2 = :2
        """, [id_emisor, id_objetivo])
        existe = cursor.fetchone() is not None

        if existe:
            # Desbloquear (RS4.5)
            cursor.execute("""
                DELETE FROM BLOQUEO
                WHERE IDUSUARIO1 = :1 AND IDUSUARIO2 = :2
            """, [id_emisor, id_objetivo])
            conn.commit()
            return True, "Usuario desbloqueado"
        else:
            # Al bloquear: eliminar amistad en ambos sentidos
            cursor.execute("""
                DELETE FROM AMISTAD
                WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)
                   OR (IDUSUARIO1 = :2 AND IDUSUARIO2 = :1)
            """, [id_emisor, id_objetivo])

            cursor.execute("""
                INSERT INTO BLOQUEO (IDUSUARIO1, IDUSUARIO2, FECHABLOQUEO)
                VALUES (:1,:2,:3)
            """, [id_emisor, id_objetivo, _now_date()])

            conn.commit()
            return True, "Usuario bloqueado"

    except Exception as e:
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()


# -------------------------------------------------------------------
# RF4.5: Añadir amigo 
# -------------------------------------------------------------------
def anadir_amigo(conn, id_emisor, id_objetivo):
    """
    RF4.5 (Añadir amigo): relación tipo AMISTAD unilateral. :contentReference[oaicite:11]{index=11}
    RS4.5.1 no auto, RS4.5.2 usuario existente/no eliminado, RS4.5.3 no duplicar.
    Además: si hay bloqueos en cualquier sentido, rechazamos.
    """
    cursor = conn.cursor()
    try:
        if id_emisor == id_objetivo:
            return False, "No puedes añadirte a ti mismo"

        # Comprobar objetivo existe y no eliminado
        cursor.execute("SELECT 1 FROM USUARIO WHERE IDUSUARIO = :1 AND NVL(ELIMINADO,0) = 0", [id_objetivo])
        if not cursor.fetchone():
            return False, "Usuario objetivo no existe o está eliminado"

        # Bloqueos (si cualquiera bloqueó a cualquiera, no se permite amistad)
        cursor.execute("""
            SELECT 1 FROM BLOQUEO
            WHERE (IDUSUARIO1 = :1 AND IDUSUARIO2 = :2)
               OR (IDUSUARIO1 = :2 AND IDUSUARIO2 = :1)
        """, [id_emisor, id_objetivo])
        if cursor.fetchone():
            return False, "No se puede añadir como amigo: existe un bloqueo entre ambos"

        # Duplicidad
        cursor.execute("""
            SELECT 1 FROM AMISTAD
            WHERE IDUSUARIO1 = :1 AND IDUSUARIO2 = :2
        """, [id_emisor, id_objetivo])
        if cursor.fetchone():
            return False, "Ya has añadido a este usuario como amigo"

        cursor.execute("""
            INSERT INTO AMISTAD (IDUSUARIO1, IDUSUARIO2, FECHAAMISTAD)
            VALUES (:1,:2,:3)
        """, [id_emisor, id_objetivo, _now_date()])

        conn.commit()
        return True, "Amigo añadido (solicitud/relación unilateral creada)"

    except Exception as e:
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()
