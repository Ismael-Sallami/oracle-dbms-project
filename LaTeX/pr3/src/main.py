# import sys
# from db_connection import DBConnection

# # --- IMPORTACIÓN DE SUBSISTEMAS ---
# # Descomentar a medida que los compañeros suban su código
# from publicidad import menu as publicidad_sys
# # from usuarios import menu as usuarios_sys
# # from publicaciones import menu as publicaciones_sys
# # from tendencias import menu as tendencias_sys
# # from mensajeria import menu as mensajeria_sys

# def main():
#     # 1. Iniciar conexión ÚNICA
#     db = DBConnection()
#     conn = db.connect()
    
#     if not conn:
#         print("Saliendo del sistema...")
#         sys.exit(1)

#     # 2. Bucle del Menú Principal
#     while True:
#         print("\n========================================")
#         print("      SISTEMA DE INFORMACIÓN EKIS       ")
#         print("========================================")
#         print("1. Gestión de Publicidad (Ismael)")
#         print("2. Gestión de Usuarios (Fer)")
#         print("3. Gestión de Publicaciones (Javi)")
#         print("4. Gestión de Tendencias (Jesús)")
#         print("5. Mensajería Privada (Sergio)")
#         print("0. Salir")
#         print("========================================")
        
#         opcion = input("Seleccione una opción: ")

#         if opcion == "1":
#             publicidad_sys.mostrar_menu(conn)
#         elif opcion == "2":
#             print("⚠️ Módulo en desarrollo (Fer)")
#             # usuarios_sys.mostrar_menu(conn)
#         elif opcion == "3":
#             print("⚠️ Módulo en desarrollo (Javi)")
#         elif opcion == "4":
#             print("⚠️ Módulo en desarrollo (Jesús)")
#         elif opcion == "5":
#             print("⚠️ Módulo en desarrollo (Sergio)")
#         elif opcion == "0":
#             db.close()
#             print("¡Hasta luego!")
#             break
#         else:
#             print("Opción no válida.")

#     if conn:
#         db.close() 

# if __name__ == "__main__":
#     main()

import customtkinter as ctk
from db_connection import DBConnection
import sys

