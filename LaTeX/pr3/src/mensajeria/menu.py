import customtkinter as ctk
from tkinter import messagebox
from mensajeria import functions
from datetime import datetime
from aspectoslegales.functions import enviar_reporte 

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

        self.scroll_usuarios = ctk.CTkScrollableFrame(self, label_text="Contactos")
        self.scroll_usuarios.pack(fill="both", expand=True, padx=20, pady=10)

        self.cargar_usuarios()

    def cargar_usuarios(self):
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()
        try:
            usuarios = functions.listar_usuarios(self.conn, self.id_usuario_actual, self.viendo_archivados)
            
            if not usuarios:
                ctk.CTkLabel(self.scroll_usuarios, text="No hay contactos.").pack(pady=20)
                return

            for uid, nombre, pendientes in usuarios:
                fila = ctk.CTkFrame(self.scroll_usuarios, fg_color="transparent")
                fila.pack(fill="x", pady=2)

                texto_nombre = f"👤 {nombre}"
                color_boton = ("#E5E7E9", "#2E4053") 
                
                if pendientes > 0:
                    texto_nombre += f"  ● {pendientes}"
                    color_boton = ("#AED6F1", "#1F618D") 

                # PASAMOS 'pendientes' A LA FUNCIÓN ABRIR_CHAT
                btn_user = ctk.CTkButton(fila, text=texto_nombre, anchor="w",
                                         fg_color=color_boton, 
                                         text_color=("black", "white"),
                                         command=lambda u=uid, n=nombre, p=pendientes: self.abrir_chat(u, n, p))
                btn_user.pack(side="left", fill="x", expand=True, padx=(0, 5))

                texto_icon = "📦" if not self.viendo_archivados else "📤"
                ctk.CTkButton(fila, text=texto_icon, width=40, fg_color="#AAB7B8",
                              command=lambda u=uid: self.gestionar_archivo(u)).pack(side="right")
                              
        except Exception as e:
            print(f"Error al cargar lista de usuarios: {e}")

    def toggle_archivados(self):
        self.viendo_archivados = not self.viendo_archivados
        self.lbl_estado.configure(text="Archivados" if self.viendo_archivados else "Activos")
        self.cargar_usuarios()

    def gestionar_archivo(self, id_destino):
        functions.des_archivar_usuario(self.conn, self.id_usuario_actual, id_destino)
        self.cargar_usuarios() 

    def abrir_chat(self, id_destino, nombre_destino, pendientes=0):
        VentanaChat(self, self.conn, self.id_usuario_actual, id_destino, nombre_destino, pendientes)
        self.cargar_usuarios()


