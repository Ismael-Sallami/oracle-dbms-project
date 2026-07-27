import pyodbc 
import random
from publicidad.functions import listar_activos_bd 
from .utils import conversion_a_int_seguro, vacio_a_none

NUM_PUBLICACIONES_MOSTRAR=5

def toggle_like(id_publicacion,id_usuario,cursor):
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
    except Exception as e:
        print(f"Error actualizando me gusta: {e}")

def cargar_anuncio_en_publicacion(anuncio_con):
    print(f"\n==========PUBLICIDAD==========")
    anuncios = listar_activos_bd(anuncio_con)
    if not anuncios:
        print("No se ha podido cargar la lista de anuncios activos")
        print("==========PUBLICIDAD==========")
        return

    anuncio = anuncios[random.randrange(0, len(anuncios))]
    id_anuncio = anuncio[0]
    cursor = anuncio_con.cursor()
    try:
        cursor.execute("""
                       SELECT TITULO,CUERPO,ENLACE
                       FROM ANUNCIO
                       WHERE ANUNCIO.IDANUNCIO = :1
                       """, (id_anuncio,))
        anuncio=cursor.fetchone()
        print(f"{anuncio[0]}\n")
        print(f"{anuncio[1]}")
        print(f"{anuncio[2]}")
    except Exception as e:
        print(f"Error obteniendo el anuncio: {e}")
    finally:
        cursor.close()

    print(f"==========PUBLICIDAD==========\n")

def dar_formato_publicacion(publicacion, index, anuncio_con):
    """
    es importante recordar que una publicación es una tupla que contiene:
        publicacion: nombre, descripcion, imagen, num_likes
        si es listado privado, tenemos dos datos extra
            usuario: nombre 
            publicacion: idpublicacion
        o en el caso en el que el formato sea de listado privado, solo un dato extra:
            publicacion: idpublicacion
    en ese orden, por lo que su longitud es 5 o 6. Pero esta función solo tomará
    los 5 primeros valores.
    index: índice de la publicación en la lista
    anuncio_con: conexion a la base de datos para introducir un anuncio, si desea introducir un anuncio,
    en caso contrario None
    """
    NOM_PUBLI=0
    PUBLI_DESC=1
    NOM_IMG_PUBLI=2
    NUM_LIKES=3
    NOM_USU_OR_ID_PUBLICACION=4
    anuncio_cargado=False
    
    print("----------------------------------------")
    #Si el anuncio va en la última publicacion que se ve, sería razonable
    #ponerlo al principio de la publicación para que el lector lo tenga que ver
    #sí o sí 
    if (index + 1) % NUM_PUBLICACIONES_MOSTRAR == 0 and anuncio_con:
        cargar_anuncio_en_publicacion(anuncio_con)
        anuncio_cargado=True
    print(f"{index}. {publicacion[NOM_PUBLI]}")
    print(f"{publicacion[NOM_USU_OR_ID_PUBLICACION]}        Likes:{publicacion[NUM_LIKES]}")
    if publicacion[NOM_IMG_PUBLI] is not None:
        print(f"{publicacion[NOM_IMG_PUBLI]}")
    print(f"{publicacion[PUBLI_DESC]}")
    #En principio el anuncio tiene que estar dentro, la publicidad se pone como
    #un append, a no ser que sea la última publicación visible desde el visor
    #donde la publicación va en el head
    if not anuncio_cargado and anuncio_con:
        cargar_anuncio_en_publicacion(anuncio_con)
    print("----------------------------------------")


