import pyodbc 
import getpass
from datetime import datetime
import os

# --- CONFIGURACIÓN DE CONEXIÓN A ETSIIT ---
DB_HOST = "oracle0.ugr.es"
DB_PORT = 1521
DB_SERVICE = "practbd"

# Nombre del driver ODBC de Oracle instalado en el sistema
ORACLE_DRIVER_NAME = "{Oracle12ODBC}"


# Hecho por Javier Niño Sánchez y Fernando José Gracia Choin
def get_db_connection():
    """
    Solicita al usuario sus credenciales de la ETSIIT y devuelve un
    objeto de conexión de pyodbc.
    """
    user = input(f"Introduce tu usuario de Oracle (ej. x1234567): ")
    password = getpass.getpass(f"Introduce tu contraseña: ")

    try:
        # Construimos el DSN (Data Source Name) para la conexión. Esta es la sintaxis TNS_ADMIN que usa el driver de Oracle.
        tns_admin_dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
        
        # Construimos la cadena de conexión para pyodbc
        connection_string = (
            f"DRIVER={ORACLE_DRIVER_NAME};"
            f"UID={user};"
            f"PWD={password};"
            f"Dbq={tns_admin_dsn};"
        )
        
        # Nos conectamos usando la cadena de conexión
        connection = pyodbc.connect(connection_string)
        
        # IMPORTANTE: Desactivar autocommit
        # Para controlar las transacciones manualmente con COMMIT y ROLLBACK.
        connection.autocommit = False
        
        print(f"\nConexión exitosa a {DB_HOST} como {user} usando pyodbc.")
        return connection
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        print("Asegúrate de tener el driver ODBC de Oracle correcto y que 'ORACLE_DRIVER_NAME' esté bien configurado.")
        return None 

# Hecho por Sergio Calvo González
def print_table(cursor, table_name):
    """
    Función para imprimir el contenido de una tabla de forma ordenada.
    """
    try:
        print(f"\n--- Contenido de la tabla: {table_name} ---")
        
        cursor.execute(f"SELECT * FROM {table_name}")
        
        # Obtener nombres de columnas
        col_names = [col[0] for col in cursor.description]
        if not col_names:
            print("(Tabla vacía o no existe)")
            return
            
        print(f"| {' | '.join(col_names)} |")
        
        # Imprimir filas
        rows = cursor.fetchall()
        for row in rows:
            print(f"| {' | '.join(str(item) for item in row)} |")
            
        if not rows:
            print("(Tabla vacía)")
            
    except pyodbc.Error as e:
        # El código de error para "tabla no existe" puede variar,
        # pero ORA-00942 es el error estándar de Oracle cuando no existe la tabla.
        if "ORA-00942" in str(e):
             print(f"Error: La tabla {table_name} no existe. Asegúrate de que esté creada.")
        else:
            print(f"Error al leer la tabla {table_name}: {e}") 

def show_tables(cursor):
    """
    Opción 2: Muestra el contenido de todas las tablas de la BD.
    """
    print_table(cursor, "Stock")
    print_table(cursor, "Pedido")
    print_table(cursor, "DetallePedido") 

