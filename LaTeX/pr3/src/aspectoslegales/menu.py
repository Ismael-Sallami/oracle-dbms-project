import customtkinter as ctk
from tkinter import messagebox
from . import functions as aspects_functions

class VentanaReportes(ctk.CTkFrame):
    def __init__(self, master, conn):
        super().__init__(master)
        self.conn = conn
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- LISTA DE REPORTES (Izquierda) ---
        self.lista_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.lbl_lista = ctk.CTkLabel(self.lista_frame, text="Reportes Recientes", font=("Arial", 16, "bold"))
        self.lbl_lista.pack(pady=10)

        self.scroll_reportes = ctk.CTkScrollableFrame(self.lista_frame)
        self.scroll_reportes.pack(fill="both", expand=True, padx=5, pady=5)

        # --- DETALLE DEL REPORTE (Derecha) ---
        self.detalle_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.detalle_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.mostrar_placeholder()
        self.cargar_lista_reportes()

    def mostrar_placeholder(self):
        for widget in self.detalle_frame.winfo_children():
            widget.destroy()
        self.placeholder_lbl = ctk.CTkLabel(self.detalle_frame, text="Seleccione un reporte para ver los detalles", font=("Arial", 14, "italic"))
        self.placeholder_lbl.pack(expand=True)

    def cargar_lista_reportes(self):
        for widget in self.scroll_reportes.winfo_children():
            widget.destroy()

        reportes = aspects_functions.listar_todos_los_reportes(self.conn)
        
        if not reportes:
            ctk.CTkLabel(self.scroll_reportes, text="Sin reportes").pack(pady=20)
            return

        for rep in reportes:
            id_rep = rep[0]
            motivo = rep[4]
            
            btn = ctk.CTkButton(
                self.scroll_reportes, 
                text=f"ID: {id_rep}\n{motivo[:20]}...",
                fg_color="#34495E",
                anchor="w",
                command=lambda r=rep: self.mostrar_detalle(r)
            )
            btn.pack(fill="x", pady=2)


    def mostrar_detalle(self, reporte):
        """
        Muestra la información extendida de un reporte seleccionado.
        reporte esperado: (id_rep, denunciante, denun_nombre, tipo, motivo, prueba, id_p, id_m, id_denunciado_num)
        """
        for widget in self.detalle_frame.winfo_children():
            widget.destroy()

        id_rep, denunciante, denun_nombre, tipo, motivo, prueba, id_p, id_m, id_denunciado_num = reporte

        # Título del reporte
        ctk.CTkLabel(
            self.detalle_frame, 
            text=f"Detalles del Reporte #{id_rep}", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        scroll_contenido = ctk.CTkScrollableFrame(self.detalle_frame, fg_color="transparent")
        scroll_contenido.pack(fill="both", expand=True, padx=10, pady=5)

        # --- SECCIÓN 1: INFORMACIÓN BÁSICA ---
        info_f = ctk.CTkFrame(scroll_contenido)
        info_f.pack(fill="x", padx=10, pady=10)
        
        detalles = [
            ("Denunciante:", denunciante), 
            ("Denunciado:", f"{denun_nombre} (ID: {id_denunciado_num})"), 
            ("Tipo de contenido:", tipo), 
            ("Motivo del reporte:", motivo)
        ]

        for i, (lab, val) in enumerate(detalles):
            ctk.CTkLabel(info_f, text=lab, font=ctk.CTkFont(weight="bold")).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            ctk.CTkLabel(info_f, text=val).grid(row=i, column=1, padx=10, pady=5, sticky="w")

        # --- SECCIÓN 2: CONTENIDO ESPECÍFICO (EVIDENCIA) ---
        lbl_evidencia = ctk.CTkLabel(scroll_contenido, text="Contenido reportado / Evidencia:", font=ctk.CTkFont(weight="bold"))
        lbl_evidencia.pack(pady=(10, 0), padx=20, anchor="w")

        if tipo == 'PUBLICACION' and id_p:
            # Si es una publicación, intentamos traer sus datos actuales
            pub_data = aspects_functions.obtener_detalle_publicacion(self.conn, id_p)
            if pub_data:
                nombre_p, desc_p, cat_p, img_p, fecha_p = pub_data
                
                pub_frame = ctk.CTkFrame(scroll_contenido, fg_color=("#D5DBDB", "#2C3E50"))
                pub_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(pub_frame, text=f"Título: {nombre_p}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5, padx=10, anchor="w")
                ctk.CTkLabel(pub_frame, text=f"Categoría: {cat_p} | Fecha: {fecha_p}", font=ctk.CTkFont(size=11)).pack(padx=10, anchor="w")
                
                txt_desc = ctk.CTkTextbox(pub_frame, height=80)
                txt_desc.pack(fill="x", pady=10, padx=10)
                txt_desc.insert("0.0", desc_p if desc_p else "[Sin descripción]")
                txt_desc.configure(state="disabled")

                # BOTÓN DE ACCIÓN: Eliminar Publicación
                ctk.CTkButton(
                    pub_frame, 
                    text="Eliminar Publicación Definitivamente", 
                    fg_color="#943126", 
                    hover_color="#641E16",
                    command=lambda: self.confirmar_eliminar_publicacion(id_p, id_denunciado_num, id_rep)
                ).pack(pady=10)
            else:
                ctk.CTkLabel(scroll_contenido, text="⚠️ La publicación ya no existe o no se pudo cargar.", text_color="orange").pack(pady=10)
        
        else:
            # Para MENSAJES u otros tipos, mostramos el texto de prueba directamente
            txt_evidencia = ctk.CTkTextbox(scroll_contenido, height=150)
            txt_evidencia.pack(fill="x", padx=10, pady=10)
            txt_evidencia.insert("0.0", prueba if prueba else "No hay evidencia de texto disponible.")
            txt_evidencia.configure(state="disabled")

        # --- SECCIÓN 3: BOTONES DE ACCIÓN GENERAL ---
        btns_f = ctk.CTkFrame(self.detalle_frame, fg_color="transparent")
        btns_f.pack(side="bottom", fill="x", pady=15)

        # Botón para desestimar (solo borra el reporte)
        ctk.CTkButton(
            btns_f, 
            text="Desestimar Reporte", 
            fg_color="#7F8C8D", 
            command=lambda: self.borrar_reporte(id_rep)
        ).pack(side="left", padx=20, expand=True)
        
        # Botón para sancionar al usuario (bloqueo, etc)
        ctk.CTkButton(
            btns_f, 
            text="Sancionar Usuario", 
            fg_color="#C0392B", 
            command=lambda: self.sancionar_usuario_interfaz(denun_nombre, id_denunciado_num)
        ).pack(side="left", padx=20, expand=True)

    def sancionar_usuario_interfaz(self, nombre_usuario):
        messagebox.showinfo("Moderación", f"Funcionalidad de sanción para el usuario '{nombre_usuario}' no implementada.")

    def confirmar_eliminar_publicacion(self, id_p, id_u_num, id_r):
        if messagebox.askyesno("Confirmar Acción", "¿Está seguro de eliminar esta publicación permanentemente?"):

            if aspects_functions.eliminar_publicacion_bd(self.conn, id_u_num, id_p):
                messagebox.showinfo("Éxito", "La publicación ha sido eliminada correctamente.")
            
                if aspects_functions.eliminar_reporte(self.conn, id_r):
                    print(f"Reporte #{id_r} cerrado automáticamente.")

                self.cargar_lista_reportes()
                self.mostrar_placeholder()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la publicación. Verifique la conexión o permisos.")

    def borrar_reporte(self, id_rep):
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el reporte #{id_rep}?"):
            if aspects_functions.eliminar_reporte(self.conn, id_rep):
                messagebox.showinfo("Éxito", "Reporte eliminado.")
                self.cargar_lista_reportes()
                self.mostrar_placeholder()