import pyodbc
import getpass
import sys

class DBConnection:
    _instance = None
    _connection = None

    # Configuración de la ETSIIT (Hardcoded o variable de entorno)
    DB_HOST = "oracle0.ugr.es"
    DB_PORT = 1521
    DB_SERVICE = "practbd"
    ORACLE_DRIVER_NAME = "{Oracle12ODBC}" # Aseguraos de que todos tenéis el mismo driver instalado

    def __new__(cls):
        # Patrón Singleton: Garantiza una única instancia
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """
        Establece la conexión si no existe ya.
        Pide credenciales por consola la primera vez.
        """
        if self._connection and not self._connection.closed:
            return self._connection

        print("\n=== CONEXIÓN A BASE DE DATOS ORACLE ===")
        try:
            user = input("Usuario Oracle (ej. x1234567): ")
            password = getpass.getpass("Contraseña: ")
            
            dsn = f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_SERVICE}"
            conn_str = f"DRIVER={self.ORACLE_DRIVER_NAME};UID={user};PWD={password};Dbq={dsn};"
            
            self._connection = pyodbc.connect(conn_str)
            self._connection.autocommit = False # IMPORTANTE: Control manual de transacciones
            
            print("✅ Conexión establecida correctamente.\n")
            return self._connection
            
        except pyodbc.Error as e:
            print(f"\n❌ ERROR CRÍTICO DE CONEXIÓN: {e}")
            print("Verifica si estás en la VPN de la UGR o tienes el driver ODBC instalado.")
            return None

    def close(self):
        if self._connection:
            self._connection.close()
            print("🔒 Conexión cerrada.")

    def get_connection(self):
        # Método helper para obtener la conexión activa
        return self._connection