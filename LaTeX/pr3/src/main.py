import sys
from db_connection import DBConnection

# --- IMPORTACIÓN DE SUBSISTEMAS ---
# Descomentar a medida que los compañeros suban su código
from publicidad import menu as publicidad_sys
# from usuarios import menu as usuarios_sys
# from publicaciones import menu as publicaciones_sys
# from tendencias import menu as tendencias_sys
# from mensajeria import menu as mensajeria_sys

def main():
    # 1. Iniciar conexión ÚNICA
    db = DBConnection()
    conn = db.connect()
    
    if not conn:
        print("Saliendo del sistema...")
        sys.exit(1)

    # 2. Bucle del Menú Principal
    while True:
        print("\n========================================")
        print("      SISTEMA DE INFORMACIÓN EKIS       ")
        print("========================================")
        print("1. Gestión de Publicidad (Ismael)")
        print("2. Gestión de Usuarios (Fer)")
        print("3. Gestión de Publicaciones (Javi)")
        print("4. Gestión de Tendencias (Jesús)")
        print("5. Mensajería Privada (Sergio)")
        print("0. Salir")
        print("========================================")
        
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            publicidad_sys.mostrar_menu(conn)
        elif opcion == "2":
            print("⚠️ Módulo en desarrollo (Fer)")
            # usuarios_sys.mostrar_menu(conn)
        elif opcion == "3":
            print("⚠️ Módulo en desarrollo (Javi)")
        elif opcion == "4":
            print("⚠️ Módulo en desarrollo (Jesús)")
        elif opcion == "5":
            print("⚠️ Módulo en desarrollo (Sergio)")
        elif opcion == "0":
            db.close()
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()