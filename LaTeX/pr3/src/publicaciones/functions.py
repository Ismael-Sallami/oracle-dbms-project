import oracledb 
import random
from publicidad.functions import listar_activos_bd 
from .utils import conversion_a_int_seguro, vacio_a_none

NUM_PUBLICACIONES_MOSTRAR=5

def toggle_like(id_publicacion,id_usuario,connection):
    cursor = connection.cursor()
    try:
        cursor.execute("""
                       SELECT 1 FROM ME_GUSTA WHERE
                       IDUSUARIO = :1 AND IDPUBLICACION = :2
                       """, (id_usuario,id_publicacion))
        #Existe la fila? Se borra
        if cursor.fetchone() is not None:
            cursor.execute("""
                            DELETE FROM ME_GUSTA 
                            WHERE IDUSUARIO = :1 AND IDPUBLICACION = :2
                            """, (id_usuario,id_publicacion))
        #No existe la fila? Pues se crea
        else:
            #para evitar posibles errores de concurrencia se hace otro try
            try:
                cursor.execute("""
                            INSERT INTO ME_GUSTA (IDUSUARIO, IDPUBLICACION)
                            VALUES(:1, :2)
                            """, (id_usuario,id_publicacion))
            except Exception as e:
                print("Insert error por concurrencia:",e)
        connection.commit()
    except Exception as e:
        print(f"Error actualizando me gusta: {e}")
    finally:
        cursor.close()

def cargar_anuncio_en_publicacion(anuncios, connection):
    anuncio = anuncios[random.randrange(0, len(anuncios))]
    id_anuncio = anuncio[0]
    cursor = connection.cursor()
    try:
        cursor.execute("""
                       SELECT TITULO,CUERPO,ENLACE
                       FROM ANUNCIO
                       WHERE ANUNCIO.IDANUNCIO = :1
                       """, (id_anuncio,))
        anuncio=cursor.fetchone()
        return anuncio
    except Exception as e:
        print(f"Error obteniendo el anuncio: {e}")
        anuncio=[]
    finally:
        cursor.close()

def crear_publicacion(cursor, id_usuario, nombre, imagen, descripcion, categoria):
    imagen = vacio_a_none(imagen)
    descripcion = vacio_a_none(descripcion)
    categoria = vacio_a_none(categoria)
    try:
        cursor.execute("""
                       INSERT INTO PUBLICACION (NOMBRE, DESCRIPCION, CATEGORIA, IMAGEN, IDUSUARIO)
                       VALUES (:1, :2, :3, :4, :5)
                       """,
                       (nombre,descripcion,categoria,imagen,id_usuario,))
        return True 
    except Exception as e:
        print(f"Un error ha ocurrido: {e}")
        return False

def modificar_publicacion(cursor, id_usuario, id_publicacion, nombre, descripcion, imagen, categoria):
    """
    cabe recordar que para los parámetros se tendrá en cuenta si son None, "" u otro:
        -None: Eso quiere decir que se borra el valor por completo, se pone a null en la BD
        -"": Se conserva el valor original
        -Otro: Ese será el valor con el que se sobreescribe el original
    """
    sql_query="UPDATE PUBLICACION SET"

    set_opciones=[]
    parametros=[]
    opcion=1
    
    #aquí el nombre no puede ser None, será o un str o un falsey como ""
    if nombre:
        set_opciones.append(f"NOMBRE = :{opcion}")
        parametros.append(nombre)
        opcion+=1
    else: pass
    
    #Si es None (se borra el valor y se deja en null) se acepta,
    #Si no es None pero es un str tal que len(str) >= 1 entonces se acepta
    if descripcion is None or descripcion:
        set_opciones.append(f"DESCRIPCION = :{opcion}")
        parametros.append(descripcion)
        opcion+=1
    #Descripcion es un "", eso quiere decir que se conserva el original
    else: pass

    if imagen is None or imagen:
        set_opciones.append(f"IMAGEN = :{opcion}")
        parametros.append(imagen)
        opcion+=1
    else: pass 

    if categoria is None or categoria:
        set_opciones.append(f"CATEGORIA = :{opcion}")
        parametros.append(categoria)
        opcion+=1
    else: pass

    if not set_opciones:
        print("Nada que actualizar.")
        return False
    
    sql_query+=" " + ", ".join(set_opciones) + f" WHERE IDPUBLICACION = :{opcion} AND IDUSUARIO = :{opcion+1}"
    parametros.append(id_publicacion)
    parametros.append(id_usuario)

    try:
        cursor.execute(sql_query,parametros)
        cursor.execute(
                "SELECT 1 FROM PUBLICACION WHERE IDPUBLICACION = :1 AND IDUSUARIO = :2",
                (id_publicacion, id_usuario)
                )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Un error ha ocurrido: {e}")
        return False

