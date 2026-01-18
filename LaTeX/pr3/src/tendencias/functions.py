
def crear_o_mencionar_hashtag(cursor, hashtag, id_publicacion):
    if not hashtag.startswith("#"):
        print("Error: El hashtag debe comenzar con #")
        return

    cursor.execute("SELECT menciones FROM HASHTAG WHERE hashtag = :1", [hashtag])
    resultado = cursor.fetchone()

    if resultado:
        cursor.execute("UPDATE HASHTAG SET menciones = menciones + 1 WHERE hashtag = :1", [hashtag])
    else:
        cursor.execute("INSERT INTO HASHTAG (hashtag, menciones) VALUES (:1, 1)", [hashtag])

    cursor.execute("INSERT INTO CONTIENE_HASHTAG (idpublicacion, hashtag) VALUES (:1, :2)", [id_publicacion, hashtag])
    

def listar_tendencias(cursor):
    try:
        cursor.execute("SELECT hashtag, menciones FROM HASHTAG ORDER BY menciones DESC FETCH FIRST 10 ROWS ONLY")
        return cursor.fetchall()

    except Exception as e:
        print (f"Error al listar las tendencias: {e}")
        return []
    

def asignar_categoria_a_tendencia(cursor, hashtag, categoria):
    try:
        cursor.execute("SELECT hashtag FROM HASHTAG WHERE hashtag = :1", [hashtag])
        if not cursor.fetchone():
            return False, "El hashtag no existe en el sistema."

        cursor.execute("UPDATE HASHTAG SET categoria = :1 WHERE hashtag = :2", [categoria, hashtag])
        return True, f"Categoría '{categoria}' asignada a {hashtag}."

    except Exception as e:
        return False, f"Error de BD: {str(e)}"

def mostrar_categoria_ordenada(cursor, categoria):
    try:
        cursor.execute("SELECT hashtag, menciones FROM HASHTAG where categoria = :1 ORDER BY menciones DESC", [categoria])
        return cursor.fetchall()

    except Exception as e:
        print (f"Error al listar las tendencias: {e}")
        return []
    

def eliminar_tendencia(cursor, hashtag):
    try:
        cursor.execute("SELECT hashtag FROM HASHTAG WHERE hashtag = :1", [hashtag])
        if not cursor.fetchone():
            return False, "El hashtag no existe."
        
        cursor.execute("UPDATE HASHTAG SET menciones = 0 WHERE hashtag = :1", [hashtag])
        return True, f"Tendencia --{hashtag}-- eliminada con éxito."
    
    except Exception as e:
       return False, f"Error al eliminar hashtag: {str(e)}"
    
def obtener_categorias_unicas(cursor):
    """
    Recupera todas las categorías distintas que tienen al menos un hashtag asignado.
    """
    try:
        # Usamos DISTINCT para que no se repitan y filtramos los nulos
        cursor.execute("SELECT DISTINCT categoria FROM HASHTAG WHERE categoria IS NOT NULL ORDER BY categoria ASC")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener las categorías únicas: {e}")
        return []