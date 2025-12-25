import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from publicidad import functions 

class VentanaPublicidad(ctk.CTkFrame):
    def __init__(self, master, conn):
        super().__init__(master)
        self.conn = conn
        
        # Título Principal
        self.lbl_titulo = ctk.CTkLabel(self, text="GESTIÓN DE PUBLICIDAD", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=10)

        # ---------------------------------------------------
        # ZONA 1: CREAR (Formulario - Arriba)
        # ---------------------------------------------------
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=300) 
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(self.scroll_frame, text="1. Contratar Nueva Campaña", font=("Arial", 16, "bold"), text_color="cyan").pack(pady=5, anchor="w")

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

        # Características Extra
        ctk.CTkLabel(self.scroll_frame, text="Características (Opcional)", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w")
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
        
        self.scroll_frame_gestion = ctk.CTkScrollableFrame(self, height=200)
        self.scroll_frame_gestion.pack(fill="both", expand=False, padx=20, pady=10, side="bottom")

        self.frame_gestion = ctk.CTkFrame(self.scroll_frame_gestion, fg_color=("gray85", "gray20"))
        self.frame_gestion.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.frame_gestion, text="2. Gestión de Campañas Activas", font=("Arial", 16, "bold"), text_color="orange").pack(pady=5)

        self.entry_id_gestion = ctk.CTkEntry(self.frame_gestion, placeholder_text="ESCRIBE AQUÍ EL ID A GESTIONAR")
        self.entry_id_gestion.pack(pady=5, padx=10, fill="x")

        self.frame_botones = ctk.CTkFrame(self.frame_gestion, fg_color="transparent")
        self.frame_botones.pack(pady=10)

        # Botones de Acción
        self.btn_extender = ctk.CTkButton(self.frame_botones, text="Extender Fecha", command=self.accion_extender, fg_color="#D35400", width=120)
        self.btn_extender.pack(side="left", padx=5)

        self.btn_eliminar = ctk.CTkButton(self.frame_botones, text="Eliminar", command=self.accion_eliminar, fg_color="#C0392B", width=120)
        self.btn_eliminar.pack(side="left", padx=5)

        self.btn_ver_lista = ctk.CTkButton(self.frame_botones, text="Ver Lista Activos", command=self.accion_ver_lista, fg_color="#2980B9", width=120)
        self.btn_ver_lista.pack(side="left", padx=5)

    # =======================================================
    # LÓGICA DE LOS BOTONES
    # =======================================================

    def accion_guardar(self):
        print("Botón Guardar pulsado...") 
        try:
            fecha_dt = datetime.strptime(self.entry_fecha.get(), "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "La fecha debe ser DD/MM/YYYY")
            return

        datos = {
            'id': self.entry_id.get(),
            'titulo': self.entry_titulo.get(),
            'cuerpo': self.entry_cuerpo.get(),
            'enlace': self.entry_enlace.get(),
            'fechafin': fecha_dt,
            'nom_carac': self.entry_nom_carac.get(),
            'val_carac': self.entry_val_carac.get()
        }

        if functions.crear_anuncio_bd(self.conn, datos):
            messagebox.showinfo("Éxito", "Anuncio creado correctamente.")
            self.limpiar_campos_crear()
        else:
            messagebox.showerror("Error", "Error en BD (Revisa la consola).")

    def accion_extender(self):
        print("Botón Extender pulsado...")
        id_anuncio = self.entry_id_gestion.get()
        
        if not id_anuncio:
            messagebox.showwarning("Atención", "Debes escribir el ID en el cuadro GRIS de abajo.")
            return
            
        dialog = ctk.CTkInputDialog(text="Nueva Fecha Fin (DD/MM/YYYY):", title="Extender Campaña")
        nueva_fecha_str = dialog.get_input()
        
        if nueva_fecha_str:
            try:
                nueva_fecha = datetime.strptime(nueva_fecha_str, "%d/%m/%Y")
                exito, msg = functions.extender_campana_bd(self.conn, id_anuncio, nueva_fecha)
                if exito:
                    messagebox.showinfo("Éxito", msg)
                    self.entry_id_gestion.delete(0, "end")
                    self.accion_ver_lista() # Opcional: abrir lista para ver cambio
                else:
                    messagebox.showerror("Error", msg)
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido.")

    def accion_eliminar(self):
        print("Botón Eliminar pulsado...")
        id_anuncio = self.entry_id_gestion.get()
        
        if not id_anuncio:
            messagebox.showwarning("Atención", "Debes escribir el ID en el cuadro GRIS de abajo.")
            return

        respuesta = messagebox.askyesno("Confirmar", f"¿Estás seguro de borrar el anuncio {id_anuncio}?")
        if respuesta:
            exito, msg = functions.eliminar_anuncio_bd(self.conn, id_anuncio)
            if exito:
                messagebox.showinfo("Eliminado", msg)
                self.entry_id_gestion.delete(0, "end")
            else:
                messagebox.showerror("Error", msg)

    def accion_ver_lista(self):
        print("Cargando lista...")
        # 1. Recuperar datos de la BD
        filas = functions.listar_activos_bd(self.conn)

        # 2. Crear ventana flotante (Toplevel)
        ventana_lista = ctk.CTkToplevel(self)
        ventana_lista.title("Mis Anuncios Activos")
        ventana_lista.geometry("600x400")
        ventana_lista.attributes("-topmost", True) # Siempre visible encima

        # 3. Título interno
        ctk.CTkLabel(ventana_lista, text="LISTADO DE CAMPAÑAS ACTIVAS", font=("Arial", 18, "bold")).pack(pady=10)

        # 4. Caja de texto para mostrar los datos
        textbox = ctk.CTkTextbox(ventana_lista, width=550, height=300)
        textbox.pack(pady=10, padx=10)
        
        # 5. Formatear texto
        if not filas:
            textbox.insert("0.0", "No tienes anuncios activos actualmente.")
        else:
            cabecera = f"{'ID':<10} | {'FECHA FIN':<12} | {'TÍTULO'}\n"
            textbox.insert("end", cabecera)
            textbox.insert("end", "-"*70 + "\n")
            
            for row in filas:
                # row[0]=ID, row[1]=TITULO, row[2]=FECHAFIN (datetime)
                id_anun = str(row[0])
                titulo = str(row[1])
                
                # Manejo seguro de la fecha
                if row[2]: 
                    fecha = row[2].strftime("%d/%m/%Y")
                else:
                    fecha = "Indefinida"
                
                linea = f"{id_anun:<10} | {fecha:<12} | {titulo}\n"
                textbox.insert("end", linea)

        textbox.configure(state="disabled") # Solo lectura

    # Utilitarios
    def limpiar_campos_crear(self):
        self.entry_id.delete(0, "end")
        self.entry_titulo.delete(0, "end")
        self.entry_cuerpo.delete(0, "end")
        self.entry_enlace.delete(0, "end")
        self.entry_fecha.delete(0, "end")
        self.entry_nom_carac.delete(0, "end")
        self.entry_val_carac.delete(0, "end")