class VentanaChat(ctk.CTkToplevel):
    def __init__(self, parent, conn, id_origen, id_destino, nombre_destino, pendientes=0):
        super().__init__(parent)
        self.conn = conn
        self.id_origen = id_origen
        self.id_destino = id_destino
        self.mensajes_nuevos_count = pendientes # Guardamos cuántos mensajes separar
        
        self.ICONO_BANDERA = "!"
        self.MAX_CHARS_INPUT = 300 
        self.modo_seleccion = False
        self.modo_reporte = False 
        self.seleccionados = set()
        self.ultima_fecha_cargada = None
        self.separador_visto = False 
        self.lista_checkboxes = [] 
        self.lista_btn_reporte = [] 

        self.title(f"Chat con {nombre_destino}")
        self.geometry("600x720")
        self.attributes("-topmost", True)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.btn_modo = ctk.CTkButton(self.frame_top, text="Borrar Mensajes", 
                                      fg_color="#5D6D7E", command=self.toggle_modo_seleccion)
        self.btn_modo.pack(side="left", padx=10, pady=10)

        self.btn_reporte_toggle = ctk.CTkButton(self.frame_top, text="Reportar", 
                                               width=100, fg_color="#A04000", command=self.toggle_modo_reporte)
        self.btn_reporte_toggle.pack(side="right", padx=10, pady=10)

        self.btn_confirmar = ctk.CTkButton(self.frame_top, text="Eliminar (0)", 
                                           fg_color="#E74C3C", command=self.ejecutar_borrado_multiple)
        self.btn_cancelar = ctk.CTkButton(self.frame_top, text="Cancelar", 
                                          fg_color="#95A5A6", command=self.toggle_modo_seleccion)

        self.frame_mensajes = ctk.CTkScrollableFrame(self, label_text=f"{nombre_destino}")
        self.frame_mensajes.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.frame_input = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_input.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.frame_input.columnconfigure(0, weight=1)

        self.lbl_contador = ctk.CTkLabel(self.frame_input, text=f"0 / {self.MAX_CHARS_INPUT}", font=("Arial", 10))
        self.lbl_contador.grid(row=1, column=0, sticky="e", padx=(0, 95))

        vcmd = (self.register(self.validar_longitud), '%P')
        self.entry_msj = ctk.CTkEntry(self.frame_input, placeholder_text="Escribe...", 
                                      validate="key", validatecommand=vcmd)
        self.entry_msj.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_msj.bind("<Return>", lambda e: self.enviar())

        self.btn_enviar = ctk.CTkButton(self.frame_input, text="Enviar", width=80, command=self.enviar)
        self.btn_enviar.grid(row=0, column=1)

        self.cargar_mensajes()

    def insertar_burbuja(self, id_msj, id_remit, texto, fecha_raw, es_nuevo=False):
        f_obj = fecha_raw if isinstance(fecha_raw, datetime) else datetime.now()
        fecha_str = f_obj.strftime("%d/%m/%Y")
        hora_str = f_obj.strftime("%H:%M")

        if fecha_str != self.ultima_fecha_cargada:
            ctk.CTkLabel(self.frame_mensajes, text=f"— {fecha_str} —", 
                         text_color="gray", font=("Arial", 11, "bold")).pack(pady=10)
            self.ultima_fecha_cargada = fecha_str

        # SEPARADOR DE MENSAJES SIN LEER (Basado en el flag es_nuevo)
        if es_nuevo and not self.separador_visto:
            ctk.CTkLabel(self.frame_mensajes, text="— MENSAJES SIN LEER —", 
                         text_color="green", font=("Arial", 11, "bold")).pack(pady=10)
            self.separador_visto = True

        fila = ctk.CTkFrame(self.frame_mensajes, fg_color="transparent")
        fila.pack(fill="x", pady=2)
        fila.columnconfigure(0, weight=0)
        fila.columnconfigure(1, weight=1)
        fila.columnconfigure(2, weight=0)

        es_mio = int(id_remit) == int(self.id_origen)

        burbuja = ctk.CTkFrame(fila, fg_color="#2E86C1" if es_mio else "#515A5A", corner_radius=12)
        burbuja.grid(row=0, column=1, padx=5, sticky="e" if es_mio else "w")
        
        lbl = ctk.CTkLabel(burbuja, text=texto, padx=12, pady=6, 
                           wraplength=280, justify="left", anchor="w")
        lbl.pack(fill="both", expand=True)

        if not es_mio and id_msj:
            btn_rep = ctk.CTkButton(fila, text=self.ICONO_BANDERA, width=35, fg_color="#E67E22", hover_color="#A04000",
                                   command=lambda mid=id_msj, t=texto: self.confirmar_reporte(mid, t))
            self.lista_btn_reporte.append(btn_rep)
            if self.modo_reporte:
                btn_rep.grid(row=0, column=0, padx=(10, 5))

        if es_mio and id_msj:
            cb = ctk.CTkCheckBox(fila, text="", width=20, 
                                 command=lambda mid=id_msj: self.actualizar_conteo(mid))
            self.lista_checkboxes.append(cb)
            if self.modo_seleccion:
                cb.grid(row=0, column=2, padx=(5, 15))

        ctk.CTkLabel(fila, text=hora_str, font=("Arial", 8), 
                     text_color="gray").grid(row=1, column=1, sticky="e" if es_mio else "w", padx=10)

    def toggle_modo_reporte(self):
        self.modo_reporte = not self.modo_reporte
        if self.modo_reporte and self.modo_seleccion:
            self.toggle_modo_seleccion()

        texto_btn = "Reportar" if not self.modo_reporte else "Cancelar"
        self.btn_reporte_toggle.configure(text=texto_btn,
                                         fg_color="#A04000" if not self.modo_reporte else "#273746")
        for btn in self.lista_btn_reporte:
            if self.modo_reporte:
                btn.grid(row=0, column=0, padx=(10, 5))
            else:
                btn.grid_forget()

    def confirmar_reporte(self, id_mensaje, texto_cifrado):
        if messagebox.askyesno("Reportar", "¿Deseas denunciar este mensaje?", parent=self):
            diag = ctk.CTkInputDialog(text="Motivo de la denuncia:", title="Reportar")
            motivo = diag.get_input()
            if motivo:
                if enviar_reporte(self.conn, id_mensaje, 'MENSAJE', self.id_destino, motivo, texto_cifrado):
                    messagebox.showinfo("Enviado", "El reporte ha sido enviado con éxito.", parent=self)
                    self.toggle_modo_reporte()
                else:
                    messagebox.showerror("Error", "No se pudo procesar el reporte.", parent=self)

    def toggle_modo_seleccion(self):
        self.modo_seleccion = not self.modo_seleccion
        if self.modo_seleccion and self.modo_reporte:
            self.toggle_modo_reporte()
        self.seleccionados.clear()
        self.btn_confirmar.configure(text="Eliminar (0)", state="disabled")
        
        if self.modo_seleccion:
            self.btn_modo.pack_forget()
            self.btn_confirmar.pack(side="left", padx=10)
            self.btn_cancelar.pack(side="right", padx=10)
            for cb in self.lista_checkboxes:
                cb.grid(row=0, column=2, padx=(5, 15))
        else:
            self.btn_confirmar.pack_forget()
            self.btn_cancelar.pack_forget()
            self.btn_modo.pack(side="left", padx=10, pady=10)
            for cb in self.lista_checkboxes:
                cb.grid_forget()
                cb.deselect()

    def cargar_mensajes(self):
        for widget in self.frame_mensajes.winfo_children():
            widget.destroy()
        self.lista_checkboxes.clear()
        self.lista_btn_reporte.clear()
        self.ultima_fecha_cargada = None
        self.separador_visto = False 
        try:
            mensajes = functions.visualizar_conversacion(self.conn, self.id_origen, self.id_destino)
            
            # Lógica de cálculo de mensajes nuevos
            punto_corte = len(mensajes) - self.mensajes_nuevos_count
            
            for i, m in enumerate(mensajes):
                # Es nuevo si está en el rango final y el remitente no soy yo
                es_nuevo_msj = (i >= punto_corte and self.mensajes_nuevos_count > 0 and int(m[1]) != int(self.id_origen))
                self.insertar_burbuja(m[0], m[1], m[3], m[4], es_nuevo=es_nuevo_msj)
                
            self.after(100, self.bajar_scroll)
        except Exception as e:
            print(f"Error: {e}")

    def ejecutar_borrado_multiple(self):
        if not self.seleccionados: return
        if messagebox.askyesno("Confirmar", f"¿Eliminar {len(self.seleccionados)} mensajes?", parent=self):
            for mid in self.seleccionados:
                functions.eliminar_mensaje(self.conn, self.id_origen, mid)
            self.seleccionados.clear()
            self.toggle_modo_seleccion()
            self.cargar_mensajes()

    def actualizar_conteo(self, id_mensaje):
        if id_mensaje in self.seleccionados:
            self.seleccionados.remove(id_mensaje)
        else:
            self.seleccionados.add(id_mensaje)
        cant = len(self.seleccionados)
        self.btn_confirmar.configure(text=f"Eliminar ({cant})", 
                                     state="normal" if cant > 0 else "disabled")

    def enviar(self):
        texto = self.entry_msj.get().strip()
        if texto:
            exito, err = functions.enviar_mensaje(self.conn, self.id_origen, self.id_destino, texto)
            if exito:
                self.entry_msj.delete(0, "end")
                self.insertar_burbuja(None, self.id_origen, texto, datetime.now())
                self.after(10, self.bajar_scroll)
                if hasattr(self.master, 'cargar_usuarios'):
                    self.master.cargar_usuarios()

    def validar_longitud(self, texto_nuevo):
        if len(texto_nuevo) <= self.MAX_CHARS_INPUT:
            if hasattr(self, 'lbl_contador'):
                self.lbl_contador.configure(text=f"{len(texto_nuevo)} / {self.MAX_CHARS_INPUT}")
            return True
        return False

    def bajar_scroll(self):
        self.frame_mensajes._parent_canvas.yview_moveto(1.0)