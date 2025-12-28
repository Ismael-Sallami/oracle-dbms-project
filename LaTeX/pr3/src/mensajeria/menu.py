import customtkinter as ctk
from tkinter import messagebox
from mensajeria import functions

class VentanaMensajeria(ctk.CTkFrame):
    def __init__(self, master, conn, id_usuario_actual):
        super().__init__(master)
        self.conn = conn
        self.id_usuario_actual = id_usuario_actual
        self.viendo_archivados = False

        self.lbl_titulo = ctk.CTkLabel(self, text="MENSAJERÍA PRIVADA", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=15)

        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.pack(fill="x", padx=20, pady=5)

        self.btn_toggle = ctk.CTkButton(self.frame_top, text="Ver Archivados", 
                                        fg_color="#5D6D7E", command=self.toggle_archivados)
        self.btn_toggle.pack(side="left", padx=10, pady=10)
        
        self.lbl_estado = ctk.CTkLabel(self.frame_top, text="Contactos Activos", font=("Arial", 14, "italic"))
        self.lbl_estado.pack(side="right", padx=20)

        self.scroll_usuarios = ctk.CTkScrollableFrame(self, label_text="Selecciona un contacto para chatear")
        self.scroll_usuarios.pack(fill="both", expand=True, padx=20, pady=10)

        self.cargar_usuarios()

    def limpiar_lista(self):
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()

    def cargar_usuarios(self):
        self.limpiar_lista()
        try:
            usuarios = functions.listar_usuarios(self.conn, self.id_usuario_actual, self.viendo_archivados)
            if not usuarios:
                lbl = ctk.CTkLabel(self.scroll_usuarios, text="No hay contactos aquí.")
                lbl.pack(pady=20)
                return

            for uid, nombre in usuarios:
                fila = ctk.CTkFrame(self.scroll_usuarios, fg_color="transparent")
                fila.pack(fill="x", pady=2)

                btn_user = ctk.CTkButton(fila, text=f"👤 {nombre} (ID: {uid})", 
                                         anchor="w",
                                         fg_color=("#E5E7E9", "#2E4053"),
                                         text_color=("black", "white"),
                                         hover_color="#3498DB",
                                         command=lambda u=uid, n=nombre: self.abrir_chat(u, n))
                btn_user.pack(side="left", fill="x", expand=True, padx=(0, 5))

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
        exito, msg = functions.des_archivar_usuario(self.conn, self.id_usuario_actual, id_destino)
        if exito:
            self.cargar_usuarios() 

    def abrir_chat(self, id_destino, nombre_destino):
        VentanaChat(self, self.conn, self.id_usuario_actual, id_destino, nombre_destino)


