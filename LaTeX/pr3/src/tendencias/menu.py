from .functions import (
    listar_tendencias, 
    asignar_categoria_a_tendencia, 
    mostrar_categoria_ordenada, 
    eliminar_tendencia
)

def mostrar_menu_tendencias(conexion):
    """
    Interfaz de usuario para el subsistema de Tendencias.
    Recibe la conexión global compartida por el sistema.
    """
    cursor = conexion.cursor()
    
    while True:
        print("\n========================================")
        print("    SISTEMA EKIS - MENÚ TENDENCIAS    ")
        print("========================================")
        print("1. Ver Top 10 Tendencias (RF2.2)")
        print("2. Ver hashtags por Categoría (RF2.4)")
        print("3. Asignar Categoría a Hashtag [ADMIN] (RF2.3)")
        print("4. Eliminar/Resetear Tendencia [ADMIN] (RF2.5)")
        print("5. Volver al Menú Principal")
        print("----------------------------------------")
        
        # El RF2.1:Crear o mencionar hashtag no se incluye porque se activa con un disparador.

        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            listar_tendencias(cursor)
            
        elif opcion == "2":
            cat = input("Introduzca la categoría a consultar: ")
            mostrar_categoria_ordenada(cursor, cat)
            
        elif opcion == "3":
            tag = input("Hashtag (incluyendo #): ")
            cat = input("Nueva categoría: ")
            if asignar_categoria_a_tendencia(cursor, tag, cat):
                conexion.commit() # Confirmar cambios en la base de datos
                print(f"Categoría '{cat}' asignada con éxito a {tag}.")
                
        elif opcion == "4":
            tag = input("Introduzca el hashtag para eliminar de tendencias: ")
            if eliminar_tendencia(cursor, tag):
                conexion.commit() # Confirmar reseteo del contador
                
        elif opcion == "5":
            print("Saliendo del subsistema de Tendencias...")
            break
            
        else:
            print("Opción no válida. Intente de nuevo.")

    cursor.close()