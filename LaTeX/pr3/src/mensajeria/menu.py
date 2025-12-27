import customtkinter as ctk
from tkinter import messagebox
from mensajeria import functions

class VentanaMensajeria(ctk.CTkFrame):
    def __init__(self, master, conn):
        super().__init__(master)
        self.conn = conn
        
        # ID fijo por ahora (puedes cambiarlo al de tu usuario de prueba)
        self.id_usuario_activo = 1 
        self.viendo_archivados = False

        # Título
        self.lbl_titulo = ctk.CTkLabel(self, text="MENSAJERÍA PRIVADA", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=15)

        # --- PANEL DE CONTROL ---
        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.pack(fill="x", padx=20, pady=5)

        self.btn_toggle = ctk.CTkButton(self.frame_top, text="Ver Archivados", 
                                        fg_color="#5D6D7E", command=self.toggle_archivados)
        self.btn_toggle.pack(side="left", padx=10, pady=10)
        
        self.lbl_estado = ctk.CTkLabel(self.frame_top, text="Contactos Activos", font=("Arial", 14, "italic"))
        self.lbl_estado.pack(side="right", padx=20)

        # --- LISTA DE CONTACTOS (Scrollable) ---
        # Aquí es donde aparecerán los usuarios como botones
        self.scroll_usuarios = ctk.CTkScrollableFrame(self, label_text="Selecciona un contacto para chatear")
        self.scroll_usuarios.pack(fill="both", expand=True, padx=20, pady=10)

        # Cargar los botones por primera vez
        self.cargar_usuarios()

    def limpiar_lista(self):
        # Elimina los botones anteriores para refrescar la lista
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()

    def cargar_usuarios(self):
        self.limpiar_lista()
        try:
            usuarios = functions.listar_usuarios(self.conn, self.id_usuario_activo, self.viendo_archivados)
            
            if not usuarios:
                lbl = ctk.CTkLabel(self.scroll_usuarios, text="No hay contactos aquí.")
                lbl.pack(pady=20)
                return

            for uid, nombre in usuarios:
                # Creamos un frame para cada fila (Nombre + Botón Archivar)
                fila = ctk.CTkFrame(self.scroll_usuarios, fg_color="transparent")
                fila.pack(fill="x", pady=2)

                # Botón principal para abrir chat
                btn_user = ctk.CTkButton(fila, text=f"👤 {nombre} (ID: {uid})", 
                                         anchor="w",
                                         fg_color=("#E5E7E9", "#2E4053"),
                                         text_color=("black", "white"),
                                         hover_color="#3498DB",
                                         command=lambda u=uid, n=nombre: self.abrir_chat(u, n))
                btn_user.pack(side="left", fill="x", expand=True, padx=(0, 5))

                # Botón pequeño de acción (Archivar/Desarchivar)
                texto_accion = "📦" if not self.viendo_archivados else "📤"
                btn_acc = ctk.CTkButton(fila, text=texto_accion, width=40, 
                                        fg_color="#AAB7B8",
                                        hover_color="#EC7063",
                                        command=lambda u=uid: self.gestionar_archivo(u))
                btn_acc.pack(side="right")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar usuarios: {e}")

    def toggle_archivados(self):
        self.viendo_archivados = not self.viendo_archivados
        self.lbl_estado.configure(text="Contactos Archivados" if self.viendo_archivados else "Contactos Activos")
        self.btn_toggle.configure(text="Ver Activos" if self.viendo_archivados else "Ver Archivados")
        self.cargar_usuarios()

    def gestionar_archivo(self, id_destino):
        # Llama a tu función de base de datos
        exito, msg = functions.des_archivar_usuario(self.conn, self.id_usuario_activo, id_destino)
        if exito:
            self.cargar_usuarios() # Refrescar lista

    def abrir_chat(self, id_destino, nombre_destino):
        # Crea la ventana de chat pasando los datos directamente del botón pulsado
        VentanaChat(self, self.conn, self.id_usuario_activo, id_destino, nombre_destino)


class VentanaChat(ctk.CTkToplevel):
    def __init__(self, parent, conn, id_origen, id_destino, nombre_destino):
        super().__init__(parent)
        self.conn = conn
        self.id_origen = id_origen
        self.id_destino = id_destino
        
        self.title(f"Chat con {nombre_destino}")
        self.geometry("450x550")
        self.attributes("-topmost", True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Área de mensajes
        self.txt_chat = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.txt_chat.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Entrada de texto
        self.entry_msj = ctk.CTkEntry(self, placeholder_text="Escribe un mensaje...")
        self.entry_msj.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")
        self.entry_msj.bind("<Return>", lambda e: self.enviar())

        # Botón enviar
        self.btn_enviar = ctk.CTkButton(self, text="Enviar", width=100, command=self.enviar)
        self.btn_enviar.grid(row=1, column=1, padx=(10, 20), pady=(0, 20))

        self.cargar_mensajes()

    def cargar_mensajes(self):
        try:
            mensajes = functions.visualizar_conversacion(self.conn, self.id_origen, self.id_destino)
            self.txt_chat.configure(state="normal")
            self.txt_chat.delete("0.0", "end")
            
            for _, id_remit, nombre, texto in mensajes:
                remitente = "TÚ" if int(id_remit) == int(self.id_origen) else nombre
                self.txt_chat.insert("end", f" {remitente}:\n {texto}\n\n")
            
            self.txt_chat.configure(state="disabled")
            self.txt_chat.see("end")
        except Exception as e:
            print(f"Error al cargar mensajes: {e}")

    def enviar(self):
        texto = self.entry_msj.get().strip()
        if texto:
            exito, _ = functions.enviar_mensaje(self.conn, self.id_origen, self.id_destino, texto)
            if exito:
                self.entry_msj.delete(0, "end")
                self.cargar_mensajes()
