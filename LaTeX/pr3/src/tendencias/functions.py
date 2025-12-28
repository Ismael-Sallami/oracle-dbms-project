import pyodbc

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
    cursor.execute("SELECT hashtag, menciones FROM HASHTAG ORDER BY menciones DESC FETCH FIRST 10 ROWS ONLY")

    resultados = cursor.fetchall()

    if not resultados:
        print("No se encontró ninguna tendencia en el sistema.")

    else:
        print("\n--- TOP 10 TENDENCIAS ---")
        for i, row in enumerate(resultados, 1):
            print(f"{i}. {row[0]}: {row[1]} menciones")

    

def asignar_categoria_a_tendencia(cursor, hashtag, categoria):
    cursor.execute("SELECT hashtag FROM HASHTAG WHERE hashtag = :1", [hashtag])
    if not cursor.fetchone():
        print("Error: El hashtag no existe.")
        return False

    else:
        cursor.execute("UPDATE HASHTAG SET categoria = :1 WHERE hashtag = :2", [categoria, hashtag])
        return True

def mostrar_categoria_ordenada(cursor, categoria):
    cursor.execute("SELECT hashtag, menciones FROM HASHTAG where categoria = :1 ORDER BY menciones DESC", [categoria])

    resultados = cursor.fetchall()

    if not resultados:
        print("No se encontró ninguna tendencia con la categoría --", categoria, "-- en el sistema.")

    else:
        print("\n--- TENDENCIAS EN LA CATEGORÍA ", categoria, " ---")
        for i, row in enumerate(resultados, 1):
            print(f"{i}. {row[0]}: {row[1]} menciones")

def eliminar_tendencia(cursor, hashtag):
    cursor.execute("SELECT hashtag FROM HASHTAG WHERE hashtag = :1", [hashtag])
    if not cursor.fetchone():
        print("Error: El hashtag no existe.")
        return False

    else:
        cursor.execute("UPDATE HASHTAG SET menciones = 0 WHERE hashtag = :1", [hashtag])
        print("Tendencia --", hashtag, "-- eliminada con éxito.")
        return True