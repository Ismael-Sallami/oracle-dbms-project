import tkinter as tk
from tkinter import messagebox, ttk
import pyodbc
# Importamos las funciones del backend
from mensajeria.functions import (
    listar_usuarios, enviar_mensaje, eliminar_mensaje, 
    visualizar_conversacion, des_archivar_usuario
)

# --- VARIABLES GLOBALES ---
ID_USUARIO_ACTIVO = None 
connection = None

# ==========================================
# 1. VENTANA DE LOGIN (SIN CONTRASEÑA)
# ==========================================
class VentanaLogin:
    def __init__(self, root, conn):
        self.root = root
        self.conn = conn
        self.root.title("Acceso Rápido")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        
        tk.Label(self.root, text="SISTEMA DDSI", font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(self.root, text="Introduce tu ID de Usuario:").pack()
        self.entry_user = tk.Entry(self.root, font=("Arial", 11), justify='center')
        self.entry_user.pack(pady=10)
        self.entry_user.focus_set()

        self.btn_login = tk.Button(
            self.root, text="Entrar", bg="#007bff", fg="white",
            font=("Arial", 10, "bold"), width=15, command=self.validar_login
        )
        self.btn_login.pack(pady=10)

    def validar_login(self):
        uid = self.entry_user.get().strip()

        if not uid:
            messagebox.showwarning("Atención", "Introduce un ID")
            return

        try:
            cursor = self.conn.cursor()
            # Verificamos que el usuario exista en la tabla USUARIO
            cursor.execute("SELECT NOMBREUSUARIO FROM USUARIO WHERE IDUSUARIO = ?", (uid,))
            fila = cursor.fetchone()

            if fila:
                global ID_USUARIO_ACTIVO
                ID_USUARIO_ACTIVO = int(uid)
                nombre_real = fila[0]
                
                messagebox.showinfo("Bienvenido", f"Hola, {nombre_real}")
                
                self.root.destroy()
                root_main = tk.Tk()
                MensajeriaApp(root_main, self.conn)
                root_main.mainloop()
            else:
                messagebox.showerror("Error", "Ese ID de usuario no existe")
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error de Consulta", f"Error al buscar usuario: {e}")

# ==========================================
# 2. APLICACIÓN PRINCIPAL (LISTA DE CONTACTOS)
# ==========================================
class MensajeriaApp:
    def __init__(self, root, db_connection):
        self.root = root
        self.conn = db_connection
        self.root.title(f"Mensajería - Sesión: ID {ID_USUARIO_ACTIVO}")
        self.root.geometry("400x550")

        self.viendo_archivados = False 
        self.usuarios_cargados = [] 

        self._init_ui()
        self.cargar_usuarios()

    def _init_ui(self):
        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack(fill=tk.X)

        self.btn_toggle = tk.Button(frame_top, text="Ver Archivados", command=self.toggle_archivados)
        self.btn_toggle.pack()
        
        self.lbl_titulo = tk.Label(frame_top, text="Contactos Activos", font=("Arial", 12, "bold"))
        self.lbl_titulo.pack(pady=5)

        frame_list = tk.Frame(self.root, padx=10)
        frame_list.pack(expand=True, fill=tk.BOTH)

        self.listbox_users = tk.Listbox(frame_list, font=("Arial", 11), selectbackground="#cfe2ff")
        self.listbox_users.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        scrolly = tk.Scrollbar(frame_list, command=self.listbox_users.yview)
        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_users.config(yscrollcommand=scrolly.set)

        frame_btn = tk.Frame(self.root, pady=15)
        frame_btn.pack(fill=tk.X)

        tk.Button(frame_btn, text="Abrir Chat", bg="#d1e7dd", command=self.abrir_chat, width=15).pack(side=tk.LEFT, padx=20)
        self.btn_arch = tk.Button(frame_btn, text="Archivar", bg="#f8d7da", command=self.archivar, width=15)
        self.btn_arch.pack(side=tk.RIGHT, padx=20)

    def cargar_usuarios(self):
        self.listbox_users.delete(0, tk.END)
        self.usuarios_cargados = listar_usuarios(self.conn, ID_USUARIO_ACTIVO, self.viendo_archivados)
        for _, nombre in self.usuarios_cargados:
            self.listbox_users.insert(tk.END, f"  👤 {nombre}")

    def toggle_archivados(self):
        self.viendo_archivados = not self.viendo_archivados
        self.lbl_titulo.config(text="Contactos Archivados" if self.viendo_archivados else "Contactos Activos")
        self.btn_toggle.config(text="Ver Activos" if self.viendo_archivados else "Ver Archivados")
        self.btn_arch.config(text="Desarchivar" if self.viendo_archivados else "Archivar")
        self.cargar_usuarios()

    def abrir_chat(self):
        idx = self.listbox_users.curselection()
        if idx:
            uid, nombre = self.usuarios_cargados[idx[0]]
            VentanaChat(self.root, self.conn, uid, nombre)

    def archivar(self):
        idx = self.listbox_users.curselection()
        if idx:
            uid, _ = self.usuarios_cargados[idx[0]]
            des_archivar_usuario(self.conn, ID_USUARIO_ACTIVO, uid)
            self.cargar_usuarios()

# ==========================================
# 3. VENTANA DE CHAT (DISEÑO NOMBRE ARRIBA / MSJ ABAJO)
# ==========================================
class VentanaChat:
    def __init__(self, parent, conn, id_destino, nombre_destino):
        self.window = tk.Toplevel(parent)
        self.conn = conn
        self.id_destino = id_destino
        self.window.title(f"Chat con {nombre_destino}")
        self.window.geometry("450x600")
        
        self.mapeo_mensajes = [] 

        self._init_ui()
        self.cargar_mensajes()

    def _init_ui(self):
        frame_chat = tk.Frame(self.window, padx=5, pady=5)
        frame_chat.pack(expand=True, fill=tk.BOTH)

        self.lb_chat = tk.Listbox(frame_chat, font=("Segoe UI", 10), selectbackground="#fff3cd")
        self.lb_chat.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        scrolly = tk.Scrollbar(frame_chat, command=self.lb_chat.yview)
        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb_chat.config(yscrollcommand=scrolly.set)

        tk.Button(self.window, text="Borrar Mensaje Seleccionado", bg="#ffcccb", 
                  command=self.borrar).pack(fill=tk.X, padx=10, pady=5)

        frame_in = tk.Frame(self.window, pady=10)
        frame_in.pack(fill=tk.X)
        self.entry = tk.Entry(frame_in, font=("Arial", 11))
        self.entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
        self.entry.bind("<Return>", lambda e: self.enviar())
        tk.Button(frame_in, text="Enviar", bg="#007bff", fg="white", command=self.enviar).pack(side=tk.RIGHT, padx=10)

    def cargar_mensajes(self):
        self.lb_chat.delete(0, tk.END)
        self.mapeo_mensajes = []
        mensajes = visualizar_conversacion(self.conn, ID_USUARIO_ACTIVO, self.id_destino)

        for id_msg, id_remit, nombre, texto in mensajes:
            # 1. Nombre del remitente
            nombre_label = "● TÚ" if id_remit == ID_USUARIO_ACTIVO else f"● {nombre.upper()}"
            self.lb_chat.insert(tk.END, nombre_label)
            self.lb_chat.itemconfig(tk.END, fg="#888888", font=("Arial", 8, "italic"))
            self.mapeo_mensajes.append(None) 

            # 2. Contenido del mensaje
            self.lb_chat.insert(tk.END, f"   {texto}")
            self.lb_chat.itemconfig(tk.END, font=("Arial", 10, "bold"))
            self.mapeo_mensajes.append((id_msg, id_remit)) 
            
            # 3. Espacio
            self.lb_chat.insert(tk.END, "")
            self.mapeo_mensajes.append(None)

        self.lb_chat.yview(tk.END)

    def enviar(self):
        txt = self.entry.get().strip()
        if txt:
            exito, _ = enviar_mensaje(self.conn, ID_USUARIO_ACTIVO, self.id_destino, txt)
            if exito:
                self.entry.delete(0, tk.END)
                self.cargar_mensajes()

    def borrar(self):
        idx = self.lb_chat.curselection()
        if idx and self.mapeo_mensajes[idx[0]]:
            id_m, id_r = self.mapeo_mensajes[idx[0]]
            if id_r == ID_USUARIO_ACTIVO:
                if messagebox.askyesno("Confirmar", "¿Borrar mensaje?"):
                    eliminar_mensaje(self.conn, ID_USUARIO_ACTIVO, id_m)
                    self.cargar_mensajes()
            else:
                messagebox.showwarning("Error", "No puedes borrar mensajes de otros")

# ==========================================
# INICIO DEL PROGRAMA Y CONEXIÓN ORACLE
# ==========================================
DB_HOST = "oracle0.ugr.es"
DB_PORT = 1521
DB_SERVICE = "practbd"
ORACLE_DRIVER_NAME = "{Oracle12ODBC}"

def conectar_bd():
    # Ajusta aquí tus credenciales de Oracle de la UGR
    USER = "ORACLE_USER" 
    PASSWORD = "ORACLE_USER"
    
    try:
        tns_admin_dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
        connection_string = (
            f"DRIVER={ORACLE_DRIVER_NAME};"
            f"UID={USER};"
            f"PWD={PASSWORD};"
            f"Dbq={tns_admin_dsn};"
        )
        conn = pyodbc.connect(connection_string)
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"Error de conexión a Oracle: {e}")
        return None

if __name__ == "__main__":
    # Intentar conexión real
    connection = conectar_bd()
    
    # Si falla la conexión real, usamos el Mock para que puedas probar la interfaz
    if connection is None:
        print("CUIDADO: No se pudo conectar a Oracle.")
        exit()

    root = tk.Tk()
    VentanaLogin(root, connection)
    root.mainloop()