import customtkinter as ctk
from tkinter import messagebox
from . import functions

class VentanaTendencias(ctk.CTkFrame):
    def __init__(self, master, conn):
        super().__init__(master)
        self.conn = conn
        
        # Título Principal
        self.lbl_titulo = ctk.CTkLabel(self, text="ANÁLISIS DE TENDENCIAS", font=("Arial", 24, "bold"))
        self.lbl_titulo.pack(pady=15)

        # --- ZONA SUPERIOR: CONSULTAS (Visualización) ---
        self.frame_listas = ctk.CTkFrame(self)
        self.frame_listas.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(self.frame_listas, text="Visualización de Datos", font=("Arial", 16, "bold"), text_color="cyan").pack(pady=5)
        
        # Botones de consulta
        self.btn_top10 = ctk.CTkButton(self.frame_listas, text="Ver Top 10 Tendencias", command=self.mostrar_top_10)
        self.btn_top10.pack(pady=5)

        self.entry_cat_buscar = ctk.CTkEntry(self.frame_listas, placeholder_text="Nombre de categoría...")
        self.entry_cat_buscar.pack(pady=5)
        self.btn_buscar_cat = ctk.CTkButton(self.frame_listas, text="Filtrar por Categoría", command=self.mostrar_por_categoria)
        self.btn_buscar_cat.pack(pady=5)
        self.btn_ver_all_cats = ctk.CTkButton(self.frame_listas, 
                                              text="Ver Todas las Categorías Existentes", 
                                              fg_color="#2E86C1",
                                              command=self.mostrar_categorias)
        self.btn_ver_all_cats.pack(pady=5)

        # Caja de texto para resultados
        self.textbox = ctk.CTkTextbox(self.frame_listas, height=150)
        self.textbox.pack(fill="x", padx=10, pady=10)

        # --- ZONA INFERIOR: GESTIÓN ADMIN (Acciones) ---
        self.frame_admin = ctk.CTkFrame(self)
        self.frame_admin.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.frame_admin, text="Gestión de Administrador", font=("Arial", 16, "bold"), text_color="orange").pack(pady=5)

        # Formulario Asignar Categoría
        self.entry_tag = ctk.CTkEntry(self.frame_admin, placeholder_text="Hashtag (ej: #Python)")
        self.entry_tag.pack(side="left", padx=5, pady=10, expand=True, fill="x")
        self.entry_cat_nueva = ctk.CTkEntry(self.frame_admin, placeholder_text="Nueva Categoría")
        self.entry_cat_nueva.pack(side="left", padx=5, pady=10, expand=True, fill="x")
        
        self.btn_asignar = ctk.CTkButton(self.frame_admin, text="Asignar", width=80, command=self.asignar_categoria)
        self.btn_asignar.pack(side="left", padx=5)

        # Botón Eliminar (Resetear)
        self.btn_reset = ctk.CTkButton(self, text="Resetear Contador de Tendencia", fg_color="#E74C3C", hover_color="#C0392B", command=self.resetear_tendencia)
        self.btn_reset.pack(pady=10)

    # --- LÓGICA DE LA INTERFAZ ---

    def mostrar_top_10(self):
        cursor = self.conn.cursor()
        filas = functions.listar_tendencias(cursor)
        self.actualizar_texto("TOP 10 TENDENCIAS GLOBALES", filas)

    def mostrar_por_categoria(self):
        cat = self.entry_cat_buscar.get().strip()
        if not cat:
            messagebox.showwarning("Atención", "Escribe una categoría para buscar.")
            return
        
        cursor = self.conn.cursor()
        filas = functions.mostrar_categoria_ordenada(cursor, cat)
        self.actualizar_texto(f"TENDENCIAS EN: {cat.upper()}", filas)

    def actualizar_texto(self, titulo, filas):
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("end", f"--- {titulo} ---\n\n")
        
        if not filas:
            self.textbox.insert("end", "No se encontraron datos.")
        else:
            for i, row in enumerate(filas, 1):
                # row[0] = Hashtag, row[1] = Menciones
                self.textbox.insert("end", f"{i}. {row[0]} -> {row[1]} menciones\n")
        
        self.textbox.configure(state="disabled")

    def asignar_categoria(self):
        tag = self.entry_tag.get().strip()
        cat = self.entry_cat_nueva.get().strip()
        
        if not tag or not cat:
            messagebox.showwarning("Faltan datos", "Debes rellenar el hashtag y la categoría.")
            return

        cursor = self.conn.cursor()
        exito, msg = functions.asignar_categoria_a_tendencia(cursor, tag, cat)
        
        if exito:
            self.conn.commit()
            messagebox.showinfo("Éxito", msg)
            self.entry_tag.delete(0, "end")
            self.entry_cat_nueva.delete(0, "end")
        else:
            messagebox.showerror("Error", msg)

    def resetear_tendencia(self):
        tag = self.entry_tag.get().strip() # Reutilizamos el campo de texto del hashtag
        if not tag:
            messagebox.showwarning("Atención", "Escribe el hashtag que deseas resetear en el campo de texto.")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de resetear el contador de {tag} a cero?"):
            cursor = self.conn.cursor()
            exito, msg = functions.eliminar_tendencia(cursor, tag)
            if exito:
                self.conn.commit()
                messagebox.showinfo("Hecho", msg)
            else:
                messagebox.showerror("Error", msg)

    def mostrar_categorias(self):
        cursor = self.conn.cursor()
        # Llamamos a la nueva función de lógica
        categorias = functions.obtener_categorias_unicas(cursor)
        
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("end", "--- CATEGORÍAS DISPONIBLES EN EL SISTEMA ---\n\n")
        
        if not categorias:
            self.textbox.insert("end", "Aún no se han asignado categorías a ningún hashtag.")
        else:
            for i, cat in enumerate(categorias, 1):
                # cat[0] es el nombre de la categoría
                nombre_cat = cat[0] if cat[0] else "Sin nombre"
                self.textbox.insert("end", f"{i}. {nombre_cat}\n")
        
        self.textbox.configure(state="disabled")
        cursor.close()