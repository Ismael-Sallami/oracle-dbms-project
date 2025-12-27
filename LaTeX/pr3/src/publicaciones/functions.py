import pyodbc 
import random
from publicidad.functions import listar_activos_bd 
from .utils import conversion_a_int_seguro, vacio_a_none

NUM_PUBLICACIONES_MOSTRAR=5

def obtener_likes_usuario(id_usuario,connection):
    cursor = connection.cursor()
    try:
        cursor.execute("""
                       SELECT IDPUBLICACION FROM ME_GUSTA
                       WHERE IDUSUARIO = :1
                       """, [id_usuario])
        #Se devuelve un set, ya que las búsquedas son O(1), que es lo que nos interesa
        #para poder mostrar en O(n) todas las publicaciones al usuario con los me gusta
        return {row[0] for row in cursor.fetchall()}
    except Exception as e:
        print(f"Error obteniendo likes: {e}")
        return set()
    finally:
        cursor.close()


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
            cursor.execute("""
                            INSERT INTO ME_GUSTA (IDUSUARIO, IDPUBLICACION)
                            VALUES(:1, :2)
                            """, (id_usuario,id_publicacion))
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
    
def obtener_publicaciones(connection,id_usuario,privado=False):
    resultados=[]
    cursor = connection.cursor()
    try:
        if not privado:
            parametros=[]
            sql_query="""
                SELECT PUBLICACION.NOMBRE,
                    PUBLICACION.DESCRIPCION,
                    PUBLICACION.IMAGEN,
                    PUBLICACION.NUM_LIKES,
                    USUARIO.NOMBREUSUARIO,
                    PUBLICACION.IDPUBLICACION
                FROM PUBLICACION
                INNER JOIN USUARIO ON PUBLICACION.IDUSUARIO = USUARIO.IDUSUARIO
                WHERE PUBLICACION.ELIMINADO = 'N'
                """ 
        else:
            parametros=[id_usuario]
            sql_query="""
                SELECT NOMBRE, DESCRIPCION, IMAGEN, NUM_LIKES, IDPUBLICACION
                FROM PUBLICACION WHERE IDUSUARIO = :1 AND ELIMINADO = 'N'
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
