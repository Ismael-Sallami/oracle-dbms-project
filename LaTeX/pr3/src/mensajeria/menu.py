import customtkinter as ctk
from tkinter import messagebox
from mensajeria import functions
from datetime import datetime
import threading
import time
from aspectoslegales.functions import enviar_reporte 

class VentanaMensajeria(ctk.CTkFrame):
    def __init__(self, master, conn, id_usuario_actual):
        super().__init__(master)
        self.conn = conn
        self.id_usuario_actual = id_usuario_actual
        self.viendo_archivados = False
        self.ejecutando_hilo = True
        self.ultimo_estado_usuarios = None

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
        
        self.thread_usuarios = threading.Thread(target=self.monitorizar_usuarios, daemon=True)
        self.thread_usuarios.start()

    def monitorizar_usuarios(self):
        while self.ejecutando_hilo:
            try:
                usuarios = functions.listar_usuarios(self.conn, self.id_usuario_actual, self.viendo_archivados)
                if usuarios != self.ultimo_estado_usuarios:
                    self.ultimo_estado_usuarios = usuarios
                    self.after(0, self.cargar_usuarios)
                time.sleep(4)
            except:
                break

    def cargar_usuarios(self):
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()
        try:
            usuarios = functions.listar_usuarios(self.conn, self.id_usuario_actual, self.viendo_archivados)
            self.ultimo_estado_usuarios = usuarios
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
                btn_user = ctk.CTkButton(fila, text=texto_nombre, anchor="w",
                                         fg_color=color_boton, text_color=("black", "white"),
                                         command=lambda u=uid, n=nombre, p=pendientes: self.abrir_chat(u, n, p))
                btn_user.pack(side="left", fill="x", expand=True, padx=(0, 5))
                texto_icon = "📦" if not self.viendo_archivados else "📤"
                ctk.CTkButton(fila, text=texto_icon, width=40, fg_color="#AAB7B8",
                              command=lambda u=uid: self.gestionar_archivo(u)).pack(side="right")
        except:
            pass

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

    def destroy(self):
        self.ejecutando_hilo = False
        super().destroy()

