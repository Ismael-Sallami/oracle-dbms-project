import oracledb
from auth import login
from functions import crear_usuario
from menu import mostrar_menu_usuarios  
from getpass import getpass


def main():
    try:
        conexion = oracledb.connect(
            user="ORACLE_USER",
            password="ORACLE_USER",
            dsn="oracle0.ugr.es:1521/practbd"
        )
    except Exception as e:
        print(f"Error de conexión: {e}")
        return

    while True:
        print("\n========================================")
        print("        SISTEMA EKIS - ACCESO            ")
        print("========================================")
        print("1. Login")
        print("2. Crear usuario")
        print("3. Salir")
        print("----------------------------------------")

        opcion = input("Seleccione una opción: ").strip()

        # ---------------- LOGIN ----------------
        if opcion == "1":
            email = input("Email: ")
            password = getpass("Contraseña: ")

            ok, res = login(conexion, email, password)
            if ok:
                id_usuario_activo = res
                print(f"\nLogin correcto. IDUSUARIO={id_usuario_activo}")
                mostrar_menu_usuarios(conexion, id_usuario_activo)
            else:
                print(f"\n {res}")

        # ------------- REGISTRO ----------------
        elif opcion == "2":
            nombre = input("Nombre de usuario: ")
            email = input("Email: ")
            password = getpass("Contraseña: ")
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

        # ---------------- SALIR ----------------
        elif opcion == "3":
            print("Saliendo del sistema...")
            break

        else:
            print("Opción no válida.")

    conexion.close()


if __name__ == "__main__":
    main()