# Hecho por todos los integrantes del grupo.
def create_new_order(cursor, connection):
    """
    Opción 1: Dar de alta un nuevo pedido.
    Esta función implementa el control de transacciones.
    """
    print("\n--- Iniciando Alta de Nuevo Pedido ---")
    
    try:
        c_pedido = int(input("Introduce el código del pedido (ej. 101): "))
        c_cliente = int(input("Introduce el código del cliente (ej. 1): "))
        fecha_actual = datetime.now()

        # --- INICIO DE LA TRANSACCIÓN ---
        # pyodbc usa '?' como marcador de parámetros
        cursor.execute(
            "INSERT INTO Pedido (CPedido, CCliente, FechaPedido) VALUES (?, ?, SYSDATE)",
            (c_pedido, c_cliente)
        )
        print(f"Pedido {c_pedido} creado en la transacción. Añada detalles.")

        # --- ESTABLECER SAVEPOINT ---
        savepoint_name = "PEDIDO_CREADO" # crea un punto de control dentro de una transacción para poder deshacer selectivamente los cambios posteriores hasta ese punto
        cursor.execute(f"SAVEPOINT {savepoint_name}") 
        print(f"Savepoint '{savepoint_name}' establecido.")

        while True:
            print("\n--- Submenú Pedido ---")
            print("1. Añadir detalle de producto")
            print("2. Eliminar TODOS los detalles de este pedido (usar Savepoint)")
            print("3. Cancelar PEDIDO COMPLETO (usar Rollback)")
            print("4. Finalizar pedido (usar Commit)")
            
            sub_opcion = input("Elige una opción (1-4): ")

            if sub_opcion == '1':
                try:
                    c_producto = int(input("  Código de producto: "))
                    cantidad_pedida = int(input("  Cantidad: "))
                    
                    if cantidad_pedida <= 0:
                        print("Error: La cantidad debe ser positiva.")
                        continue

                    # Comprobar stock. Usamos FOR UPDATE para bloquear la fila y asegurar que no sean modificadas por otro proceso hasta que la transacción actual se complet
                    cursor.execute(
                        "SELECT Cantidad FROM Stock WHERE Cproducto = ? FOR UPDATE",
                        (c_producto,)
                    )
                    stock_row = cursor.fetchone() # Este método recupera una sola fila del conjunto de resultados de una consulta ejecutada previamente

                    if stock_row and stock_row[0] >= cantidad_pedida:
                        # Hay stock, actualizamos Stock
                        cursor.execute(
                            "UPDATE Stock SET Cantidad = Cantidad - ? WHERE Cproducto = ?",
                            (cantidad_pedida, c_producto)
                        )
                        # Insertamos en Detalle-Pedido
                        cursor.execute(
                            "INSERT INTO DetallePedido (Cpedido, Cproducto, Cantidad) VALUES (?, ?, ?)",
                            (c_pedido, c_producto, cantidad_pedida)
                        )
                        print(f"Producto {c_producto} añadido al pedido {c_pedido}.")
                    else:
                        print("Error: Stock insuficiente o producto no existe.")
                    
                    show_tables(cursor)

                except pyodbc.Error as e:
                    print(f"Error al añadir detalle: {e}. Los cambios de este detalle no se aplicarán.")
                    cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                except ValueError:
                    print("Error: Introduce un número válido.")
            
            elif sub_opcion == '2':
                # --- Opción 2: Eliminar detalles (ROLLBACK TO SAVEPOINT) --- 
                cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                print(f"Rollback a savepoint '{savepoint_name}' realizado. Todos los detalles eliminados.")
                show_tables(cursor)

            elif sub_opcion == '3':
                # --- Opción 3: Cancelar pedido (ROLLBACK) ---
                connection.rollback()
                print("Rollback completo realizado. El pedido ha sido cancelado.")
                show_tables(cursor)
                return 
            
            # Diferencia entre sub_opcion '2' y '3': El 2 vuelve al savepoint definido anteriormente, mientras que el 3 deshace toda la transacción desde el inicio.

            elif sub_opcion == '4':
                # --- Opción 4: Finalizar pedido (COMMIT) --- 
                connection.commit()
                print("Commit realizado. El pedido se ha guardado permanentemente.")
                return

            else:
                print("Opción no válida. Inténtalo de nuevo.")

    except pyodbc.Error as e:
        print(f"Error CRÍTICO en la transacción del pedido: {e}")
        print("Se desharán todos los cambios de este pedido.")
        connection.rollback() # Rollback de seguridad
    except ValueError:
        print("Error: El código de pedido y cliente deben ser números.")
        print("La transacción no se ha iniciado.") 
        
        

def delete_and_create_tables(cursor, connection):
    """
    Elimina las tablas existentes (si existen) y crea de nuevo Stock, Pedido y DetallePedido.
    Inserta 10 tuplas predefinidas en Stock y hace commit al final.
    """
    try:
        print("\n--- Borrando tablas (si existen) ---")
        for tbl in ("DetallePedido", "Stock", "Pedido"):
            try:
                cursor.execute(f"DROP TABLE {tbl}")
                print(f"Tabla {tbl} eliminada.")
            except pyodbc.Error as e:
                # Ignorar si la tabla no existe
                if "ORA-00942" in str(e) or "table or view does not exist" in str(e).lower():
                    print(f"Tabla {tbl} no existe. Se omite.")
                else:
                    raise

        print("\n--- Creando tablas ---")
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
        print("Tablas creadas correctamente.")

        # Insertar 10 tuplas predefinidas en Stock
        stock_rows = [(i, 10 + i * 5) for i in range(1, 11)]  # ejemplos de cantidades
        cursor.executemany("INSERT INTO Stock (CProducto, Cantidad) VALUES (?, ?)", stock_rows)
        connection.commit()
        print("Insertadas 10 tuplas en Stock. Commit realizado.")

    except pyodbc.Error as e:
        print(f"Error al (re)crear tablas: {e}")
        try:
            connection.rollback()
            print("Rollback realizado por error.")
        except Exception:
            pass

# Jesús Rodríguez González e Ismael Sallami Moreno
def main():
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            return 

        cursor = connection.cursor()

        while True:
            print("\n--- Menú Principal del Sistema de Pedidos (pyodbc) ---")
            print("0. Borrado y nueva creación de las tablas e inserción de 10 tuplas predefinidas en el código en la tabla Stock.")
            print("1. Dar de alta nuevo pedido")
            print("2. Mostrar contenido de las tablas")
            print("3. Salir")
            
            opcion = input("Selecciona una opción (0-3): ")

            if opcion == '0':
                delete_and_create_tables(cursor, connection);
            elif opcion == '1':
                create_new_order(cursor, connection)
            elif opcion == '2':
                show_tables(cursor)
            elif opcion == '3':
                print("Saliendo del programa...") 
                break
            else:
                print("Opción no válida. Por favor, elige de 1 a 3.")

    except pyodbc.Error as e:
        print(f"Error inesperado de base de datos: {e}")
    finally:
        if 'cursor' in locals() and cursor: # Vemos si existe cursor y no es None
            cursor.close()
        if connection:
            connection.close()
            print("Conexión a la BD cerrada.")

if __name__ == "__main__":
    main()