class VentanaChat(ctk.CTkToplevel):
    def __init__(self, parent, conn, id_origen, id_destino, nombre_destino, pendientes=0):
        super().__init__(parent)
        self.conn = conn
        self.id_origen = id_origen
        self.id_destino = id_destino
        self.mensajes_nuevos_count = pendientes 
        self.ICONO_BANDERA = "!"
        self.MAX_CHARS_INPUT = 300 
        self.LIMITE_LOTE = 10 
        self.modo_seleccion = False
        self.modo_reporte = False 
        self.seleccionados = set()
        self.ultima_fecha_cargada = None
        self.separador_visto = False 
        self.lista_checkboxes = [] 
        self.lista_btn_reporte = [] 
        self.mensajes_totales = []
        self.indice_superior = 0 
        self.indice_inferior_actual = 0
        self.ejecutando_hilo = True

        self.title(f"Chat con {nombre_destino}")
        self.geometry("600x720")
        self.attributes("-topmost", True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.btn_modo = ctk.CTkButton(self.frame_top, text="Borrar Mensajes", fg_color="#5D6D7E", command=self.toggle_modo_seleccion)
        self.btn_modo.pack(side="left", padx=10, pady=10)
        self.btn_reporte_toggle = ctk.CTkButton(self.frame_top, text="Reportar", width=100, fg_color="#A04000", command=self.toggle_modo_reporte)
        self.btn_reporte_toggle.pack(side="right", padx=10, pady=10)
        self.btn_confirmar = ctk.CTkButton(self.frame_top, text="Eliminar (0)", fg_color="#E74C3C", command=self.ejecutar_borrado_multiple)
        self.btn_cancelar = ctk.CTkButton(self.frame_top, text="Cancelar", fg_color="#95A5A6", command=self.toggle_modo_seleccion)

        self.frame_mensajes = ctk.CTkScrollableFrame(self, label_text=f"{nombre_destino}")
        self.frame_mensajes.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.btn_cargar_mas = ctk.CTkButton(self.frame_mensajes, text="↑ Cargar mensajes antiguos", fg_color="transparent", text_color="#2E86C1", command=self.cargar_mas_antiguos)
        self.btn_cargar_nuevos = ctk.CTkButton(self.frame_mensajes, text="↓ Cargar mensajes más recientes", fg_color="transparent", text_color="#27AE60", command=self.cargar_lote_siguiente)

        self.frame_input = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_input.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.frame_input.columnconfigure(0, weight=1)
        self.lbl_contador = ctk.CTkLabel(self.frame_input, text=f"0 / {self.MAX_CHARS_INPUT}", font=("Arial", 10))
        self.lbl_contador.grid(row=1, column=0, sticky="e", padx=(0, 95))
        vcmd = (self.register(self.validar_longitud), '%P')
        self.entry_msj = ctk.CTkEntry(self.frame_input, placeholder_text="Escribe...", validate="key", validatecommand=vcmd)
        self.entry_msj.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_msj.bind("<Return>", lambda e: self.enviar())
        self.btn_enviar = ctk.CTkButton(self.frame_input, text="Enviar", width=80, command=self.enviar)
        self.btn_enviar.grid(row=0, column=1)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.inicializar_chat_progresivo()
        self.thread_escucha = threading.Thread(target=self.escuchar_mensajes, daemon=True)
        self.thread_escucha.start()

    def escuchar_mensajes(self):
        while self.ejecutando_hilo:
            try:
                raw = functions.visualizar_conversacion(self.conn, self.id_origen, self.id_destino)
                nuevos_datos = sorted(raw, key=lambda x: x[4])
                if len(nuevos_datos) > len(self.mensajes_totales):
                    diff = nuevos_datos[len(self.mensajes_totales):]
                    self.after(0, self.inyectar_tiempo_real, diff)
                    self.mensajes_totales = nuevos_datos
                time.sleep(2)
            except: break

    def inyectar_tiempo_real(self, lista):
        canvas = self.frame_mensajes._parent_canvas
        pos_actual = canvas.yview()[1]
        for m in lista:
            if int(m[1]) != int(self.id_origen):
                self.insertar_burbuja(self.frame_mensajes, m[0], m[1], m[3], m[4])
                if self.indice_inferior_actual >= len(self.mensajes_totales) - len(lista):
                    self.indice_inferior_actual += 1
                if pos_actual >= 0.9: self.bajar_scroll()

    def inicializar_chat_progresivo(self):
        try:
            raw = functions.visualizar_conversacion(self.conn, self.id_origen, self.id_destino)
            self.mensajes_totales = sorted(raw, key=lambda x: x[4])
            total = len(self.mensajes_totales)
            corte = total - self.mensajes_nuevos_count
            if self.mensajes_nuevos_count > self.LIMITE_LOTE:
                self.indice_superior, self.indice_inferior_actual = corte, corte + self.LIMITE_LOTE
            else:
                self.indice_superior, self.indice_inferior_actual = max(0, total - self.LIMITE_LOTE), total
            self.renderizar_vista_inicial()
        except: pass

    def renderizar_vista_inicial(self):
        for w in self.frame_mensajes.winfo_children():
            if w not in [self.btn_cargar_mas, self.btn_cargar_nuevos]: w.destroy()
        self.lista_checkboxes.clear(); self.lista_btn_reporte.clear(); self.ultima_fecha_cargada = None; self.separador_visto = False 
        if self.indice_superior > 0: self.btn_cargar_mas.pack(fill="x", pady=5)
        else: self.btn_cargar_mas.pack_forget()
        lote = self.mensajes_totales[self.indice_superior : self.indice_inferior_actual]
        corte = len(self.mensajes_totales) - self.mensajes_nuevos_count
        for i, m in enumerate(lote):
            idx = self.indice_superior + i
            nuevo = (idx >= corte and self.mensajes_nuevos_count > 0 and int(m[1]) != int(self.id_origen))
            self.insertar_burbuja(self.frame_mensajes, m[0], m[1], m[3], m[4], es_nuevo=nuevo)
        self.gestionar_boton_nuevos()
        if self.mensajes_nuevos_count > 0: self.after(200, lambda: self.frame_mensajes._parent_canvas.yview_moveto(0.0))
        else: self.after(200, self.bajar_scroll)

    def gestionar_boton_nuevos(self):
        if self.indice_inferior_actual < len(self.mensajes_totales): self.btn_cargar_nuevos.pack(fill="x", pady=10, side="bottom")
        else: self.btn_cargar_nuevos.pack_forget()

    def cargar_lote_siguiente(self):
        inicio = self.indice_inferior_actual
        fin = min(len(self.mensajes_totales), inicio + self.LIMITE_LOTE)
        lote = self.mensajes_totales[inicio:fin]
        contenedor = ctk.CTkFrame(self.frame_mensajes, fg_color="transparent")
        contenedor.pack(fill="x", before=self.btn_cargar_nuevos)
        corte = len(self.mensajes_totales) - self.mensajes_nuevos_count
        for i, m in enumerate(lote):
            idx = inicio + i
            nuevo = (idx >= corte and int(m[1]) != int(self.id_origen))
            self.insertar_burbuja(contenedor, m[0], m[1], m[3], m[4], es_nuevo=nuevo)
        self.indice_inferior_actual = fin
        self.gestionar_boton_nuevos()

    def cargar_mas_antiguos(self):
        if self.indice_superior <= 0: return
        canvas = self.frame_mensajes._parent_canvas
        self.frame_mensajes.update_idletasks()
        h_antes, pos_v_antes = canvas.bbox("all")[3], canvas.yview()[0]
        limite = max(0, self.indice_superior - self.LIMITE_LOTE)
        seg = self.mensajes_totales[limite : self.indice_superior]
        bloque = ctk.CTkFrame(self.frame_mensajes, fg_color="transparent")
        fecha_l = None
        for m in seg:
            f_o = m[4] if isinstance(m[4], datetime) else datetime.now()
            f_s = f_o.strftime("%d/%m/%Y")
            if f_s != fecha_l:
                ctk.CTkLabel(bloque, text=f"— {f_s} —", text_color="gray", font=("Arial", 11, "bold")).pack(pady=5)
                fecha_l = f_s
            self.insertar_burbuja(bloque, m[0], m[1], m[3], m[4])
        bloque.pack(side="top", fill="x", after=self.btn_cargar_mas)
        self.indice_superior = limite
        if self.indice_superior == 0: self.btn_cargar_mas.pack_forget()
        bloque.update_idletasks()
        h_despues = canvas.bbox("all")[3]
        nueva_p = ((pos_v_antes * h_antes) + (h_despues - h_antes)) / h_despues
        canvas.yview_moveto(nueva_p)

    def insertar_burbuja(self, parent, id_msj, id_remit, texto, fecha_raw, es_nuevo=False):
        f_o = fecha_raw if isinstance(fecha_raw, datetime) else datetime.now()
        f_s, h_s = f_o.strftime("%d/%m/%Y"), f_o.strftime("%H:%M")
        if parent == self.frame_mensajes:
            if f_s != self.ultima_fecha_cargada:
                ctk.CTkLabel(parent, text=f"— {f_s} —", text_color="gray", font=("Arial", 11, "bold")).pack(pady=10)
                self.ultima_fecha_cargada = f_s
            if es_nuevo and not self.separador_visto:
                ctk.CTkLabel(parent, text="— MENSAJES SIN LEER —", text_color="green", font=("Arial", 11, "bold")).pack(pady=10)
                self.separador_visto = True
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", pady=2)
        fila.columnconfigure(1, weight=1)
        mio = int(id_remit) == int(self.id_origen)
        burbuja = ctk.CTkFrame(fila, fg_color="#2E86C1" if mio else "#515A5A", corner_radius=12)
        burbuja.grid(row=0, column=1, padx=5, sticky="e" if mio else "w")
        ctk.CTkLabel(burbuja, text=texto, padx=12, pady=6, wraplength=280, justify="left").pack()
        if not mio and id_msj:
            btn = ctk.CTkButton(fila, text=self.ICONO_BANDERA, width=30, fg_color="#E67E22", command=lambda mid=id_msj, t=texto: self.confirmar_reporte(mid, t))
            self.lista_btn_reporte.append(btn)
            if self.modo_reporte: btn.grid(row=0, column=0, padx=5)
        if mio and id_msj:
            cb = ctk.CTkCheckBox(fila, text="", width=20, command=lambda mid=id_msj: self.actualizar_conteo(mid))
            self.lista_checkboxes.append(cb)
            if self.modo_seleccion: cb.grid(row=0, column=2, padx=5)
        ctk.CTkLabel(fila, text=h_s, font=("Arial", 8), text_color="gray").grid(row=1, column=1, sticky="e" if mio else "w", padx=10)

    def toggle_modo_reporte(self):
        self.modo_reporte = not self.modo_reporte
        self.btn_reporte_toggle.configure(text="Reportar" if not self.modo_reporte else "Cancelar")
        for b in self.lista_btn_reporte:
            if self.modo_reporte: b.grid(row=0, column=0, padx=5)
            else: b.grid_forget()

    def confirmar_reporte(self, id_m, txt):
        if messagebox.askyesno("Reportar", "¿Denunciar mensaje?", parent=self):
            diag = ctk.CTkInputDialog(text="Motivo:", title="Reportar")
            motivo = diag.get_input()
            if motivo:
                if enviar_reporte(self.conn, self.id_origen, id_m, 'MENSAJE', self.id_destino, motivo, txt):
                    messagebox.showinfo("Éxito", "Reporte enviado.", parent=self)
                    self.toggle_modo_reporte()

    def toggle_modo_seleccion(self):
        self.modo_seleccion = not self.modo_seleccion
        self.seleccionados.clear()
        if self.modo_seleccion:
            self.btn_modo.pack_forget(); self.btn_confirmar.pack(side="left", padx=10); self.btn_cancelar.pack(side="right", padx=10)
            for c in self.lista_checkboxes: c.grid(row=0, column=2, padx=5)
        else:
            self.btn_confirmar.pack_forget(); self.btn_cancelar.pack_forget(); self.btn_modo.pack(side="left", padx=10)
            for c in self.lista_checkboxes: c.grid_forget(); c.deselect()

    def ejecutar_borrado_multiple(self):
        if not self.seleccionados: return
        if messagebox.askyesno("Confirmar", f"¿Eliminar {len(self.seleccionados)} mensajes?", parent=self):
            for mid in self.seleccionados: functions.eliminar_mensaje(self.conn, self.id_origen, mid)
            self.toggle_modo_seleccion(); self.inicializar_chat_progresivo()

    def actualizar_conteo(self, mid):
        if mid in self.seleccionados: self.seleccionados.remove(mid)
        else: self.seleccionados.add(mid)
        self.btn_confirmar.configure(text=f"Eliminar ({len(self.seleccionados)})")

    def enviar(self):
        txt = self.entry_msj.get().strip()
        if txt:
            exito, _ = functions.enviar_mensaje(self.conn, self.id_origen, self.id_destino, txt)
            if exito:
                self.entry_msj.delete(0, "end"); ahora = datetime.now(); self.mensajes_totales.append((None, self.id_origen, self.id_destino, txt, ahora))
                if self.indice_inferior_actual >= len(self.mensajes_totales) - 1:
                    self.insertar_burbuja(self.frame_mensajes, None, self.id_origen, txt, ahora); self.indice_inferior_actual = len(self.mensajes_totales); self.bajar_scroll()
                if hasattr(self.master, 'cargar_usuarios'): self.master.cargar_usuarios()

    def validar_longitud(self, t):
        if len(t) <= self.MAX_CHARS_INPUT:
            self.lbl_contador.configure(text=f"{len(t)} / {self.MAX_CHARS_INPUT}"); return True
        return False

    def bajar_scroll(self):
        self.frame_mensajes.update_idletasks(); self.frame_mensajes._parent_canvas.yview_moveto(1.0)

    def on_close(self):
        self.ejecutando_hilo = False; self.destroy()