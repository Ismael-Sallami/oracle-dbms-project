import os

import oracledb

class DBConnection:
    def __init__(self):
        # Credentials come from the environment. The delivered version had the
        # university account written in the file; see the README.
        self.username = os.environ.get("ORACLE_USER", "")
        self.password = os.environ.get("ORACLE_PASSWORD", "")
        self.dsn = os.environ.get("ORACLE_DSN", "oracle0.ugr.es:1521/practbd")
        self.connection = None 

    def connect(self):
        try:
            self.connection = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=self.dsn
            )
            return self.connection
        except oracledb.Error as e:
            print(f"\n❌ Error conectando a Oracle: {e}")
            return None
            
    def close(self): 
        if self.connection:
            try:
                self.connection.close()
                print("Conexión cerrada.")
            except oracledb.Error:
                pass
