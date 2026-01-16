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

#      # 1. Iniciar conexión ÚNICA

#      db = DBConnection()

#      conn = db.connect()

    

#      if not conn:

#          print("Saliendo del sistema...")

#          sys.exit(1)



#      # 2. Bucle del Menú Principal

#      while True:

#          print("\n========================================")

#          print("      SISTEMA DE INFORMACIÓN EKIS       ")

#          print("========================================")

#          print("1. Gestión de Publicidad (Ismael)")

#          print("2. Gestión de Usuarios (Fer)")

#          print("3. Gestión de Publicaciones (Javi)")

#          print("4. Gestión de Tendencias (Jesús)")

#          print("5. Mensajería Privada (Sergio)")

#          print("0. Salir")

#          print("========================================")

        

#          opcion = input("Seleccione una opción: ")



#          if opcion == "1":

#              publicidad_sys.mostrar_menu(conn)

#          elif opcion == "2":

#              print("⚠️ Módulo en desarrollo (Fer)")

#              # usuarios_sys.mostrar_menu(conn)

#          elif opcion == "3":

#              print("⚠️ Módulo en desarrollo (Javi)")

#          elif opcion == "4":

#              print("⚠️ Módulo en desarrollo (Jesús)")

#          elif opcion == "5":

#              print("⚠️ Módulo en desarrollo (Sergio)")

#          elif opcion == "0":

#              db.close()

#              print("¡Hasta luego!")

#              break

#          else:

#              print("Opción no válida.")



#      if conn:

#          db.close() 



# if __name__ == "__main__":

#      main()



import customtkinter as ctk

from db_connection import DBConnection

import sys

import faulthandler



# Habilitar el rastreador de fallos de segmentación

faulthandler.enable()



# --- IMPORTACIÓN DE SUBSISTEMAS ---

from publicidad.menu import VentanaPublicidad

from publicaciones.menu import VentanaPublicaciones

from tendencias.menu import VentanaTendencias

from mensajeria.menu import VentanaMensajeria

from usuarios.functions import crear_usuario

from usuarios.menu import VentanaUsuario

from usuarios.auth import login

from publicidad.functions import es_admin_bd

from aspectoslegales.terminosyservicios import TEXTO_TERMINOS

from aspectoslegales.menu import VentanaReportes



ctk.set_appearance_mode("Dark")

ctk.set_default_color_theme("blue")



