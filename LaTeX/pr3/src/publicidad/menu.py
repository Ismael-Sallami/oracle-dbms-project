from datetime import datetime
from src.publicidad import functions # Importamos tu lógica

def mostrar_menu(conn):
    while True:
        print("\n====================================")
        print("   SUBSISTEMA PUBLICIDAD (Ismael)   ")
        print("====================================")
        print("1. Contratar Nuevo Anuncio (Transacción)")
        print("2. Ver mis anuncios activos")
        print("0. Volver al Menú Principal")
        
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            form_contratar_anuncio(conn)
        elif opcion == "2":
            ver_anuncios(conn)
        elif opcion == "0":
            break
        else:
            print("Opción no válida.")

def form_contratar_anuncio(conn):
    print("\n--- NUEVA CAMPAÑA PUBLICITARIA ---")
    
    # 1. Pedir datos al usuario
    idanuncio = input("ID Anuncio (ej: A001): ")
    titulo = input("Título del anuncio: ")
    cuerpo = input("Cuerpo/Texto: ")
    enlace = input("Enlace URL: ")
    fecha_str = input("Fecha Fin (DD/MM/YYYY): ")

    # 2. Validar formato de fecha en Python antes de enviar
    try:
        fechafin = datetime.strptime(fecha_str, "%d/%m/%Y")
    except ValueError:
        print("❌ Error: Formato de fecha incorrecto. Usa DD/MM/YYYY")
        return

    # 3. Empaquetar datos
    datos = {
        'id': idanuncio,
        'titulo': titulo,
        'cuerpo': cuerpo,
        'enlace': enlace,
        'fechafin': fechafin
    }

    # 4. Llamar a la capa de lógica (functions.py)
    exito = functions.crear_anuncio_bd(conn, datos)

    if exito:
        print("✅ ¡Anuncio contratado con éxito! Transacción completada.")
    else:
        print("⚠️ No se pudo contratar el anuncio. Operación cancelada.")

def ver_anuncios(conn):
    print("\n--- LISTADO DE ANUNCIOS ---")
    filas = functions.listar_anuncios_bd(conn)
    
    if not filas:
        print("(No hay anuncios registrados)")
    else:
        print(f"{'ID':<10} {'TÍTULO':<30} {'FIN CAMPAÑA'}")
        print("-" * 55)
        for row in filas:
            # row[0] es ID, row[1] es TITULO, row[2] es FECHAFIN
            print(f"{row[0]:<10} {row[1]:<30} {row[2]}")