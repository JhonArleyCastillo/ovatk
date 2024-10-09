import mysql.connector
import os
from load_env import load_env
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
dotenv_path = Path(BASE_DIR)/'.env'
load_env()

class OvaModel:
    def __init__(self):
        self.connection = None
        self.connect_to_database()

    def connect_to_database(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.environ.get('DB_HOST'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                database=os.environ.get('DB_NAME'),
                port=os.environ.get('DB_PORT', '3306'),
            )
            if self.connection.is_connected():
                print("Conexión a la base de datos establecida.")
        except mysql.connector.Error as err:
            print(f"Error en la conexión: {err}")

    def save_user_data(self, user_data):
        # Verificar si la conexión existe y está activa
        if self.connection is None or not self.connection.is_connected():
            print("Error: No hay conexión a la base de datos.")
            try:
                self.connection.reconnect()  # Intentar reconectar
                print("Reconexión exitosa.")
            except mysql.connector.Error as err:
                print(f"Error al intentar reconectar: {err}")
                return False

        # Proceder a guardar los datos si la conexión es válida
        try:
            with self.connection.cursor() as cursor:
                query = """
                    INSERT INTO user_data (name, age, address, phone, email)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (user_data['name'], user_data['age'], user_data['address'], user_data['phone'], user_data['email'])

                cursor.execute(query, values)
                self.connection.commit()
                print("Datos guardados en la base de datos.")
        except mysql.connector.Error as err:
            self.connection.rollback()
            print(f"Error al guardar datos: {err}")
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False

    def get_user_data(self, user_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM user_data WHERE id = %s"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if result:
                return result  # Retorna un diccionario con los datos del usuario
            else:
                return None  # Si no encuentra al usuario, retorna None
        except mysql.connector.Error as err:
            print(f"Error al obtener los datos del usuario: {err}")
            return None
        finally:
            cursor.close()
            
    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a la base de datos cerrada.")