class VentanaChat(ctk.CTkToplevel):
    def __init__(self, parent, conn, id_origen, id_destino, nombre_destino):
        super().__init__(parent)
        self.conn = conn
        self.id_origen = id_origen
        self.id_destino = id_destino
        
        # --- ESTADO DE SELECCIÓN ---
        self.modo_seleccion = False
        self.seleccionados = set() # Aquí guardaremos los IDs de los mensajes a borrar

        self.title(f"Chat con {nombre_destino}")
        self.geometry("500x650")
        self.attributes("-topmost", True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # El frame de mensajes ocupa el centro

        # --- PANEL SUPERIOR (Acciones) ---
        self.frame_top_acciones = ctk.CTkFrame(self)
        self.frame_top_acciones.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")

        self.btn_modo = ctk.CTkButton(self.frame_top_acciones, text="Seleccionar Mensajes", 
                                      fg_color="#5D6D7E", command=self.toggle_modo_seleccion)
        self.btn_modo.pack(side="left", padx=10, pady=10)

        # Estos botones solo se ven en modo selección
        self.btn_confirmar = ctk.CTkButton(self.frame_top_acciones, text="Eliminar (0)", 
                                           fg_color="#E74C3C", command=self.ejecutar_borrado_multiple)
        
        self.btn_cancelar = ctk.CTkButton(self.frame_top_acciones, text="Cancelar", 
                                          fg_color="#95A5A6", command=self.toggle_modo_seleccion)

        # --- ÁREA DE MENSAJES ---
        self.frame_mensajes = ctk.CTkScrollableFrame(self, label_text=f"Conversación con {nombre_destino}")
        self.frame_mensajes.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # --- ÁREA DE ENTRADA ---
        self.entry_msj = ctk.CTkEntry(self, placeholder_text="Escribe un mensaje...")
        self.entry_msj.grid(row=2, column=0, padx=(20, 10), pady=20, sticky="ew")
        self.entry_msj.bind("<Return>", lambda e: self.enviar())

        self.btn_enviar = ctk.CTkButton(self, text="Enviar", width=100, command=self.enviar)
        self.btn_enviar.grid(row=2, column=1, padx=(10, 20), pady=20)

        self.cargar_mensajes()

    def toggle_modo_seleccion(self):
        self.modo_seleccion = not self.modo_seleccion
        self.seleccionados.clear()
        
        if self.modo_seleccion:
            self.btn_modo.pack_forget() # Ocultamos botón principal
            self.btn_confirmar.pack(side="left", padx=10, pady=10)
            self.btn_confirmar.configure(text="Eliminar (0)", state="disabled")
            self.btn_cancelar.pack(side="right", padx=10, pady=10)
            self.btn_enviar.configure(state="disabled")
            self.entry_msj.configure(state="disabled")
        else:
            self.btn_confirmar.pack_forget()
            self.btn_cancelar.pack_forget()
            self.btn_modo.pack(side="left", padx=10, pady=10)
            self.btn_enviar.configure(state="normal")
            self.entry_msj.configure(state="normal")
        
        self.cargar_mensajes()

    def cargar_mensajes(self):
        for widget in self.frame_mensajes.winfo_children():
            widget.destroy()

        try:
            mensajes = functions.visualizar_conversacion(self.conn, self.id_origen, self.id_destino)
            for id_msj, id_remit, nombre, texto in mensajes:
                fila_msj = ctk.CTkFrame(self.frame_mensajes, fg_color="transparent")
                fila_msj.pack(fill="x", pady=5, padx=5)

                if int(id_remit) == int(self.id_origen):
                    # --- MENSAJE PROPIO ---
                    if self.modo_seleccion:
                        cb = ctk.CTkCheckBox(fila_msj, text="", width=20,
                                             command=lambda mid=id_msj: self.actualizar_conteo(mid))
                        cb.pack(side="right", padx=(5, 0))

                    lbl = ctk.CTkLabel(fila_msj, text=f"TÚ:\n{texto}", 
                                       fg_color="#2E86C1", corner_radius=10, 
                                       padx=10, pady=5, justify="right")
                    lbl.pack(side="right")
                else:
                    # --- MENSAJE RECIBIDO ---
                    lbl = ctk.CTkLabel(fila_msj, text=f"{nombre}:\n{texto}", 
                                       fg_color="#5D6D7E", corner_radius=10, 
                                       padx=10, pady=5, justify="left")
                    lbl.pack(side="left")
            
            self.frame_mensajes._parent_canvas.yview_moveto(1.0)
        except Exception as e:
            print(f"Error al cargar mensajes: {e}")

    def actualizar_conteo(self, id_mensaje):
        if id_mensaje in self.seleccionados:
            self.seleccionados.remove(id_mensaje)
        else:
            self.seleccionados.add(id_mensaje)
        
        cant = len(self.seleccionados)
        self.btn_confirmar.configure(text=f"Eliminar ({cant})", 
                                     state="normal" if cant > 0 else "disabled")

    def ejecutar_borrado_multiple(self):
        cant = len(self.seleccionados)
        if messagebox.askyesno("Borrar", f"¿Seguro que quieres borrar {cant} mensajes?"):
            for mid in self.seleccionados:
                functions.eliminar_mensaje(self.conn, self.id_origen, mid)
            
            self.toggle_modo_seleccion() # Refresca y sale del modo

    def enviar(self):
        texto = self.entry_msj.get().strip()
        if texto:
            exito, _ = functions.enviar_mensaje(self.conn, self.id_origen, self.id_destino, texto)
            if exito:
                self.entry_msj.delete(0, "end")
                self.cargar_mensajes()