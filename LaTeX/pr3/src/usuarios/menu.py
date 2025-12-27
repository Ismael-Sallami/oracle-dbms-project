from .functions import (
    crear_usuario,
    modificar_usuario,
    eliminar_usuario,
    bloquear_desbloquear_usuario,
    anadir_amigo
)

def mostrar_menu_usuarios(conexion):
    """
    Interfaz de usuario para el subsistema de Usuarios.
    Recibe la conexión global compartida por el sistema.
    """
    cursor = conexion.cursor()

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

            ok, msg = crear_usuario(
                cursor,
                nombre,
                email,
                password,
                imagen if imagen else None,
                bio if bio else None
            )

            if ok:
                conexion.commit()
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

            ok, msg = modificar_usuario(
                cursor,
                int(idu),
                nombre if nombre else None,
                email if email else None,
                password if password else None,
                imagen if imagen else None,
                bio if bio else None
            )

            if ok:
                conexion.commit()
            print(msg)

        # RF4.3 – Eliminar usuario (borrado físico, cascade)
        elif opcion == "3":
            idu = input("ID del usuario a eliminar: ")
            password = input("Contraseña: ")
            confirm = input("¿Está seguro? (S/N): ").upper()

            if confirm == "S":
                ok, msg = eliminar_usuario(cursor, int(idu), password)
                if ok:
                    conexion.commit()
                print(msg)
            else:
                print("Operación cancelada.")

        # RF4.4 – Bloquear / Desbloquear usuario
        elif opcion == "4":
            id1 = input("ID del usuario activo: ")
            id2 = input("ID del usuario a bloquear/desbloquear: ")

            ok, msg = bloquear_desbloquear_usuario(cursor, int(id1), int(id2))
            if ok:
                conexion.commit()
            print(msg)

        # RF4.5 – Añadir amigo
        elif opcion == "5":
            id1 = input("ID del usuario activo: ")
            id2 = input("ID del usuario a añadir como amigo: ")

            ok, msg = anadir_amigo(cursor, int(id1), int(id2))
            if ok:
                conexion.commit()
            print(msg)

        elif opcion == "6":
            print("Saliendo del subsistema de Usuarios...")
            break

        else:
            print("Opción no válida. Intente de nuevo.")

    cursor.close()
