from functions import (
    crear_usuario,
    modificar_usuario,
    eliminar_usuario,
    bloquear_desbloquear_usuario,
    anadir_amigo
)
'''
def mostrar_menu_usuarios(conexion):
    """
    Interfaz de usuario para el subsistema de Usuarios.
    Recibe la conexión global compartida por el sistema.
    """
    while True:
        print("\n========================================")
        print("     SISTEMA EKIS - MENÚ USUARIOS        ")
        print("========================================")
        print("1. Crear usuario (RF4.1)")
        print("2. Modificar usuario (RF4.2)")
        print("3. Eliminar usuario (RF4.3)")
        print("4. Bloquear / Desbloquear usuario (RF4.4)")
        print("5. Añadir amigo (RF4.5)")
        print("6. Volver al Menú Principal")
        print("----------------------------------------")

        opcion = input("Seleccione una opción: ")

        # RF4.1 – Crear usuario
        if opcion == "1":
            nombre = input("Nombre de usuario: ")
            email = input("Email: ")
            password = input("Contraseña: ")
            imagen = input("Imagen de perfil (opcional): ")
            bio = input("Biografía (opcional): ")

            msg = crear_usuario(
                conexion,
                nombre,
                email,
                password,
                imagen if imagen else None,
                bio if bio else None
            )

            print(msg)

        # RF4.2 – Modificar usuario
        elif opcion == "2":
            idu = input("ID del usuario a modificar: ")
            print("Deje en blanco los campos que no quiera modificar.")

            nombre = input("Nuevo nombre de usuario: ")
            email = input("Nuevo email: ")
            password = input("Nueva contraseña: ")
            imagen = input("Nueva imagen de perfil: ")
            bio = input("Nueva biografía: ")

            msg = modificar_usuario(
                conexion,
                int(idu),
                nombre if nombre else None,
                email if email else None,
                password if password else None,
                imagen if imagen else None,
                bio if bio else None
            )

            print(msg)

        # RF4.3 – Eliminar usuario (borrado físico, cascade)
        elif opcion == "3":
            idu = input("ID del usuario a eliminar: ")
            password = input("Contraseña: ")
            confirm = input("¿Está seguro? (S/N): ").upper()

            if confirm == "S":
                msg = eliminar_usuario(conexion, int(idu), password)
                print(msg)
            else:
                print("Operación cancelada.")

        # RF4.4 – Bloquear / Desbloquear usuario
        elif opcion == "4":
            id1 = input("ID del usuario activo: ")
            id2 = input("ID del usuario a bloquear/desbloquear: ")

            msg = bloquear_desbloquear_usuario(conexion, int(id1), int(id2))
            print(msg)

        # RF4.5 – Añadir amigo
        elif opcion == "5":
            id1 = input("ID del usuario activo: ")
            id2 = input("ID del usuario a añadir como amigo: ")

            msg = anadir_amigo(conexion, int(id1), int(id2))
            print(msg)

        elif opcion == "6":
            print("Saliendo del subsistema de Usuarios...")
            break

        else:
            print("Opción no válida. Intente de nuevo.")
'''
def mostrar_menu_usuarios(conexion, id_usuario_activo):
    while True:
        print("\n========================================")
        print(f"     EKIS - MENÚ USUARIOS (ID {id_usuario_activo})")
        print("========================================")
        print("1. Modificar MI usuario (RF4.2)")
        print("2. Eliminar MI usuario (RF4.3)")
        print("3. Bloquear / Desbloquear usuario (RF4.4)")
        print("4. Añadir amigo (RF4.5)")
        print("5. Volver")
        print("----------------------------------------")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            # ya no pides ID, usas el activo
            nombre = input("Nuevo nombre (blank=igual): ") or None
            email = input("Nuevo email (blank=igual): ") or None
            password = input("Nueva contraseña (blank=igual): ") or None
            imagen = input("Nueva imagen (blank=igual): ") or None
            bio = input("Nueva bio (blank=igual): ") or None

            msg = modificar_usuario(conexion, id_usuario_activo, nombre, email, password, imagen, bio)
            print(msg)

        elif opcion == "2":
            password = input("Contraseña: ")
            confirm = input("¿Seguro? (S/N): ").upper()
            if confirm == "S":
                msg = eliminar_usuario(conexion, id_usuario_activo, password)
                print(msg)
                break
            else:
                print("Cancelado.")

        elif opcion == "3":
            id2 = int(input("ID del usuario a bloquear/desbloquear: "))
            msg = bloquear_desbloquear_usuario(conexion, id_usuario_activo, id2)
            print(msg)

        elif opcion == "4":
            id2 = int(input("ID del usuario a añadir como amigo: "))
            msg = anadir_amigo(conexion, id_usuario_activo, id2)
            print(msg)

        elif opcion == "5":
            break
        else:
            print("Opción no válida.")
'''
import oracledb
try:
    connection = oracledb.connect(
            user="ORACLE_USER",
            password="ORACLE_USER",
            dsn="oracle0.ugr.es:1521/practbd"
            )
    mostrar_menu_usuarios(connection)
except Exception as e:
    print(f"Error: {e}")
    exit(127)
'''