# Importamos los módulos (Aquí irán los de tus compañeros también)
from publicidad.menu import VentanaPublicidad
from publicaciones.menu import VentanaPublicaciones
from tendencias.menu import VentanaTendencias
from usuarios.functions import crear_usuario
from usuarios.menu import VentanaUsuario
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
import customtkinter as ctk
from usuarios.auth import login

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, conn, on_login_ok):
        super().__init__(master)
        self.conn = conn
        self.on_login_ok = on_login_ok
        self.registro_activo = False

        self.grid_columnconfigure(0, weight=1)

        # ---------- TÍTULO ----------
        self.titulo = ctk.CTkLabel(
            self, text="EKIS - Acceso",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.titulo.grid(row=0, column=0, pady=(40, 20))

        # ---------- LOGIN ----------
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=320)
        self.email_entry.grid(row=1, column=0, pady=10)

        self.pass_entry = ctk.CTkEntry(
            self, placeholder_text="Contraseña", show="*", width=320
        )
        self.pass_entry.grid(row=2, column=0, pady=10)

        # ---------- REGISTRO (ocultos al inicio) ----------
        self.nombre_entry = ctk.CTkEntry(
            self, placeholder_text="Nombre de usuario", width=320
        )
        self.email_reg_entry = ctk.CTkEntry(
            self, placeholder_text="Email", width=320
        )
        self.pass_reg_entry = ctk.CTkEntry(
            self, placeholder_text="Contraseña", show="*", width=320
        )

        # ---------- MENSAJES ----------
        self.msg = ctk.CTkLabel(self, text="", text_color="tomato")
        self.msg.grid(row=4, column=0, pady=(5, 10))

        # ---------- BOTÓN PRINCIPAL ----------
        self.btn_principal = ctk.CTkButton(
            self, text="Entrar", width=320, command=self.accion_principal
        )
        self.btn_principal.grid(row=5, column=0, pady=10)

        # ---------- BOTÓN CAMBIO MODO ----------
        self.btn_cambiar = ctk.CTkButton(
            self,
            text="Crear cuenta",
            fg_color="gray",
            hover_color="#555555",
            width=320,
            command=self.toggle_registro
        )
        self.btn_cambiar.grid(row=6, column=0, pady=(5, 30))

        # Enter = acción principal
        self.pass_entry.bind("<Return>", lambda e: self.accion_principal())
        self.pass_reg_entry.bind("<Return>", lambda e: self.accion_principal())

    # ======================================================
    # CAMBIAR ENTRE LOGIN / REGISTRO
    # ======================================================
    def toggle_registro(self):
        self.msg.configure(text="")

        if not self.registro_activo:
            # Ocultar login
            self.email_entry.grid_remove()
            self.pass_entry.grid_remove()

            # Mostrar registro
            self.nombre_entry.grid(row=1, column=0, pady=10)
            self.email_reg_entry.grid(row=2, column=0, pady=10)
            self.pass_reg_entry.grid(row=3, column=0, pady=10)

            self.titulo.configure(text="EKIS - Registro")
            self.btn_principal.configure(text="Crear usuario")
            self.btn_cambiar.configure(text="Volver a login")

            self.registro_activo = True
        else:
            # Volver a login
            self.nombre_entry.grid_remove()
            self.email_reg_entry.grid_remove()
            self.pass_reg_entry.grid_remove()

            self.email_entry.grid(row=1, column=0, pady=10)
            self.pass_entry.grid(row=2, column=0, pady=10)

            self.titulo.configure(text="EKIS - Acceso")
            self.btn_principal.configure(text="Entrar")
            self.btn_cambiar.configure(text="Crear cuenta")

            self.registro_activo = False

    # ======================================================
    # ACCIÓN PRINCIPAL (LOGIN O REGISTRO)
    # ======================================================
    def accion_principal(self):
        if self.registro_activo:
            self.crear_usuario_gui()
        else:
            self.login_gui()

    # ---------------- LOGIN ----------------
    def login_gui(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get()

        if not email or not password:
            self.msg.configure(text="Complete email y contraseña.")
            return

        ok, res = login(self.conn, email, password)
        if not ok:
            self.msg.configure(text=str(res))
            return

        self.msg.configure(text="")
        self.on_login_ok(res)  # id_usuario

    # ---------------- REGISTRO ----------------
    def crear_usuario_gui(self):
        nombre = self.nombre_entry.get().strip()
        email = self.email_reg_entry.get().strip()
        password = self.pass_reg_entry.get()

        if not nombre or not email or not password:
            self.msg.configure(text="Complete todos los campos.")
            return

        msg = crear_usuario(self.conn, nombre, email, password)

        if "creado" in msg.lower():
            self.msg.configure(
                text="Usuario creado. Inicie sesión.",
                text_color="green"
            )
            self.toggle_registro()
        else:
            self.msg.configure(text=msg)
       


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema EKIS - Práctica 3")
        self.geometry("900x600")

        # Conexión DB
        self.db = DBConnection()
        self.conn = self.db.connect()
        if not self.conn:
            print("❌ Error fatal: No hay conexión a Oracle.")
            sys.exit(1)

        # Estado de sesión
        self.id_usuario_activo = None

        # Contenedor único (para cambiar de pantalla)
        self.root_frame = ctk.CTkFrame(self)
        self.root_frame.pack(fill="both", expand=True)

        # Pantalla inicial: Login
        self.mostrar_login()

    def limpiar_root(self):
        for widget in self.root_frame.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_root()
        login_frame = LoginFrame(self.root_frame, self.conn, self.on_login_ok)
        login_frame.pack(fill="both", expand=True)

    def on_login_ok(self, id_usuario):
        self.id_usuario_activo = id_usuario
        self.mostrar_dashboard()
        self.mostrar_home()

    def mostrar_dashboard(self):
        self.limpiar_root()

        # Layout Principal (Grid 2 columnas)
        self.root_frame.grid_columnconfigure(1, weight=1)
        self.root_frame.grid_rowconfigure(0, weight=1)

        # --- BARRA LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self.root_frame, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"EKIS\nUsuario ID: {self.id_usuario_activo}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="Inicio", command=self.mostrar_home)
        self.btn_home.grid(row=1, column=0, padx=20, pady=10)

        self.btn_publicidad = ctk.CTkButton(self.sidebar_frame, text="Publicidad", command=self.mostrar_publicidad)
        self.btn_publicidad.grid(row=2, column=0, padx=20, pady=10)

        self.btn_publicaciones = ctk.CTkButton(self.sidebar_frame, text="Publicaciones", command=self.mostrar_publicaciones)
        self.btn_publicaciones.grid(row=3, column=0, padx=20, pady=10)

        self.btn_tendencias = ctk.CTkButton(self.sidebar_frame, text="Tendencias", command=self.mostrar_tendencias)
        self.btn_tendencias.grid(row=4, column=0, padx=20, pady=10)

        self.btn_usuarios = ctk.CTkButton(self.sidebar_frame, text="Usuarios", command=self.mostrar_menu_usuarios)
        self.btn_usuarios.grid(row=5, column=0, padx=20, pady=10)

        # Logout
        self.btn_logout = ctk.CTkButton(self.sidebar_frame, text="Cerrar sesión", command=self.cerrar_sesion)
        self.btn_logout.grid(row=6, column=0, padx=20, pady=10)

        self.btn_salir = ctk.CTkButton(self.sidebar_frame, text="Salir", fg_color="red", command=self.salir)
        self.btn_salir.grid(row=8, column=0, padx=20, pady=20)

        # --- CONTENIDO ---
        self.frame_contenido = ctk.CTkFrame(self.root_frame)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.mostrar_home()

    def limpiar_panel(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def mostrar_home(self):
        self.limpiar_panel()
        lbl = ctk.CTkLabel(self.frame_contenido, text="Bienvenido a EKIS", font=("Arial", 30))
        lbl.pack(pady=80)
        lbl2 = ctk.CTkLabel(self.frame_contenido, text="Selecciona un módulo en el menú lateral.")
        lbl2.pack()

    def mostrar_publicidad(self):
        self.limpiar_panel()
        ventana_pub = VentanaPublicidad(self.frame_contenido, self.conn)
        ventana_pub.pack(fill="both", expand=True)

    def mostrar_publicaciones(self):
        self.limpiar_panel()
        ventana_publicaciones = VentanaPublicaciones(self.frame_contenido, self.conn)
        ventana_publicaciones.pack(fill="both", expand=True)

    def mostrar_tendencias(self):
        self.limpiar_panel()
        ventana_tendencias = VentanaTendencias(self.frame_contenido, self.conn)
        ventana_tendencias.pack(fill="both", expand=True)
    def mostrar_menu_usuarios(self):
        self.limpiar_panel()
        view = VentanaUsuario(self.frame_contenido, self.conn, self.id_usuario_activo, on_user_deleted=self.cerrar_sesion)
        view.pack(fill="both", expand=True)

    def cerrar_sesion(self):
        self.id_usuario_activo = None
        self.mostrar_login()

    def salir(self):
        self.db.close()
        self.destroy()





'''
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Configuración de la Ventana Principal
        self.title("Sistema EKIS - Práctica 3")
        self.geometry("900x600")

        # 2. Conexión a Base de Datos
        self.db = DBConnection()
        self.conn = self.db.connect()
        if not self.conn:
            print("❌ Error fatal: No hay conexión a Oracle.")
            sys.exit(1)

        # 3. Layout Principal (Grid 2 columnas: Menú izquierda, Contenido derecha)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- BARRA LATERAL (Menú) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="EKIS DB\nDashboard", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones del Menú
        self.btn_home = ctk.CTkButton(self.sidebar_frame, text="Inicio", command=self.mostrar_home)
        self.btn_home.grid(row=1, column=0, padx=20, pady=10)

        self.btn_publicidad = ctk.CTkButton(self.sidebar_frame, text="Publicidad", command=self.mostrar_publicidad)
        self.btn_publicidad.grid(row=2, column=0, padx=20, pady=10)

        self.btn_publicaciones = ctk.CTkButton(self.sidebar_frame, text="Publicaciones", command=self.mostrar_publicaciones)
        self.btn_publicaciones.grid(row=3, column=0, padx=20, pady=10)

        self.btn_tendencias = ctk.CTkButton(self.sidebar_frame, text="Tendencias", command=self.mostrar_tendencias)
        self.btn_tendencias.grid(row=4, column=0, padx=20, pady=10)
        
        # Aquí añadirías los botones de Fer, Javi, etc...
        # self.btn_usuarios = ...

        self.btn_salir = ctk.CTkButton(self.sidebar_frame, text="Salir / Desconectar", fg_color="red", command=self.salir)
        self.btn_salir.grid(row=7, column=0, padx=20, pady=20)

        # --- ÁREA DE CONTENIDO (Derecha) ---
        self.frame_contenido = ctk.CTkFrame(self)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Cargar pantalla inicial
        self.mostrar_home()

    def limpiar_panel(self):
        # Borra lo que haya en el panel derecho
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def mostrar_home(self):
        self.limpiar_panel()
        lbl = ctk.CTkLabel(self.frame_contenido, text="Bienvenido al Sistema EKIS", font=("Arial", 30))
        lbl.pack(pady=100)
        lbl2 = ctk.CTkLabel(self.frame_contenido, text="Selecciona un módulo en el menú lateral.")
        lbl2.pack()

    def mostrar_publicidad(self):
        self.limpiar_panel()
        # Instanciamos TU clase de publicidad dentro del panel derecho
        ventana_pub = VentanaPublicidad(self.frame_contenido, self.conn)
        ventana_pub.pack(fill="both", expand=True)

    def mostrar_publicaciones(self):
        self.limpiar_panel()
        ventana_publicaciones = VentanaPublicaciones(self.frame_contenido,self.conn)
        ventana_publicaciones.pack(fill="both", expand=True)

    def mostrar_tendencias(self):
        self.limpiar_panel()
        ventana_tendencias = VentanaTendencias(self.frame_contenido,self.conn)
        ventana_tendencias.pack(fill="both", expand=True)


    def salir(self):
        self.db.close()
        self.destroy()
'''
if __name__ == "__main__":
    app = App()
    app.mainloop()