class LoginFrame(ctk.CTkFrame):

    def __init__(self, master, conn, on_login_ok):

        super().__init__(master)

        self.conn = conn

        self.on_login_ok = on_login_ok

        self.registro_activo = False

        

        self.grid_columnconfigure(0, weight=1)



        self.titulo = ctk.CTkLabel(

            self, text="EKIS - Acceso",

            font=ctk.CTkFont(size=26, weight="bold")

        )

        self.titulo.grid(row=0, column=0, pady=(40, 20))



        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=320)

        self.email_entry.grid(row=1, column=0, pady=10)



        self.pass_entry = ctk.CTkEntry(

            self, placeholder_text="Contraseña", show="*", width=320

        )

        self.pass_entry.grid(row=2, column=0, pady=10)



        # Widgets de registro (se ocultan inicialmente)

        self.nombre_entry = ctk.CTkEntry(self, placeholder_text="Nombre de usuario", width=320)

        self.email_reg_entry = ctk.CTkEntry(self, placeholder_text="Email", width=320)

        self.pass_reg_entry = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=320)

        

        

        self.frame_legal = ctk.CTkFrame(self, fg_color="transparent")

        self.check_terminos = ctk.CTkCheckBox(

            self.frame_legal, 

            text="He leído y acepto los", 

            width=0,

            command=lambda: self.msg.configure(text="") if self.check_terminos.get() else None

        )

        self.check_terminos.pack(side="left", padx=(0, 2))

        self.label_link = ctk.CTkLabel(

            self.frame_legal, 

            text="Terminos y Condiciones",

            text_color="#1F618D", # Color azul link

            font=ctk.CTkFont(size=12, underline=True),

            cursor="hand2"        # Cambia el cursor a la manita

        )

        self.label_link.pack(side="left")

        

        # Vincular el clic al método que abre la ventana

        self.label_link.bind("<Button-1>", lambda e: self.mostrar_ventana_terminos())



        self.msg = ctk.CTkLabel(self, text="", text_color="tomato")

        self.msg.grid(row=7, column=0, pady=(5, 10))



        self.btn_principal = ctk.CTkButton(self, text="Entrar", width=320, command=self.accion_principal)

        self.btn_principal.grid(row=5, column=0, pady=10)



        self.btn_cambiar = ctk.CTkButton(

            self, text="Crear cuenta", fg_color="gray", hover_color="#555555",

            width=320, command=self.toggle_registro

        )

        self.btn_cambiar.grid(row=6, column=0, pady=(5, 30))



    def toggle_registro(self):

        self.msg.configure(text="")

        if not self.registro_activo:

            self.email_entry.grid_remove()

            self.pass_entry.grid_remove()

            self.nombre_entry.grid(row=1, column=0, pady=10)

            self.email_reg_entry.grid(row=2, column=0, pady=10)

            self.pass_reg_entry.grid(row=3, column=0, pady=10)

            self.frame_legal.grid(row=4, column=0, pady=(10, 0))

            self.btn_principal.configure(text="Crear usuario")

            self.btn_cambiar.configure(text="Volver a login")

            self.registro_activo = True

        else:

            self.nombre_entry.grid_remove()

            self.email_reg_entry.grid_remove()

            self.pass_reg_entry.grid_remove()

            self.frame_legal.grid_remove()

            self.email_entry.grid(row=1, column=0, pady=10)

            self.pass_entry.grid(row=2, column=0, pady=10)

            self.btn_principal.configure(text="Entrar")

            self.btn_cambiar.configure(text="Crear cuenta")

            self.registro_activo = False



    def accion_principal(self):

        if self.registro_activo:

            self.crear_usuario_gui()

        else:

            self.login_gui()



    def login_gui(self):

        email = self.email_entry.get().strip()

        password = self.pass_entry.get()

        if not email or not password:

            self.msg.configure(text="Complete email y contraseña.", text_color="red")

            return

        ok, res = login(self.conn, email, password)

        if not ok:

            self.msg.configure(text=str(res))

            return

        self.on_login_ok(res)



    def crear_usuario_gui(self):

        if not self.check_terminos.get():

            self.msg.configure(text="Debe aceptar los términos y condiciones.", text_color="red")

            return

        msg = crear_usuario(self.conn, self.nombre_entry.get(), self.email_reg_entry.get(), self.pass_reg_entry.get())

        if "creado" in msg.lower():

            self.msg.configure(text="Creado. Inicie sesión.", text_color="green")

            self.toggle_registro()

        else:

            self.msg.configure(text=msg)



    def mostrar_ventana_terminos(self):

        ventana = ctk.CTkToplevel(self)

        ventana.title("Términos")

        ventana.geometry("600x700")

        txt_box = ctk.CTkTextbox(ventana, width=550, height=600)

        txt_box.insert("0.0", TEXTO_TERMINOS)

        txt_box.configure(state="disabled")

        txt_box.pack(padx=20, pady=20)



