import oracledb

class DBConnection:
    def __init__(self):
        self.username = "ORACLE_USER"   
        self.password = "ORACLE_USER"  # CAMBIAR
        self.dsn = "oracle0.ugr.es:1521/practbd"
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
