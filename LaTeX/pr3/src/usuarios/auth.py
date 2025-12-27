
#aqui hago lo del login por ahora no tiene puesto lo del hash


def login(conn, email, contrasena):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT IDUSUARIO
            FROM USUARIO
            WHERE LOWER(EMAIL) = LOWER(:1)
              AND CONTRASENIA = :2
        """, [email, contrasena])

        row = cursor.fetchone()
        if row is None:
            return False, "Email o contraseña incorrectos"

        return True, row[0]   # id_usuario_activo

    except Exception as e:
        return False, f"Error SQL: {e}"
    finally:
        cursor.close()