def listar_publicaciones(connection, id_usuario, offset=0, limit=10, privado=False):
    resultados = []
    # Parametros base
    parametros = [id_usuario]
    
    cursor = connection.cursor()
    try:
        # Nota: Se añade ORDER BY IDPUBLICACION DESC para que salgan las nuevas primero
        # Se añade la sintaxis de paginación estándar de SQL (funciona en Oracle 12c+, SQL Server, Postgre)
        paginacion_sql = " ORDER BY p.IDPUBLICACION DESC OFFSET :2 ROWS FETCH NEXT :3 ROWS ONLY"
        
        if not privado:
            sql_query = """
                SELECT p.NOMBRE, p.DESCRIPCION, p.IMAGEN,
                NVL(l.num_likes,0) AS NUM_LIKES, u.NOMBREUSUARIO, p.IDPUBLICACION,
                CASE 
                    WHEN ul.IDPUBLICACION IS NOT NULL THEN 1 
                    ELSE 0 
                END AS DIO_LIKE,
                p.IDUSUARIO
                FROM PUBLICACION p 
                LEFT JOIN (
                    SELECT IDPUBLICACION, COUNT(*) AS num_likes
                    FROM ME_GUSTA
                    GROUP BY IDPUBLICACION
                ) l ON l.IDPUBLICACION = p.IDPUBLICACION
                LEFT JOIN USUARIO u ON u.IDUSUARIO = p.IDUSUARIO
                LEFT JOIN (
                    SELECT IDPUBLICACION FROM ME_GUSTA WHERE IDUSUARIO = :1
                ) ul ON ul.IDPUBLICACION = p.IDPUBLICACION
                WHERE p.ELIMINADO = 'N'
                """ + paginacion_sql
        else:
            sql_query = """
                SELECT p.NOMBRE, p.DESCRIPCION, p.IMAGEN,
                NVL(l.num_likes,0) AS NUM_LIKES, p.IDPUBLICACION
                FROM PUBLICACION p 
                LEFT JOIN (
                    SELECT IDPUBLICACION, COUNT(*) AS num_likes
                    FROM ME_GUSTA
                    GROUP BY IDPUBLICACION
                ) l on l.IDPUBLICACION = p.IDPUBLICACION
                WHERE p.ELIMINADO = 'N' AND p.IDUSUARIO = :1
                """ + paginacion_sql

        # Añadimos los parámetros de paginación a la lista
        parametros.append(offset)
        parametros.append(limit)
        
        cursor.execute(sql_query, parametros)
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Un error ha ocurrido: {e}")
        return [] # Retornar lista vacía en error para evitar crash
    finally:
        cursor.close()

def listar_publicaciones_antiguo(connection,id_usuario,privado=False):
    resultados=[]
    parametros=[id_usuario]
    cursor = connection.cursor()
    try:
        if not privado:
            sql_query="""
                SELECT p.NOMBRE, p.DESCRIPCION, p.IMAGEN,
                NVL(l.num_likes,0) AS NUM_LIKES, u.NOMBREUSUARIO, p.IDPUBLICACION,
                CASE 
                    WHEN ul.IDPUBLICACION IS NOT NULL THEN 1 
                    ELSE 0 
                END AS DIO_LIKE,
                p.IDUSUARIO
                FROM PUBLICACION p 
                LEFT JOIN (
                    SELECT IDPUBLICACION, COUNT(*) AS num_likes
                    FROM ME_GUSTA
                    GROUP BY IDPUBLICACION
                ) l ON l.IDPUBLICACION = p.IDPUBLICACION
                LEFT JOIN USUARIO u ON u.IDUSUARIO = p.IDUSUARIO
                LEFT JOIN (
                    SELECT IDPUBLICACION FROM ME_GUSTA WHERE IDUSUARIO = :1
                ) ul ON ul.IDPUBLICACION = p.IDPUBLICACION
                WHERE p.ELIMINADO = 'N'
                """
        else:
            sql_query="""
                SELECT p.NOMBRE, p.DESCRIPCION, p.IMAGEN,
                NVL(l.num_likes,0) AS NUM_LIKES, p.IDPUBLICACION
                FROM PUBLICACION p 
                LEFT JOIN (
                    SELECT IDPUBLICACION, COUNT(*) AS num_likes
                    FROM ME_GUSTA
                    GROUP BY IDPUBLICACION
                ) l on l.IDPUBLICACION = p.IDPUBLICACION
                WHERE p.ELIMINADO = 'N' AND p.IDUSUARIO = :1
                """
        cursor.execute(sql_query,parametros)
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Un error ha ocurrido: {e}")
    finally:
        cursor.close()


def eliminar_publicacion(cursor,id_usuario,id_publicacion):
    try:
        cursor.execute(
                       """
                       UPDATE PUBLICACION SET ELIMINADO='Y'
                       WHERE IDUSUARIO = :1 AND IDPUBLICACION = :2
                       """, (id_usuario,id_publicacion))
        cursor.execute(
                """
                SELECT ELIMINADO FROM PUBLICACION
                WHERE IDUSUARIO = :1 AND IDPUBLICACION = :2
                """, (id_usuario,id_publicacion)
                )
        row = cursor.fetchone()
        if row and row[0] == 'Y':
            print(f"Publicación {id_publicacion} eliminada con éxito.")
            return True 
        else:
            print("No se encontró la publicación o no tiene permiso para eliminarla")
            return False
    except Exception as e:
        print(f"Error obteniendo el anuncio: {e}")
        return False
