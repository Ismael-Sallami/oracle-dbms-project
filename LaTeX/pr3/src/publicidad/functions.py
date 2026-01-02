import oracledb
from datetime import datetime

# ==============================================================================
# 1. CREAR ANUNCIO (Llama al Procedure y gestiona el Trigger de Coherencia)
# ==============================================================================
def crear_anuncio_bd(conn, datos):
    cursor = conn.cursor()
    try:
        # Llamamos al procedimiento almacenado CONTRATAR_ANUNCIO
        # Orden de parametros: ID, TITULO, CUERPO, ENLACE, FECHA, NOM_CARAC, VAL_CARAC, ID_PROPIETARIO
        cursor.callproc("CONTRATAR_ANUNCIO", [
            datos['id'],
            datos['titulo'],
            datos['cuerpo'],
            datos['enlace'],
            datos['fechafin'],
            datos['nom_carac'],
            datos['val_carac'],
            datos['id_propietario']
        ])
        # Si llega aquí, es que no hubo error
        return True, "Campaña creada correctamente."

    except oracledb.DatabaseError as e:
        # Recuperamos el objeto de error
        error_obj, = e.args
        mensaje_completo = error_obj.message
        
        print(f"DEBUG SQL Error: {mensaje_completo}") 

        # --- DETECCIÓN DEL TRIGGER (ORA-20005) ---
        if "ORA-20005" in mensaje_completo:
            # Limpiamos el mensaje técnico para mostrar solo el texto del trigger
            partes = mensaje_completo.split("ORA-20005:")
            if len(partes) > 1:
                mensaje_limpio = partes[1].split("\n")[0].strip()
                return False, f"⚠️ DATOS INCORRECTOS: {mensaje_limpio}"
        
        # --- DETECCIÓN DE DUPLICADOS (ORA-00001) ---
        if "ORA-00001" in mensaje_completo:
            return False, "Ese ID de anuncio ya existe. Prueba con otro."

        # Cualquier otro error técnico
        return False, f"Error de Base de Datos: {mensaje_completo}"

    except Exception as e:
        return False, f"Error inesperado en Python: {str(e)}"
    finally:
        cursor.close()

# ==============================================================================
# 2. LISTAR ANUNCIOS (Filtrado por Rol y Estado)
# ==============================================================================
def listar_activos_bd(conn, id_usuario_solicitante, es_admin):
    cursor = conn.cursor()
    resultados = []
    try:
        # Seleccionamos columnas clave. 
        # IMPORTANTE: El orden importa para el menu.py (0:ID, 1:TITULO, 2:FECHA, 3:CUERPO)
        sql = """
            SELECT A.IDANUNCIO, A.TITULO, A.FECHAFIN, A.CUERPO 
            FROM ANUNCIO A 
            WHERE A.ESTADO = 'ACTIVO'
        """
        
        # LÓGICA DE SEGURIDAD (Multitenencia)
        if not es_admin:
            # Si NO es admin, solo ve SU publicidad
            sql += " AND A.IDPROPIETARIO = :1"
            cursor.execute(sql, [id_usuario_solicitante])
        else:
            # Si ES admin, ve todo lo activo
            cursor.execute(sql)
            
        resultados = cursor.fetchall()
        return resultados

    except Exception as e:
        print(f"Error listando: {e}")
        return []
    finally:
        cursor.close()

# ==============================================================================
# 3. GESTIÓN: EXTENDER CAMPAÑA
# ==============================================================================
def extender_campania_bd(conn, id_anuncio, nueva_fecha):
    cursor = conn.cursor()
    try:
        sql = "UPDATE ANUNCIO SET FECHAFIN = :1 WHERE IDANUNCIO = :2"
        cursor.execute(sql, [nueva_fecha, id_anuncio])
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Fecha actualizada correctamente."
        else:
            return False, "El ID del anuncio no existe."
            
    except oracledb.Error as e:
        return False, f"Error BD: {e.args[0].message}"
    finally:
        cursor.close()

# ==============================================================================
# 4. GESTIÓN: ELIMINAR ANUNCIO (Borrado Físico)
# ==============================================================================
def eliminar_anuncio_bd(conn, id_anuncio):
    cursor = conn.cursor()
    try:
        # Nota: Usamos DELETE físico. Si prefieres borrado lógico usa:
        # UPDATE ANUNCIO SET ESTADO = 'ELIMINADO' WHERE ...
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

# ==============================================================================
# 5. UTILIDADES (ROL) ES DE FER
# ==============================================================================
def es_admin_bd(conn, id_usuario):
    """
    Verifica si el usuario tiene rol de Administrador (ESADMIN = 1)
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ESADMIN FROM USUARIO WHERE IDUSUARIO = :1", [id_usuario])
        fila = cursor.fetchone()
        
        if fila and fila[0] == 1:
            return True
        return False
    except Exception as e:
        print(f"Error verificando rol: {e}")
        return False
    finally:
        cursor.close()