class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Sistema EKIS - Práctica 3")

        self.geometry("1000x700")



        self.db = DBConnection()

        self.conn = self.db.connect()

        if not self.conn:

            sys.exit(1)



        self.id_usuario_activo = None

        self.root_frame = ctk.CTkFrame(self)

        self.root_frame.pack(fill="both", expand=True)

        self.mostrar_login()



    def limpiar_root(self):

        for widget in self.root_frame.winfo_children():

            widget.destroy()



    def mostrar_login(self):

        self.limpiar_root()

        LoginFrame(self.root_frame, self.conn, self.on_login_ok).pack(fill="both", expand=True)



    def on_login_ok(self, id_usuario):

        self.id_usuario_activo = id_usuario

        self.conn.id_usuario_actual = id_usuario

        self.es_admin = es_admin_bd(self.conn, id_usuario)

        # Usamos after para dejar que el frame de login se destruya totalmente antes de crear el Dashboard

        self.after(100, self.mostrar_dashboard)



    def mostrar_dashboard(self):

        self.limpiar_root()

        

        # Grid para el layout principal

        self.root_frame.grid_columnconfigure(1, weight=1)

        self.root_frame.grid_rowconfigure(0, weight=1)



        self.sidebar_frame = ctk.CTkFrame(self.root_frame, width=200, corner_radius=0)

        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        

        self.frame_contenido = ctk.CTkFrame(self.root_frame)

        self.frame_contenido.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)



        self._crear_widgets_sidebar()



    def _crear_widgets_sidebar(self):

        # Título lateral

        ctk.CTkLabel(self.sidebar_frame, text=f"EKIS\nID: {self.id_usuario_activo}", 

                     font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=20)



        # Botones estáticos (sin bucles complejos para evitar inestabilidad en X11)

        common = {"corner_radius": 0, "width": 160}

        

        ctk.CTkButton(self.sidebar_frame, text="Inicio", command=self.mostrar_home, **common).grid(row=1, column=0, pady=5)

        ctk.CTkButton(self.sidebar_frame, text="Publicidad", command=self.mostrar_publicidad, **common).grid(row=2, column=0, pady=5)

        ctk.CTkButton(self.sidebar_frame, text="Publicaciones", command=self.mostrar_publicaciones, **common).grid(row=3, column=0, pady=5)

        ctk.CTkButton(self.sidebar_frame, text="Tendencias", command=self.mostrar_tendencias, **common).grid(row=4, column=0, pady=5)

        ctk.CTkButton(self.sidebar_frame, text="Usuarios", command=self.mostrar_menu_usuarios, **common).grid(row=5, column=0, pady=5)

        ctk.CTkButton(self.sidebar_frame, text="Mensajería", command=self.mostrar_mensajeria, **common).grid(row=6, column=0, pady=5)



        if self.es_admin:

            ctk.CTkButton(self.sidebar_frame, text="🚩 Reportes", fg_color="#A04000", 

                          command=self.mostrar_reportes, **common).grid(row=7, column=0, pady=5)



        # Empujar botones de abajo hacia el final

        self.sidebar_frame.grid_rowconfigure(8, weight=1)



        ctk.CTkButton(self.sidebar_frame, text="Cerrar sesión", command=self.cerrar_sesion, **common).grid(row=9, column=0, pady=5)

        ctk.CTkButton(self.sidebar_frame, text="Salir", fg_color="#943126", command=self.salir, **common).grid(row=10, column=0, pady=(5, 20))



        self.mostrar_home()



    def limpiar_panel(self):

        for widget in self.frame_contenido.winfo_children():

            widget.destroy()



    def mostrar_home(self):

        self.limpiar_panel()

        ctk.CTkLabel(self.frame_contenido, text="Panel de Control EKIS", font=("Arial", 24)).pack(pady=40)

        ctk.CTkLabel(self.frame_contenido, text="Bienvenido. Selecciona un módulo para comenzar.").pack()



    def mostrar_publicidad(self):

        self.limpiar_panel()

        VentanaPublicidad(self.frame_contenido, self.conn, self.id_usuario_activo, self.es_admin).pack(fill="both", expand=True)



    def mostrar_publicaciones(self):

        self.limpiar_panel()

        VentanaPublicaciones(self.frame_contenido, self.conn, self.id_usuario_activo, self.es_admin).pack(fill="both", expand=True)



    def mostrar_tendencias(self):

        self.limpiar_panel()

        VentanaTendencias(self.frame_contenido, self.conn).pack(fill="both", expand=True)

    

    def mostrar_mensajeria(self):

        self.limpiar_panel()

        VentanaMensajeria(self.frame_contenido, self.conn, self.id_usuario_activo).pack(fill="both", expand=True)



    def mostrar_menu_usuarios(self):

        self.limpiar_panel()

        VentanaUsuario(self.frame_contenido, self.conn, self.id_usuario_activo, on_user_deleted=self.cerrar_sesion).pack(fill="both", expand=True)



    def mostrar_reportes(self):

        self.limpiar_panel()

        VentanaReportes(self.frame_contenido, self.conn).pack(fill="both", expand=True)



    def cerrar_sesion(self):

        self.id_usuario_activo = None

        self.mostrar_login()



    def salir(self):

        self.db.close()

        self.quit()



if __name__ == "__main__":

    app = App()

    app.mainloop()























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
