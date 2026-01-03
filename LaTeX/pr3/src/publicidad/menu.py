import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from publicidad import functions 

class VentanaPublicidad(ctk.CTkFrame):
    def __init__(self, master, conn, id_usuario, es_admin=False):
        super().__init__(master)
        self.conn = conn
        self.id_usuario = id_usuario # ID del usuario logueado
        self.es_admin = es_admin     # Rol (True/False)
        
        # Limpiamos cualquier widget previo
        for widget in self.winfo_children():
            widget.destroy()

        # --- Lógica de Bifurcación (RBAC) ---
        if self.es_admin:
            self.construir_interfaz_admin()
        else:
            self.construir_interfaz_usuario()

    # =======================================================
    # VISTA ADMINISTRADOR (Gestión Total)
    # =======================================================
    def construir_interfaz_admin(self):
        # Título Principal
        self.lbl_titulo = ctk.CTkLabel(self, text="GESTIÓN DE PUBLICIDAD (ADMIN)", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=10)

        # ---------------------------------------------------
        # ZONA 1: CREAR (Formulario)
        # ---------------------------------------------------
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=350) 
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(self.scroll_frame, text="1. Contratar Nueva Campaña", font=("Arial", 16, "bold"), text_color="#5DADE2").pack(pady=5, anchor="w")

        # Campos básicos
        self.entry_id = ctk.CTkEntry(self.scroll_frame, placeholder_text="ID Anuncio (ej: A001)")
        self.entry_id.pack(pady=5, fill="x")

        self.entry_titulo = ctk.CTkEntry(self.scroll_frame, placeholder_text="Título")
        self.entry_titulo.pack(pady=5, fill="x")

        self.entry_cuerpo = ctk.CTkEntry(self.scroll_frame, placeholder_text="Cuerpo/Descripción")
        self.entry_cuerpo.pack(pady=5, fill="x")

        self.entry_enlace = ctk.CTkEntry(self.scroll_frame, placeholder_text="Enlace URL")
        self.entry_enlace.pack(pady=5, fill="x")

        self.entry_fecha = ctk.CTkEntry(self.scroll_frame, placeholder_text="Fecha Fin (DD/MM/YYYY)")
        self.entry_fecha.pack(pady=5, fill="x")

        # --- NUEVO CAMPO: ID PROPIETARIO ---
        # Permite al admin asignar el anuncio a otro usuario (o a sí mismo si lo deja vacío)
        ctk.CTkLabel(self.scroll_frame, text="Asignar Propietario (Opcional)", font=("Arial", 12, "bold")).pack(pady=(5,0), anchor="w")
        self.entry_propietario = ctk.CTkEntry(self.scroll_frame, placeholder_text=f"ID Dueño (Tu ID es {self.id_usuario})")
        self.entry_propietario.pack(pady=5, fill="x")

        # Características Extra
        ctk.CTkLabel(self.scroll_frame, text="Características (Validación Activada)", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w")
        self.frame_extras = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.frame_extras.pack(fill="x", pady=5)
        
        self.entry_nom_carac = ctk.CTkEntry(self.frame_extras, placeholder_text="Nombre (ej: Color)")
        self.entry_nom_carac.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.entry_val_carac = ctk.CTkEntry(self.frame_extras, placeholder_text="Valor (ej: Rojo)")
        self.entry_val_carac.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.btn_guardar = ctk.CTkButton(self.scroll_frame, text="CONTRATAR CAMPAÑA", command=self.accion_guardar, fg_color="green")
        self.btn_guardar.pack(pady=20)

        # ---------------------------------------------------
        # ZONA 2: GESTIÓN (Abajo)
        # ---------------------------------------------------
        self.frame_gestion = ctk.CTkFrame(self, fg_color=("gray85", "gray20"))
        self.frame_gestion.pack(pady=10, padx=20, fill="x", side="bottom")

        ctk.CTkLabel(self.frame_gestion, text="2. Operaciones sobre Campañas", font=("Arial", 14, "bold")).pack(pady=5)

        self.entry_id_gestion = ctk.CTkEntry(self.frame_gestion, placeholder_text="ID Anuncio a gestionar")
        self.entry_id_gestion.pack(pady=5, padx=10, fill="x")

        self.frame_botones = ctk.CTkFrame(self.frame_gestion, fg_color="transparent")
        self.frame_botones.pack(pady=10)

        self.btn_extender = ctk.CTkButton(self.frame_botones, text="Extender Fecha", command=self.accion_extender, fg_color="#D35400", width=120)
        self.btn_extender.pack(side="left", padx=5)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="Eliminar", command=self.accion_eliminar, fg_color="#C0392B", width=120)
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_ver_lista = ctk.CTkButton(self.frame_botones, text="Ver Lista Global", command=self.accion_ver_lista, fg_color="#2980B9", width=120)
        self.btn_ver_lista.pack(side="left", padx=5)

    # =======================================================
    # VISTA USUARIO (Solo Lectura - Sus Anuncios)
    # =======================================================
    def construir_interfaz_usuario(self):
        self.lbl_titulo = ctk.CTkLabel(self, text="MIS CAMPAÑAS ACTIVAS", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=10)

        self.scroll_feed = ctk.CTkScrollableFrame(self)
        self.scroll_feed.pack(fill="both", expand=True, padx=20, pady=10)

        # Llamamos a listar pasando MI ID para que filtre
        try:
            anuncios = functions.listar_activos_bd(self.conn, self.id_usuario, self.es_admin)
        except Exception as e:
            ctk.CTkLabel(self.scroll_feed, text=f"Error cargando anuncios: {e}").pack()
            return

        if not anuncios:
            ctk.CTkLabel(self.scroll_feed, text="No tienes campañas activas asignadas.", font=("Arial", 16)).pack(pady=50)
            return

        for row in anuncios:
            # La query devuelve: ID, TITULO, FECHAFIN, CUERPO...
            titulo = row[1] 
            fecha_fin = row[2]
            cuerpo = row[3] if len(row) > 3 else ""

            # Formateo seguro de fecha
            txt_fecha = fecha_fin.strftime("%d/%m/%Y") if hasattr(fecha_fin, 'strftime') else str(fecha_fin)

            card = ctk.CTkFrame(self.scroll_feed, fg_color="#2E4053", border_color="#F1C40F", border_width=2)
            card.pack(fill="x", pady=10, ipadx=10, ipady=10)
            
            # Cabecera Tarjeta
            ctk.CTkLabel(card, text=titulo, font=("Arial", 18, "bold"), text_color="white").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Vence el: {txt_fecha}", font=("Arial", 12), text_color="orange").pack(anchor="w", padx=10)
            
            # Separador
            ctk.CTkFrame(card, height=2, fg_color="gray").pack(fill="x", padx=10, pady=5)
            
            # Cuerpo
            ctk.CTkLabel(card, text=str(cuerpo), font=("Arial", 14), text_color="#BDC3C7", anchor="w", justify="left").pack(fill="x", padx=10)


    # =======================================================
    # LÓGICA DE LOS BOTONES
    # =======================================================

    def accion_guardar(self):
        print("Botón Guardar pulsado...") 
        
        # 1. Validar fecha
        try:
            fecha_str = self.entry_fecha.get()
            if not fecha_str:
                messagebox.showwarning("Faltan datos", "La fecha es obligatoria")
                return
            fecha_dt = datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "La fecha debe ser DD/MM/YYYY")
            return

        # 2. Gestionar Propietario
        id_prop = self.entry_propietario.get()
        if not id_prop:
            id_prop = self.id_usuario # Si lo deja vacío, se asigna a sí mismo

        # 3. Empaquetar datos
        datos = {
            'id': self.entry_id.get(),
            'titulo': self.entry_titulo.get(),
            'cuerpo': self.entry_cuerpo.get(),
            'enlace': self.entry_enlace.get(),
            'fechafin': fecha_dt,
            'nom_carac': self.entry_nom_carac.get(), 
            'val_carac': self.entry_val_carac.get(),
            'id_propietario': id_prop 
        }

        # 4. Llamada al Backend (devuelve Tupla: Exito, Mensaje)
        exito, mensaje = functions.crear_anuncio_bd(self.conn, datos)

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar_campos_crear()
        else:
            # Aquí se mostrará el error del Trigger o validación
            messagebox.showerror("Error al Guardar", mensaje)

    def accion_extender(self):
        id_anuncio = self.entry_id_gestion.get()
        if not id_anuncio:
            messagebox.showwarning("Atención", "Escribe el ID en el cuadro de gestión.")
            return
            
        dialog = ctk.CTkInputDialog(text="Nueva Fecha Fin (DD/MM/YYYY):", title="Extender Campaña")
        nueva_fecha_str = dialog.get_input()
        
        if nueva_fecha_str:
            try:
                nueva_fecha = datetime.strptime(nueva_fecha_str, "%d/%m/%Y")
                try:
                    exito, msg = functions.extender_campania_bd(self.conn, id_anuncio, nueva_fecha)
                    if exito:
                        messagebox.showinfo("Éxito", msg)
                    else:
                        messagebox.showerror("Error", msg)
                except AttributeError:
                    messagebox.showerror("Error", "Función extender no encontrada en functions.py")

            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido.")

    def accion_eliminar(self):
        id_anuncio = self.entry_id_gestion.get()
        if not id_anuncio:
            messagebox.showwarning("Atención", "Escribe el ID en el cuadro de gestión.")
            return

        if messagebox.askyesno("Confirmar", f"¿Borrar anuncio {id_anuncio}?"):
            try:
                exito, msg = functions.eliminar_anuncio_bd(self.conn, id_anuncio)
                if exito:
                    messagebox.showinfo("Eliminado", msg)
                    self.entry_id_gestion.delete(0, "end")
                else:
                    messagebox.showerror("Error", msg)
            except AttributeError:
                messagebox.showerror("Error", "Función eliminar no encontrada en functions.py")

    def accion_ver_lista(self):
        # Esta es la lista global para el Admin
        filas = functions.listar_activos_bd(self.conn, self.id_usuario, self.es_admin)

        ventana_lista = ctk.CTkToplevel(self)
        ventana_lista.title("Todas las Campañas Activas")
        ventana_lista.geometry("600x400")
        ventana_lista.attributes("-topmost", True) 

        ctk.CTkLabel(ventana_lista, text="LISTADO GLOBAL (ADMIN)", font=("Arial", 18, "bold")).pack(pady=10)

        textbox = ctk.CTkTextbox(ventana_lista, width=550, height=300)
        textbox.pack(pady=10, padx=10)
        
        if not filas:
            textbox.insert("0.0", "No hay datos.")
        else:
            cabecera = f"{'ID':<10} | {'FIN':<12} | {'TÍTULO'}\n"
            textbox.insert("end", cabecera + "-"*60 + "\n")
            
            for row in filas:
                # row: [ID, TITULO, FECHAFIN, CUERPO]
                id_an = str(row[0])
                tit = str(row[1])
                f_fin = row[2].strftime("%d/%m/%Y") if row[2] else "N/A"
                
                linea = f"{id_an:<10} | {f_fin:<12} | {tit}\n"
                textbox.insert("end", linea)

        textbox.configure(state="disabled")

    def limpiar_campos_crear(self):
        self.entry_id.delete(0, "end")
        self.entry_titulo.delete(0, "end")
        self.entry_cuerpo.delete(0, "end")
        self.entry_enlace.delete(0, "end")
        self.entry_fecha.delete(0, "end")
        self.entry_propietario.delete(0, "end") # Limpiar también el dueño
        self.entry_nom_carac.delete(0, "end")
        self.entry_val_carac.delete(0, "end")