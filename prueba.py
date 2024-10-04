import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import speech_recognition as sr
import threading
import pyttsx3
import mysql.connector
import os

class OvaApp:
    def __init__(self, root):
        # Configura la interfaz principal
        self.root = root
        self.root.title("OVA Interface")
        
        # Frame para el formulario
        form_frame = tk.Frame(root)
        form_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Nombre
        tk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1)

        # Edad
        tk.Label(form_frame, text="Edad:").grid(row=1, column=0, sticky="w")
        self.age_entry = tk.Entry(form_frame, width=30)
        self.age_entry.grid(row=1, column=1)

        # Dirección
        tk.Label(form_frame, text="Dirección:").grid(row=2, column=0, sticky="w")
        self.address_entry = tk.Entry(form_frame, width=30)
        self.address_entry.grid(row=2, column=1)

        # Teléfono
        tk.Label(form_frame, text="Teléfono:").grid(row=3, column=0, sticky="w")
        self.phone_entry = tk.Entry(form_frame, width=30)
        self.phone_entry.grid(row=3, column=1)

        # Email
        tk.Label(form_frame, text="Correo Electrónico:").grid(row=4, column=0, sticky="w")
        self.email_entry = tk.Entry(form_frame, width=30)
        self.email_entry.grid(row=4, column=1)

        # Botón para enviar datos
        self.submit_button = tk.Button(form_frame, text="Enviar Datos", command=self.send_data)
        self.submit_button.grid(row=5, column=1, pady=10)

        # Área de texto (ScrolledText) para mostrar interacciones
        self.text_area = ScrolledText(root, wrap=tk.WORD, width=50, height=10, font=("Arial", 12))
        self.text_area.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Inicializa reconocimiento de voz y síntesis de voz
        self.tts_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.language = 'es'
        self.running = False

    def speak(self, text):
        """Convierte texto a voz."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen_for_response(self):
        """Escucha la respuesta del usuario."""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.log_message("Escuchando...")
            audio = self.recognizer.listen(source)
            try:
                response = self.recognizer.recognize_google(audio, language='es-ES')
                self.log_message(f"Escuchaste: {response}")
                return response
            except sr.UnknownValueError:
                self.log_message("No se pudo entender el audio")
                self.speak("No entendí lo que dijiste. Por favor, intenta de nuevo.")
            except sr.RequestError as e:
                self.log_message(f"Error al comunicarse con el servicio de reconocimiento de voz: {e}")
                self.speak("Hubo un error al procesar tu solicitud. Inténtalo más tarde.")
            return None

    def send_data(self):
        """Envía los datos a la base de datos."""
        user_data = {
            'name': self.name_entry.get(),
            'age': self.age_entry.get(),
            'address': self.address_entry.get(),
            'phone': self.phone_entry.get(),
            'email': self.email_entry.get()
        }

        # Verifica que no haya campos vacíos
        if not all(user_data.values()):
            messagebox.showerror("Error", "Por favor, completa todos los campos.")
            return

        # Llamada a la función que guarda en la base de datos
        self.connect_to_database(user_data)

    def connect_to_database(self, user_data):
        """Conecta a la base de datos MySQL y guarda los datos."""
        try:
            connection = mysql.connector.connect(
                host=os.environ.get('DB_HOST'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                database=os.environ.get('DB_NAME'),
                port=os.environ.get('DB_PORT', '3306'),
            )
            if connection.is_connected():
                cursor = connection.cursor()
                query = """
                    INSERT INTO user_data (name, age, address, phone, email)
                    VALUES (%s, %s, %s, %s, %s)
                """
                values = (user_data['name'], user_data['age'], user_data['address'], user_data['phone'], user_data['email'])
                cursor.execute(query, values)
                connection.commit()
                self.log_message("Datos guardados en la base de datos.")
                self.speak("Tus datos se han guardado correctamente.")

        except mysql.connector.Error as err:
            self.log_message(f"Error en la base de datos: {err}")
            self.speak("No pudimos guardar los datos.")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def log_message(self, message):
        """Registra un mensaje en el área de texto."""
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = OvaApp(root)
    root.mainloop()
