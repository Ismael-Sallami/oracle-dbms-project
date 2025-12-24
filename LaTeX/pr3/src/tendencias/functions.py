import pyodbc

def crear_o_mencionar_hashtag(cursor, texto_hashtag):
    # RS2.1: Debe empezar por "#"
    if not texto_hashtag.startswith("#"):
        print("Error: El hashtag debe comenzar con #")
        return

    # RS2.2: Verificar si existe para actualizar o insertar
    cursor.execute("SELECT contador FROM HASHTAG WHERE hashtag = ?", (texto_hashtag,))
    resultado = cursor.fetchone()

    if resultado:
        cursor.execute("UPDATE HASHTAG SET contador = contador + 1 WHERE hashtag = ?", (texto_hashtag,))
    else:
        cursor.execute("INSERT INTO HASHTAG (hashtag, contador) VALUES (?, 1)", (texto_hashtag,))

def listar_tendencias(cursor):
    cursor.execute("SELECT TOP 10 hastag, contador FROM HASHTAG ORDER BY contador DESC")
    for row in cursor.fetchall():
        print(f"{row.hashtag}: {row.contador} menciones")