def menu_listado_publicaciones(resultados,cursor,id_usuario,conexion=None):
    publicacion_start=0
    anuncio_en=-1
    while True:
        num_publicaciones=len(resultados)
        publicaciones_en_pantalla=min(NUM_PUBLICACIONES_MOSTRAR,num_publicaciones)
        """
        el problema de hacerlo random es que cada publicación no está al menos a 5 publicaciones
        pero no afecta tanto, es más un detalle, lo peor que podría ocurrir es que haya
        dos anuncios seguidos, se podría solucionar guardando el índice en el que se puso el último
        anuncio y haciendo una condición en la que haya al menos x número de publicaciones
        sin anuncios. Pero ahora mismo no es estrictamente necesario, y seguiría sin ser 
        exactamente cada 5 publicaciones, en cuyo caso simplemente sería elegir un base random al principio de la función
        del 0 hasta min(NUM_PUBLICACIONES_MOSTRAR, num_publicaciones) y sumarlo como offset
        de publicacion_start.

        SOLUCION POR AHORA: Como mínimo tiene que haber dos publicaciones sin anuncios,
        no puede haber más de 5 publicaciones de distancio (rango entre 2 y 5)
        Para ello, si el último anuncio ha estado en NUM_PUBLICACIONES_MOSTRAR-2 o después,
        se va sumando el número: limit_inferior = (anuncio_en+2)% NUM_PUBLICACIONES_MOSTRAR if anuncio_en+2 >= NUM_PUBLICACIONES
        else 0. 
        El límite superior no se tocará, lo que interesa es que no se encuentre con dos anuncios seguidos
        """
        if anuncio_en +2 >= NUM_PUBLICACIONES_MOSTRAR:
            limite_inferior = (anuncio_en+2) % publicaciones_en_pantalla
        else: limite_inferior = 0
        
        anuncio_en=random.randrange(limite_inferior,publicaciones_en_pantalla)
        publicaciones = [resultados[p%num_publicaciones] for p in range(publicacion_start,publicacion_start+publicaciones_en_pantalla)]
        print("\n========================================")
        print(" MENÚ PUBLICACIONES - LISTAR PUBLICACION ")
        print("========================================")
        for id,publi in enumerate(publicaciones):
            dar_formato_publicacion(publi, id+publicacion_start, conexion 
                                    if anuncio_en == id and conexion else None)

        print("========================================")
        print(f"1. Ver las {NUM_PUBLICACIONES_MOSTRAR} siguientes publicaciones")
        print(f"2. Ir a las {NUM_PUBLICACIONES_MOSTRAR} primeras publicaciones")
        print(f"3. Ir a las {NUM_PUBLICACIONES_MOSTRAR} últimas publicaciones")
        print(f"4. Dar me gusta a alguna(s) publicación(es)")
        print(f"5. Salir")
        print("========================================")
        opcion = input("Seleccione una opción: ").strip()
        opcion=conversion_a_int_seguro(opcion)

        if opcion == 1:
            publicacion_start=(publicacion_start + NUM_PUBLICACIONES_MOSTRAR)%num_publicaciones
        elif opcion == 2:
            publicacion_start = 0
        elif opcion == 3:
            if num_publicaciones > NUM_PUBLICACIONES_MOSTRAR:
                publicacion_start=(num_publicaciones-NUM_PUBLICACIONES_MOSTRAR)%num_publicaciones
            else:
                publicacion_start = 0
        elif opcion == 4:
            likes=input("Introduzca los índices de las publicaciones a las que quiere dar me gusta, separados por un espacio").strip()
            if not likes:
                print("No se han introducido ningún indice.")
                continue
            likes=likes.split()
            for like in likes:
                like_idx=conversion_a_int_seguro(like)
                if like_idx is None or like_idx < 0 or like_idx >= len(publicaciones):
                    print("Error en la lectura de los índices")
                    break 
                #obtenemos id_publicacion e id_usuario
                toggle_like(publicaciones[like_idx][-1],id_usuario,cursor)

            
        elif opcion == 5:
            #guardamos los likes
            if conexion is not None:
                conexion.commit()
            return
        else:
            print(f"Opcion {opcion} inválida.")

        resultados=obtener_publicaciones(cursor,id_usuario,conexion is None)



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
    

def obtener_publicaciones(cursor,id_usuario,privado=False):
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
        return cursor.fetchall()
    except Exception as e:
        print(f"Un error ha ocurrido: {e}")
    
    return []

def listar_publicaciones(cursor,id_usuario,conexion=None):
        resultados = obtener_publicaciones(cursor,id_usuario,conexion is None)
        if resultados:
            menu_listado_publicaciones(resultados,cursor,id_usuario,conexion)
        else:
            print("No se encontró ninguna publicación en el sistema")


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
