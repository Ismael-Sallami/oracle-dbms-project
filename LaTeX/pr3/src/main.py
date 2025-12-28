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
# from usuarios import menu as usuarios_sys
# from publicaciones import menu as publicaciones_sys
# from tendencias import menu as tendencias_sys
# from mensajeria import menu as mensajeria_sys

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

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

    def salir(self):
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()