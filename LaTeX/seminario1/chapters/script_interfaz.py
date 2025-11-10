import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# --- CONFIGURACIÓN DE CONEXIÓN ---
DB_HOST = "oracle0.ugr.es"
DB_PORT = 1521
DB_SERVICE = "practbd"
ORACLE_DRIVER_NAME = "{Oracle12ODBC}"

connection = None
cursor = None

# --- FUNCIONES DE BASE DE DATOS ---
def conectar_bd(user, password):
    global connection, cursor
    try:
        tns_admin_dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
        connection_string = (
            f"DRIVER={ORACLE_DRIVER_NAME};"
            f"UID={user};"
            f"PWD={password};"
            f"Dbq={tns_admin_dsn};"
        )
        connection = pyodbc.connect(connection_string)
        connection.autocommit = False
        cursor = connection.cursor()
        messagebox.showinfo("Conexión exitosa", f"Conectado como {user}")
        return True
    except Exception as e:
        messagebox.showerror("Error de conexión", str(e))
        return False


def recrear_tablas():
    if not cursor:
        messagebox.showwarning("Error", "Primero conecta a la base de datos.")
        return
    try:
        for tbl in ("DetallePedido", "Stock", "Pedido"):
            try:
                cursor.execute(f"DROP TABLE {tbl}")
            except Exception:
                pass

        cursor.execute("""
            CREATE TABLE Stock(
                CProducto number PRIMARY KEY,
                Cantidad number DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE Pedido(
                CPedido number PRIMARY KEY,
                CCliente number,
                FechaPedido date NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE DetallePedido(
                CPedido number,
                CProducto number,
                Cantidad number,
                PRIMARY KEY(CPedido, CProducto),
                FOREIGN KEY(CPedido) REFERENCES Pedido(CPedido),
                FOREIGN KEY(CProducto) REFERENCES Stock(CProducto)
            )
        """)

        stock_rows = [(i, 10 + i * 5) for i in range(1, 11)]
        cursor.executemany("INSERT INTO Stock (CProducto, Cantidad) VALUES (?, ?)", stock_rows)
        connection.commit()
        messagebox.showinfo("Éxito", "Tablas recreadas correctamente.")
    except Exception as e:
        connection.rollback()
        messagebox.showerror("Error", str(e))


def mostrar_tabla(nombre_tabla, tree):
    if not cursor:
        messagebox.showwarning("Error", "Primero conecta a la base de datos.")
        return
    try:
        cursor.execute(f"SELECT * FROM {nombre_tabla}")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]

        # limpiar la tabla
        tree.delete(*tree.get_children())
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        for row in rows:
            tree.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def crear_pedido(c_pedido, c_cliente, detalles):
    if not cursor:
        messagebox.showwarning("Error", "Primero conecta a la base de datos.")
        return
    try:
        cursor.execute("INSERT INTO Pedido (CPedido, CCliente, FechaPedido) VALUES (?, ?, SYSDATE)", (c_pedido, c_cliente))
        cursor.execute("SAVEPOINT PEDIDO_CREADO")

        for d in detalles:
            c_producto, cantidad = d
            cursor.execute("SELECT Cantidad FROM Stock WHERE CProducto = ? FOR UPDATE", (c_producto,))
            stock = cursor.fetchone()
            if not stock or stock[0] < cantidad:
                raise Exception(f"Stock insuficiente para producto {c_producto}.")
            cursor.execute("UPDATE Stock SET Cantidad = Cantidad - ? WHERE CProducto = ?", (cantidad, c_producto))
            cursor.execute("INSERT INTO DetallePedido VALUES (?, ?, ?)", (c_pedido, c_producto, cantidad))

        connection.commit()
        messagebox.showinfo("Pedido completado", f"Pedido {c_pedido} creado correctamente.")
    except Exception as e:
        connection.rollback()
        messagebox.showerror("Error en pedido", str(e))


# --- INTERFAZ PRINCIPAL ---
root = tk.Tk()
root.title("Sistema de Pedidos - Oracle ETSIIT")
root.geometry("900x600")
root.configure(bg="#f5f6fa")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11), padding=8)
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


# --- PESTAÑAS ---
tabs = ttk.Notebook(root)
tabs.pack(fill="both", expand=True, padx=10, pady=10)

