from .functions import (
    crear_usuario,
    modificar_usuario,
    eliminar_usuario,
    bloquear_desbloquear_usuario,
    anadir_amigo
)
import customtkinter as ctk
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


class VentanaUsuario(ctk.CTkFrame):
    def __init__(self, master, conn, id_usuario_activo, on_user_deleted=None):
        super().__init__(master)
        self.conn = conn
        self.id_usuario_activo = id_usuario_activo
        self.on_user_deleted = on_user_deleted  # callback opcional (logout si se borra)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text=f"Menú Usuarios (ID {self.id_usuario_activo})",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.grid(row=0, column=0, columnspan=2, pady=(10, 15))

        # Mensajes de estado
        self.msg = ctk.CTkLabel(self, text="", text_color="tomato")
        self.msg.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # ---------------------------
        # SECCIÓN: MODIFICAR MI USUARIO
        # ---------------------------
        box1 = ctk.CTkFrame(self)
        box1.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        box1.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(box1, text="Modificar mi usuario", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=(10, 10))

        self.ent_nombre = ctk.CTkEntry(box1, placeholder_text="Nuevo nombre (vacío = igual)")
        self.ent_nombre.grid(row=1, column=0, padx=10, pady=6, sticky="ew")

        self.ent_email = ctk.CTkEntry(box1, placeholder_text="Nuevo email (vacío = igual)")
        self.ent_email.grid(row=2, column=0, padx=10, pady=6, sticky="ew")

        self.ent_pass = ctk.CTkEntry(box1, placeholder_text="Nueva contraseña (vacío = igual)", show="*")
        self.ent_pass.grid(row=3, column=0, padx=10, pady=6, sticky="ew")

        self.ent_imagen = ctk.CTkEntry(box1, placeholder_text="Nueva imagen (vacío = igual)")
        self.ent_imagen.grid(row=4, column=0, padx=10, pady=6, sticky="ew")

        self.ent_bio = ctk.CTkEntry(box1, placeholder_text="Nueva bio (vacío = igual)")
        self.ent_bio.grid(row=5, column=0, padx=10, pady=6, sticky="ew")

        btn_mod = ctk.CTkButton(box1, text="Guardar cambios", command=self._modificar_mi_usuario)
        btn_mod.grid(row=6, column=0, padx=10, pady=(10, 12), sticky="ew")

        # ---------------------------
        # SECCIÓN: ACCIONES SOCIALES (bloquear / añadir)
        # ---------------------------
        box2 = ctk.CTkFrame(self)
        box2.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        box2.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(box2, text="Acciones", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=(10, 10))

        self.ent_id_otro = ctk.CTkEntry(box2, placeholder_text="ID del otro usuario")
        self.ent_id_otro.grid(row=1, column=0, padx=10, pady=6, sticky="ew")

        btn_block = ctk.CTkButton(box2, text="Bloquear / Desbloquear", command=self._bloquear_desbloquear)
        btn_block.grid(row=2, column=0, padx=10, pady=6, sticky="ew")

        btn_friend = ctk.CTkButton(box2, text="Añadir amigo", command=self._anadir_amigo)
        btn_friend.grid(row=3, column=0, padx=10, pady=6, sticky="ew")

        # ---------------------------
        # SECCIÓN: ELIMINAR MI USUARIO (borrado lógico)
        # ---------------------------
        box3 = ctk.CTkFrame(self)
        box3.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        box3.grid_columnconfigure(0, weight=1)
        box3.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(box3, text="Eliminar mi usuario", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 10))

        self.ent_pass_del = ctk.CTkEntry(box3, placeholder_text="Contraseña para confirmar", show="*")
        self.ent_pass_del.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        btn_del = ctk.CTkButton(box3, text="Eliminar (borrado lógico)", fg_color="red", command=self._eliminar_mi_usuario)
        btn_del.grid(row=1, column=1, padx=10, pady=(0, 10))

    # ======================================================
    # Helpers UI
    # ======================================================
    def _set_msg_ok(self, text):
        self.msg.configure(text=text, text_color="green")

    def _set_msg_err(self, text):
        self.msg.configure(text=text, text_color="tomato")

    def _get_optional(self, entry: ctk.CTkEntry):
        v = entry.get().strip()
        return v if v else None

    # ======================================================
    # Acciones
    # ======================================================
    def _modificar_mi_usuario(self):
        nombre = self._get_optional(self.ent_nombre)
        email = self._get_optional(self.ent_email)
        password = self._get_optional(self.ent_pass)
        imagen = self._get_optional(self.ent_imagen)
        bio = self._get_optional(self.ent_bio)

        msg = modificar_usuario(self.conn, self.id_usuario_activo, nombre, email, password, imagen, bio)
        if "Error" in msg or "no" in msg.lower():
            self._set_msg_err(msg)
        else:
            self._set_msg_ok(msg)

    def _bloquear_desbloquear(self):
        raw = self.ent_id_otro.get().strip()
        if not raw.isdigit():
            self._set_msg_err("ID del usuario inválido.")
            return

        id2 = int(raw)
        msg = bloquear_desbloquear_usuario(self.conn, self.id_usuario_activo, id2)
        if "Error" in msg or "no" in msg.lower():
            self._set_msg_err(msg)
        else:
            self._set_msg_ok(msg)

    def _anadir_amigo(self):
        raw = self.ent_id_otro.get().strip()
        if not raw.isdigit():
            self._set_msg_err("ID del usuario inválido.")
            return

        id2 = int(raw)
        msg = anadir_amigo(self.conn, self.id_usuario_activo, id2)
        if "Error" in msg or "no" in msg.lower():
            self._set_msg_err(msg)
        else:
            self._set_msg_ok(msg)

    def _eliminar_mi_usuario(self):
        password = self.ent_pass_del.get()
        if not password or not password.strip():
            self._set_msg_err("Debe introducir la contraseña.")
        
        
            return

        # Confirmación simple (popup)
        dialog = ctk.CTkInputDialog(text="Escriba SI para confirmar eliminación:", title="Confirmación")
        confirm = (dialog.get_input() or "").strip().upper()
        if confirm != "SI":
            self._set_msg_err("Operación cancelada.")
            return

        msg = eliminar_usuario(self.conn, self.id_usuario_activo, password)
        if "Error" in msg or "incorrect" in msg.lower():
            self._set_msg_err(msg)
            return

        self._set_msg_ok(msg)

        # Si se borra, lo normal es cerrar sesión
        if callable(self.on_user_deleted):
            self.on_user_deleted()
        

