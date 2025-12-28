import customtkinter as ctk
from tkinter import messagebox
from . import functions
import random
from publicidad.functions import listar_activos_bd as obtener_anuncios

ID_USUARIO_ACTIVO = 8
NUM_PUBLICACIONES_MOSTRAR = 5
DEFAULT_FONT="Arial"
LIKE_RED_COLOR="#E74C3C"
LIKED_GREEN_COLOR="#2ECC71"

class VentanaPublicaciones(ctk.CTkFrame):
    def __init__(self, master, conn):
        super().__init__(master)
        self.conn = conn
        self.id_usuario = ID_USUARIO_ACTIVO
        
        # --- CONFIGURACIÓN PRINCIPAL ---
        self.lbl_titulo = ctk.CTkLabel(self, text="Muro de Publicaciones", font=(DEFAULT_FONT, 24, "bold"))
        self.lbl_titulo.pack(pady=10)

        # --- BARRA DE NAVEGACIÓN SUPERIOR (PESTAÑAS) ---
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=20, pady=5)

        # Botón Feed General (Documento)
        self.btn_feed = ctk.CTkButton(self.nav_frame, text="📄 Feed Global", font=(DEFAULT_FONT, 20),
                                      command=self.mostrar_feed_general,
                                      fg_color="#2E86C1", width=120)
        self.btn_feed.pack(side="left", padx=5)

        # Botón Mis Publicaciones (Home)
        self.btn_propias = ctk.CTkButton(self.nav_frame, text="🏠 Mis Publicaciones", font=(DEFAULT_FONT, 20),
                                         command=self.mostrar_mis_publicaciones,
                                         fg_color="#28B463", width=120)
        self.btn_propias.pack(side="left", padx=5)

        # Botón Crear (+)
        self.btn_crear = ctk.CTkButton(self.nav_frame, text="➕ Crear", font=(DEFAULT_FONT, 20),
                                       command=self.abrir_ventana_crear,
                                       fg_color="#D35400", width=80)
        self.btn_crear.pack(side="right", padx=5)

        # --- ÁREA DE CONTENIDO (SCROLL) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Publicaciones", label_font=(DEFAULT_FONT, 20))
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Cargar vista por defecto
        self.mostrar_feed_general()

    def limpiar_lista(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def mostrar_feed_general(self):
        self.limpiar_lista()
        self.scroll_frame.configure(label_text="Feed Global - Todas las publicaciones")
        
        #Se obtienen las publicaciones y si el usuario ha dado like
        #cada publicación es (NOMBRE, DESC, IMAGEN, NUM_LIKES, NOMBREUSUARIO, IDPUB), like_dado
        publicaciones = functions.listar_publicaciones(self.conn, self.id_usuario, privado=False)
        if not publicaciones:
            ctk.CTkLabel(self.scroll_frame, text="No hay publicaciones aún.").pack(pady=20)
            return
        #se obtienen los anuncios
        anuncios_disponibles = obtener_anuncios(self.conn)
        

        
        num_publicaciones=len(publicaciones)
        publicaciones_en_pantalla=min(NUM_PUBLICACIONES_MOSTRAR,num_publicaciones)
        anuncio_en=0
        for num_publi,p in enumerate(publicaciones):
            """
            Este if simula el cálculo en TUI, donde tiene que haber al menos
            dos publicaciones entre cada anuncio, el primer if es para permitir
            que pasen 5 publicaciones antes de recalcular donde se deberá de poner el 
            siguiente anuncio
            """
            if num_publi % NUM_PUBLICACIONES_MOSTRAR == 0:
                if anuncio_en + 2 >= NUM_PUBLICACIONES_MOSTRAR:
                    limite_inferior = (anuncio_en+2)%publicaciones_en_pantalla
                else: limite_inferior = 0
                if limite_inferior < publicaciones_en_pantalla:
                    anuncio_en=random.randrange(limite_inferior,publicaciones_en_pantalla)
                else: anuncio_en = 0
            
            if anuncios_disponibles and num_publi%publicaciones_en_pantalla == anuncio_en:
                anuncio = functions.cargar_anuncio_en_publicacion(anuncios_disponibles,self.conn)
                self.crear_tarjeta_anuncio(anuncio)

            # Desempaquetado seguro según functions.py
            try:
                nombre, desc, img, likes, autor, id_pub, le_ha_dado_like = p
            except ValueError:
                print(p)
            self.crear_tarjeta_publicacion(id_pub, nombre, desc, img, likes, autor, 
                                           es_propia=False, like_inicial=bool(le_ha_dado_like))

    def mostrar_mis_publicaciones(self):
        self.limpiar_lista()
        self.scroll_frame.configure(label_text="Mis Publicaciones - Gestión")
        
        # listar_publicaciones privado devuelve: (NOMBRE, DESC, IMG, LIKES, ID)
        publicaciones = functions.listar_publicaciones(self.conn, self.id_usuario, privado=True)

        if not publicaciones:
            ctk.CTkLabel(self.scroll_frame, text="No has publicado nada aún.").pack(pady=20)
            return

        for p in publicaciones:
            # Nota: la consulta privada NO devuelve el nombre de usuario, porque es el propio
            nombre, desc, img, likes, id_pub = p
            self.crear_tarjeta_publicacion(id_pub, nombre, desc, img, likes, "Yo", es_propia=True)

    def crear_tarjeta_publicacion(self, id_pub, nombre, desc, img, likes, autor, es_propia, like_inicial=False):
        """Crea un frame visual para cada publicación"""
        card = ctk.CTkFrame(self.scroll_frame, fg_color=("#E5E7E9", "#34495E"))
        card.pack(fill="x", pady=5, padx=5)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(info_frame, text=f"{nombre}", font=(DEFAULT_FONT, 18, "bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(info_frame, text=f"👤 {autor}", font=(DEFAULT_FONT, 16, "italic"), text_color="gray", anchor="w").pack(fill="x")
        
        if desc:
            ctk.CTkLabel(info_frame, text=desc, font=(DEFAULT_FONT, 16), wraplength=400, anchor="w", justify="left").pack(fill="x", pady=(5,0))
        
        if img:
            # Placeholder visual si hay imagen
            ctk.CTkLabel(info_frame, text=f"🖼️ [Imagen adjunta]: {img}", font=(DEFAULT_FONT,16), text_color="#5DADE2", anchor="w").pack(fill="x", pady=(5,0))

        # Columna Derecha: Acciones
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=10, pady=10)

        lbl_likes=ctk.CTkLabel(action_frame, text=f"{likes}")
        lbl_likes.pack(pady=(0,5))

        if not es_propia:
            # Botón LIKE
            color_btn = LIKED_GREEN_COLOR if like_inicial else LIKE_RED_COLOR
            btn_like = ctk.CTkButton(action_frame, text="❤️", width=40, fg_color=color_btn)
            btn_like.configure(command=lambda: self.accion_like(id_pub,btn_like,lbl_likes))
            btn_like.pack()
        else:
            # Botones EDITAR y BORRAR
            btn_edit = ctk.CTkButton(action_frame, text="✏️", width=40, fg_color="#F39C12",
                                     command=lambda: self.abrir_ventana_editar(id_pub, nombre, desc, img))
            btn_edit.pack(pady=2)
            
            btn_del = ctk.CTkButton(action_frame, text="🗑️", width=40, fg_color="#C0392B",
                                    command=lambda: self.accion_eliminar(id_pub))
            btn_del.pack(pady=2)

    def crear_tarjeta_anuncio(self, datos_anuncio):
        """ Crea una tarjeta visualmente distinta para publicidad """
        if not datos_anuncio: return

        try:
            titulo, cuerpo, enlace = datos_anuncio
        except ValueError:
            # Fallback por si devuelve algo diferente
            titulo = "Publicidad"
            cuerpo = str(datos_anuncio)
            enlace = ""

        card = ctk.CTkFrame(self.scroll_frame, fg_color=("#F9E79F", "#7D6608"), border_color="#F1C40F", border_width=2)
        card.pack(fill="x", pady=10, padx=5)

        ctk.CTkLabel(card, text="📢 PUBLICIDAD", font=(DEFAULT_FONT, 16, "bold"), text_color="white").pack(anchor="w", padx=10, pady=(5,0))
        ctk.CTkLabel(card, text=titulo, font=(DEFAULT_FONT, 16, "bold"), text_color="white").pack(anchor="w", padx=10)
        ctk.CTkLabel(card, text=cuerpo, font=(DEFAULT_FONT, 16), wraplength=400, justify="left", text_color="white").pack(fill="x", padx=10, pady=5)
        if enlace:
             ctk.CTkLabel(card, text=f"🔗 {enlace}", text_color="#85C1E9", cursor="hand2").pack(anchor="w", padx=10, pady=(0,10))

    # --- ACCIONES LÓGICAS ---

    def accion_like(self, id_pub,btn_widget,lbl_widget):
        functions.toggle_like(id_pub, self.id_usuario, self.conn)
        # Refrescar vista actual para actualizar contador
        color_actual = btn_widget.cget("fg_color")
        likes_actuales = int(lbl_widget.cget("text"))
        if color_actual == LIKE_RED_COLOR: 
            nuevo_color =  LIKED_GREEN_COLOR 
            nuevos_likes = likes_actuales + 1
        else: # Estaba verde (like), ahora quitamos like
            nuevo_color = LIKE_RED_COLOR # Rojo
            nuevos_likes = max(0, likes_actuales - 1)
        btn_widget.configure(fg_color=nuevo_color)
        lbl_widget.configure(text=str(nuevos_likes))

    def accion_eliminar(self, id_pub):
        respuesta = messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar esta publicación?")
        if respuesta:
            cursor = self.conn.cursor()
            if functions.eliminar_publicacion(cursor, self.id_usuario, id_pub):
                self.conn.commit()
                messagebox.showinfo("Éxito", "Publicación eliminada")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la publicación")
            cursor.close()
            self.mostrar_mis_publicaciones()

    def abrir_ventana_crear(self):
        VentanaGestionPublicacion(self, self.conn, self.id_usuario, modo="crear")

    def abrir_ventana_editar(self, id_pub, nombre, desc, img):
        # Necesitamos pasar los datos actuales
        datos_actuales = {"nombre": nombre, "desc": desc, "img": img}
        VentanaGestionPublicacion(self, self.conn, self.id_usuario, modo="editar", 
                                  id_publicacion=id_pub, datos=datos_actuales)


class VentanaGestionPublicacion(ctk.CTkToplevel):
    def __init__(self, parent, conn, id_usuario, modo="crear", id_publicacion=None, datos=None):
        super().__init__(parent)
        self.conn = conn
        self.id_usuario = id_usuario
        self.modo = modo
        self.id_publicacion = id_publicacion
        self.parent = parent # Referencia para refrescar

        self.title("Crear Publicación" if modo == "crear" else "Editar Publicación")
        self.geometry("400x500")
        self.attributes("-topmost", True)

        # Campos
        ctk.CTkLabel(self, text="Título (Obligatorio)", font=(DEFAULT_FONT,20)).pack(pady=(20, 5))
        self.entry_nombre = ctk.CTkEntry(self, width=300)
        self.entry_nombre.pack()

        ctk.CTkLabel(self, text="Descripción",font=(DEFAULT_FONT,16)).pack(pady=(10, 5))
        self.entry_desc = ctk.CTkTextbox(self, width=300, height=100)
        self.entry_desc.pack()

        ctk.CTkLabel(self, text="URL Imagen / Texto",font=(DEFAULT_FONT,16)).pack(pady=(10, 5))
        self.entry_img = ctk.CTkEntry(self, width=300)
        self.entry_img.pack()
        
        ctk.CTkLabel(self, text="Categoría",font=(DEFAULT_FONT,16)).pack(pady=(10, 5))
        self.entry_cat = ctk.CTkEntry(self, width=300)
        self.entry_cat.pack()

        # Pre-llenar datos si es editar
        if modo == "editar" and datos:
            self.entry_nombre.insert(0, datos["nombre"])
            if datos["desc"]: self.entry_desc.insert("0.0", datos["desc"])
            if datos["img"]: self.entry_img.insert(0, datos["img"])
            # Categoria no venía en el listado simple, lo dejamos vacío u opcional

        # Botón Guardar
        btn_text = "Publicar" if modo == "crear" else "Guardar Cambios"
        ctk.CTkButton(self, text=btn_text, command=self.guardar, fg_color="#27AE60").pack(pady=30)

    def guardar(self):
        nombre = self.entry_nombre.get()
        desc = self.entry_desc.get("0.0", "end").strip()
        img = self.entry_img.get()
        cat = self.entry_cat.get() # Opcional

        if not nombre:
            messagebox.showwarning("Faltan datos", "El título es obligatorio.")
            return

        cursor = self.conn.cursor()
        try:
            exito = False
            if self.modo == "crear":
                exito = functions.crear_publicacion(cursor, self.id_usuario, nombre, img, desc, cat)
            else:
                # Modificar: functions espera (cursor, id_usu, id_pub, nombre, desc, img, cat)
                exito = functions.modificar_publicacion(cursor, self.id_usuario, self.id_publicacion, nombre, desc, img, cat)
            
            if exito:
                self.conn.commit()
                messagebox.showinfo("Éxito", "Operación realizada correctamente.")
                self.destroy()
                # Refrescar la ventana padre dependiendo de donde vengamos
                if self.modo == "crear":
                    self.parent.mostrar_feed_general() # Ir al feed para ver la nueva
                else:
                    self.parent.mostrar_mis_publicaciones()
            else:
                messagebox.showerror("Error", "Hubo un problema en la base de datos.")
        
        except Exception as e:
            messagebox.showerror("Error Crítico", str(e))
        finally:
            cursor.close()