frame_conexion = ttk.Frame(tabs)
frame_tablas = ttk.Frame(tabs)
frame_pedidos = ttk.Frame(tabs)

tabs.add(frame_conexion, text="Conexión")
tabs.add(frame_tablas, text="Ver Tablas")
tabs.add(frame_pedidos, text="Nuevo Pedido")


# --- PESTAÑA CONEXIÓN ---
ttk.Label(frame_conexion, text="Usuario Oracle:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
user_entry = ttk.Entry(frame_conexion, width=30)
user_entry.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(frame_conexion, text="Contraseña:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
pass_entry = ttk.Entry(frame_conexion, width=30, show="*")
pass_entry.grid(row=1, column=1, padx=10, pady=10)

ttk.Button(frame_conexion, text="Conectar", command=lambda: conectar_bd(user_entry.get(), pass_entry.get())).grid(row=2, column=0, columnspan=2, pady=10)
ttk.Button(frame_conexion, text="(Re)Crear Tablas", command=recrear_tablas).grid(row=3, column=0, columnspan=2, pady=10)


# --- PESTAÑA TABLAS ---
ttk.Label(frame_tablas, text="Selecciona tabla:").pack(pady=5)
tabla_combo = ttk.Combobox(frame_tablas, values=["Stock", "Pedido", "DetallePedido"])
tabla_combo.pack(pady=5)

tabla_tree = ttk.Treeview(frame_tablas, show="headings")
tabla_tree.pack(fill="both", expand=True, padx=10, pady=10)

ttk.Button(frame_tablas, text="Mostrar tabla", command=lambda: mostrar_tabla(tabla_combo.get(), tabla_tree)).pack(pady=5)


# --- PESTAÑA NUEVO PEDIDO ---
pedido_frame = ttk.LabelFrame(frame_pedidos, text="Datos del Pedido", padding=10)
pedido_frame.pack(fill="x", padx=10, pady=10)

ttk.Label(pedido_frame, text="Código Pedido:").grid(row=0, column=0, padx=10, pady=5)
pedido_entry = ttk.Entry(pedido_frame, width=20)
pedido_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(pedido_frame, text="Código Cliente:").grid(row=1, column=0, padx=10, pady=5)
cliente_entry = ttk.Entry(pedido_frame, width=20)
cliente_entry.grid(row=1, column=1, padx=10, pady=5)

# --- DETALLES ---
detalle_frame = ttk.LabelFrame(frame_pedidos, text="Detalles del Pedido", padding=10)
detalle_frame.pack(fill="x", padx=10, pady=10)

detalle_tree = ttk.Treeview(detalle_frame, columns=("Producto", "Cantidad"), show="headings", height=5)
detalle_tree.heading("Producto", text="Producto")
detalle_tree.heading("Cantidad", text="Cantidad")
detalle_tree.pack(fill="x", padx=10, pady=5)

detalle_data = []


def agregar_detalle():
    try:
        c_prod = int(prod_entry.get())
        cantidad = int(cant_entry.get())
        detalle_data.append((c_prod, cantidad))
        detalle_tree.insert("", "end", values=(c_prod, cantidad))
        prod_entry.delete(0, "end")
        cant_entry.delete(0, "end")
    except ValueError:
        messagebox.showwarning("Error", "Introduce valores válidos.")


ttk.Label(detalle_frame, text="Código Producto:").pack(side="left", padx=5)
prod_entry = ttk.Entry(detalle_frame, width=10)
prod_entry.pack(side="left", padx=5)

ttk.Label(detalle_frame, text="Cantidad:").pack(side="left", padx=5)
cant_entry = ttk.Entry(detalle_frame, width=10)
cant_entry.pack(side="left", padx=5)

ttk.Button(detalle_frame, text="Añadir", command=agregar_detalle).pack(side="left", padx=5)


# --- BOTÓN CREAR PEDIDO ---
ttk.Button(frame_pedidos, text="Guardar Pedido",
           command=lambda: crear_pedido(int(pedido_entry.get()), int(cliente_entry.get()), detalle_data)
           ).pack(pady=20)


# --- FUNCIÓN SALIR ---
def salir():
    global connection, cursor
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    root.destroy()


ttk.Button(root, text="Salir", command=salir).pack(pady=10)

root.mainloop()
