import customtkinter as ctk
from tkinter import messagebox
from . import functions
import random
from aspectoslegales.functions import enviar_reporte 

NUM_PUBLICACIONES_MOSTRAR_ANUNCIO = 5
NUM_PUBLICACIONES_MOSTRAR = NUM_PUBLICACIONES_MOSTRAR_ANUNCIO*2

DEFAULT_FONT="Arial"
LIKE_RED_COLOR="#E74C3C"
LIKED_GREEN_COLOR="#2ECC71"
REPORT_ORANGE_COLOR="#F39C12"

MAX_TITLE = 30
MAX_DESC = 256
MAX_IMG = 255

class VentanaPublicaciones(ctk.CTkFrame):
    def __init__(self, master, conn, id_usuario, es_admin = False):
        super().__init__(master)
        self.conn = conn
        self.id_usuario = id_usuario
        self.es_admin = es_admin
        self.offset_actual = 0
        
        # IMPORTANTE: No creamos widgets aquí para evitar el SegFault inmediato.
        # Solo preparamos el esqueleto y delegamos la creación al 'after'.
        self.after(200, self._inicializar_interfaz)

    def _inicializar_interfaz(self):
        """Crea los componentes base con la ventana ya asentada"""
        try:
            # --- TÍTULO ---
            self.lbl_titulo = ctk.CTkLabel(self, text="Muro de Publicaciones", font=(DEFAULT_FONT, 24, "bold"))
            self.lbl_titulo.pack(pady=10)

            # --- NAVEGACIÓN ---
            self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.nav_frame.pack(fill="x", padx=20, pady=5)

            self.btn_feed = ctk.CTkButton(self.nav_frame, text="📄 Feed Global", font=(DEFAULT_FONT, 18),
                                          command=self.mostrar_feed_general, fg_color="#2E86C1", width=140)
            self.btn_feed.pack(side="left", padx=5)

            self.btn_propias = ctk.CTkButton(self.nav_frame, text="🏠 Mis Publicaciones", font=(DEFAULT_FONT, 18),
                                             command=self.mostrar_mis_publicaciones, fg_color="#28B463", width=140)
            self.btn_propias.pack(side="left", padx=5)

            self.btn_crear = ctk.CTkButton(self.nav_frame, text="➕ Crear", font=(DEFAULT_FONT, 18),
                                           command=self.abrir_ventana_crear, fg_color="#D35400", width=100)
            self.btn_crear.pack(side="right", padx=5)

            self.btn_cargar_mas = None

            # --- ÁREA SCROLLABLE ---
            self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Iniciando...", label_font=(DEFAULT_FONT, 18))
            self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

            # Lanzar la carga de datos con otro pequeño retraso
            self.after(200, self.mostrar_feed_general)
        except Exception as e:
            print(f"Error en inicialización: {e}")

    def limpiar_lista(self):
        if hasattr(self, 'scroll_frame'):
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            self.update()

    def mostrar_feed_general(self):
        self.limpiar_lista()
        self.offset_actual = 0
        self.scroll_frame.configure(label_text="Cargando feed...")
        self.cargar_lote_publicaciones(privado=False)

    def mostrar_mis_publicaciones(self):
        self.limpiar_lista()
        self.offset_actual=0
        self.scroll_frame.configure(label_text="Cargando mis publicaciones...")
        self.cargar_lote_publicaciones(privado=True)

    def cargar_lote_publicaciones(self, privado=False):
        if self.btn_cargar_mas:
            self.btn_cargar_mas.destroy()
            self.btn_cargar_mas = None

        try:
            publicaciones = functions.listar_publicaciones(self.conn, self.id_usuario,
                                                           offset=self.offset_actual,
                                                           limit=NUM_PUBLICACIONES_MOSTRAR,
                                                           privado=privado)
            if not publicaciones and self.offset_actual == 0:
                ctk.CTkLabel(self.scroll_frame, text="No hay publicaciones.").pack(pady=20)
                self.scroll_frame.configure(label_text="Muro vacío")
                return

            anuncios = None if privado else functions.obtener_anuncios_para_publicaciones(self.conn,self.id_usuario)
            num_publicaciones = len(publicaciones)
            publicaciones_en_pantalla=min(NUM_PUBLICACIONES_MOSTRAR_ANUNCIO, num_publicaciones)

            min_gap = 2
            anuncio_en = 0

            for i, p in enumerate(publicaciones):
                if not privado:
                    nombre, desc, img, likes, autor, id_pub, le_ha_dado_like = p[:7]
                    id_autor = p[7] if len(p) > 7 else None

                    if anuncios and i % NUM_PUBLICACIONES_MOSTRAR_ANUNCIO == 0:
                        if anuncio_en + min_gap >= NUM_PUBLICACIONES_MOSTRAR_ANUNCIO:
                            limite_inferior = (anuncio_en+2) % publicaciones_en_pantalla
                        else: limite_inferior = 0
                        if limite_inferior < publicaciones_en_pantalla:
                            anuncio_en=random.randrange(limite_inferior,publicaciones_en_pantalla)
                        else: anuncio_en = 0
                        
                    if anuncios and i % publicaciones_en_pantalla == anuncio_en: 
                        self.crear_tarjeta_anuncio(anuncios[random.randrange(0,len(anuncios))])
                    
                    self.crear_tarjeta_publicacion(id_pub,nombre, desc, img, likes, autor,
                                                   es_propia=False, like_inicial=bool(le_ha_dado_like),
                                                   id_autor=id_autor)
                else:
                    nombre, desc, img, likes, id_pub = p[:5]
                    self.crear_tarjeta_publicacion(id_pub, nombre,desc,img,likes, "Yo", es_propia=True)
            self.offset_actual += num_publicaciones

            if num_publicaciones == NUM_PUBLICACIONES_MOSTRAR:
                self.btn_cargar_mas = ctk.CTkButton(
                        self.scroll_frame, text="Cargar más publicaciones ⬇", 
                        command=lambda: self.cargar_lote_publicaciones(privado),
                        fg_color="#566573", hover_color="#2C3E50"
                        )
                self.btn_cargar_mas.pack(pady=15)
            self.scroll_frame.configure(label_text="Feed Global" if not privado else "Mis Publicaciones")
        except Exception as e:
            print(f"Error en carga de lote: {e}")

    def crear_tarjeta_publicacion(self, id_pub, nombre, desc, img, likes, autor, es_propia, like_inicial=False, id_autor=None):
        card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E5E7E9", "#34495E"))
        card.pack(fill="x", pady=5, padx=5)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(info, text=nombre, font=(DEFAULT_FONT, 16, "bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=f"👤 {autor}", font=(DEFAULT_FONT, 13, "italic"), text_color="gray", anchor="w").pack(fill="x")
        
        if desc:
            ctk.CTkLabel(info, text=desc, font=(DEFAULT_FONT, 13), wraplength=300, justify="left").pack(fill="x", pady=5)

        if img:
            ctk.CTkLabel(info, text=f"🖼️ [Imagen adjunta]: {img}", font=(DEFAULT_FONT, 14), text_color="#5DADE2", anchor="w").pack(fill="x", pady=5)

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="right", padx=10)

        lbl_l = ctk.CTkLabel(actions, text=str(likes))
        lbl_l.pack()

        if es_propia:
            btn_edit = ctk.CTkButton(actions, text="✏️", width=40, fg_color="#F39C12",
                                     command=lambda:self.abrir_ventana_editar(id_pub,nombre,desc,img))
            btn_edit.pack(pady=2)

            ctk.CTkButton(actions, text="🗑️", width=35, fg_color="#C0392B",
                          command=lambda i=id_pub: self.accion_eliminar(i)).pack(pady=2)
        else:
            b_frame = ctk.CTkFrame(actions, fg_color="transparent")
            b_frame.pack()
            
            c_l = LIKED_GREEN_COLOR if like_inicial else LIKE_RED_COLOR
            btn_like = ctk.CTkButton(b_frame, text="❤️", width=35, fg_color=c_l)
            btn_like.configure(command=lambda: self.accion_like(id_pub, btn_like, lbl_l))
            btn_like.pack()
            
            if id_autor != self.id_usuario:
                ctk.CTkButton(b_frame, text="!", width=35, fg_color=REPORT_ORANGE_COLOR, font=(DEFAULT_FONT, 14, "bold"),
                              command=lambda i=id_pub, a=id_autor: self.accion_reportar(i, a)).pack(side="left", padx=2)

    def crear_tarjeta_anuncio(self, d):
        card = ctk.CTkFrame(self.scroll_frame, fg_color=("#F9E79F", "#7D6608"), border_width=1)
        card.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(card, text=f"📢 {d[0]}", font=(DEFAULT_FONT, 14, "bold")).pack(pady=5)
        ctk.CTkLabel(card, text=d[1], font=(DEFAULT_FONT, 12), wraplength=350).pack(pady=5)

    def accion_like(self, id_p, btn_widget, lbl):
        try:
            functions.toggle_like(id_p, self.id_usuario, self.conn)
            #Refrescar solo el contador
            color_actual = btn_widget.cget("fg_color")
            likes_actuales = int(lbl.cget("text"))

            if color_actual == LIKE_RED_COLOR:
                nuevo_color = LIKED_GREEN_COLOR
                nuevos_likes = likes_actuales + 1
            else:
                nuevo_color = LIKE_RED_COLOR
                nuevos_likes = max(0, likes_actuales-1)
            btn_widget.configure(fg_color=nuevo_color)
            lbl.configure(text=str(nuevos_likes))
        except: pass

    def accion_reportar(self, id_p, id_a):
        if not id_a:
            messagebox.showwarning("Aviso", "No se puede reportar: ID de autor no encontrado.")
            return
            
        motivo = ctk.CTkInputDialog(text="Motivo del reporte:", title="Reportar").get_input()
        
        if motivo:
            # id_p es el id_objetivo, id_a es el id_denunciado
            if enviar_reporte(self.conn, id_p, "PUBLICACION", id_a, motivo):
                messagebox.showinfo("Éxito", "Reporte enviado.")
            else:
                messagebox.showerror("Error", "No se pudo enviar el reporte. Verifique su sesión.")
    def accion_eliminar(self, id_p):
        if messagebox.askyesno("Confirmar", "¿Eliminar publicación?"):
            cursor = self.conn.cursor()
            if functions.eliminar_publicacion(cursor, self.id_usuario, id_p):
                self.conn.commit()
                self.mostrar_mis_publicaciones()
            cursor.close()

    def abrir_ventana_crear(self):
        VentanaGestionPublicacion(self, self.conn, self.id_usuario, modo="crear")

    def abrir_ventana_editar(self, id_pub, nombre, desc, img):
        datos_actuales = {"nombre": nombre, "desc": desc, "img": img}
        VentanaGestionPublicacion(self, self.conn, self.id_usuario, 
                                  modo="editar", id_publicacion=id_pub, datos = datos_actuales)

class VentanaGestionPublicacion(ctk.CTkToplevel):
    def __init__(self, parent, conn, id_u, modo="crear", id_publicacion=None, datos=None):
        super().__init__(parent)
        self.conn, self.id_u, self.parent, self.modo = conn, id_u, parent, modo
        self.id_p = id_publicacion
        self.title("Nueva Publicación" if modo == "crear" else "Editar Publicación")
        self.geometry("400x600")
        self.attributes("-topmost", True)

        # 1. Preparar widgets antes de mostrar
        self._crear_widgets(datos=datos)

        # 2. Manejo de la visibilidad y el grab para evitar el error "window not viewable"
        self.withdraw()
        self.after(10, self._lanzar_modal)

    def _crear_widgets(self,datos=None):
        """Organiza la creación de los elementos de la interfaz"""
        
        # ---------- TÍTULO ----------
        ctk.CTkLabel(
            self, text=f"Título (Obligatorio, máx. {MAX_TITLE})",
            font=(DEFAULT_FONT, 14, "bold")
        ).pack(pady=(20, 5))

        self.title_var = ctk.StringVar()
        self.title_var.trace_add(
            "write",
            lambda *args: self._limitar_var(self.title_var, MAX_TITLE)
        )

        self.en = ctk.CTkEntry(self, width=300, textvariable=self.title_var)
        self.en.pack(pady=5)

        # ---------- DESCRIPCIÓN ----------
        ctk.CTkLabel(
            self, text=f"Descripción (máx. {MAX_DESC})",
            font=(DEFAULT_FONT, 14)
        ).pack(pady=(10, 5))

        self.ed = ctk.CTkTextbox(self, width=300, height=150)
        self.ed.pack(pady=5)
        self.ed.bind(
            "<KeyRelease>",
            lambda e: self._limitar_textbox(self.ed, MAX_DESC)
        )

        # ---------- URL IMAGEN / TEXTO ----------
        ctk.CTkLabel(
            self, text="URL Imagen / Texto",
            font=(DEFAULT_FONT, 14)
        ).pack(pady=(10, 5))

        self.url_var = ctk.StringVar()
        self.url_var.trace_add(
            "write",
            lambda *args: self._limitar_var(self.url_var, MAX_IMG)
        )

        self.en_img = ctk.CTkEntry(self, width=300, textvariable=self.url_var)
        self.en_img.pack(pady=5)

        # ---------- CATEGORÍA ----------
        ctk.CTkLabel(
            self, text="Categoría",
            font=(DEFAULT_FONT, 14)
        ).pack(pady=(10, 5))

        self.en_cat = ctk.CTkEntry(self, width=300)
        self.en_cat.pack(pady=5)

        if self.modo == "editar" and datos:
            self.title_var.set(datos["nombre"])
            if datos["desc"]: self.ed.insert("0.0", datos["desc"])
            if datos["img"]: self.url_var.set(datos["img"])

        
        btn_text = "🚀 Publicar" if self.modo == "crear" else "Guardar cambios"
        ctk.CTkButton(self, text=btn_text, fg_color="#D35400", 
                      command=self.guardar, width=200).pack(pady=30)
    
    def _limitar_var(self, var, max_len):
        value = var.get()
        if len(value) > max_len:
            var.set(value[:max_len])

    def _limitar_textbox(self, textbox, max_len):
        content = textbox.get("0.0", "end-1c")
        if len(content) > max_len:
            textbox.delete("0.0", "end")
            textbox.insert("0.0", content[:max_len])

    def _lanzar_modal(self):
        self.deiconify()          
        self.wait_visibility()   
        self.grab_set()          
        self.attributes("-topmost", True)
        self.focus_set()

    def guardar(self):
        n = self.en.get()
        d = self.ed.get("0.0", "end").strip()
        img = self.en_img.get()
        cat = self.en_cat.get()
        
        if not n:
            messagebox.showwarning("Atención", "El título es obligatorio.")
            return

        cursor = self.conn.cursor()
        try:
            exito = False
            if self.modo == "crear":
                exito = functions.crear_publicacion(cursor, self.id_u,n,img,d,cat)
            else:
                exito = functions.modificar_publicacion(cursor, self.id_u,self.id_p,n,d,img,cat)

            if exito:
                self.conn.commit()
                messagebox.showinfo("Éxito", "Operación realizada correctamente.")
                self.destroy()
                
                if self.modo == "crear":
                    self.parent.mostrar_feed_general()
                else:
                    self.parent.mostrar_mis_publicaciones()
            else:
                messagebox.showerror("Error", "No se pudo crear/modificar la publicación.")
        except Exception as e:
            print(f"Error Crítico: {e}")
        finally:
            cursor.close()
