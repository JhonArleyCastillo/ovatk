import threading
from tkinter import messagebox
import speech_recognition as sr
import re
import tkinter as tk

class OvaController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.language = 'es'
        self.running = False
        self.ova_thread = None
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Conectar eventos de la vista con funciones del controlador
        self.view.start_button.config(command=self.start_ova)
        self.view.terminate_button.config(command=self.terminate_ova)
        self.view.reset_button.config(command=self.view.reset_system)

    def start_ova(self):
        self.running = True
        self.ova_thread = threading.Thread(target=self.run_ova)
        self.ova_thread.start()
        self.view.start_button.config(state=tk.DISABLED)  # Deshabilitar el botón "Iniciar OVA"
        self.view.terminate_button.config(state=tk.NORMAL)  # Habilitar el botón "Terminar OVA"
        self.view.reset_button.config(state=tk.DISABLED)  # Deshabilitar "Reiniciar" durante la ejecución


    def terminate_ova(self):
        self.view.log_message("OVA terminada por el usuario.")
        self.view.speak("Terminando la OVA, gracias.")

        if self.ova_thread and self.ova_thread.is_alive():
            self.ova_thread.join()
        self.view.start_button.config(state=tk.NORMAL)  # Habilitar el botón "Iniciar OVA"
        self.view.terminate_button.config(state=tk.DISABLED)  # Deshabilitar el botón "Terminar OVA"
        self.view.reset_button.config(state=tk.NORMAL)  # Habilitar el botón "Reiniciar"
        self.running = False
        
    def run_ova(self):
        self.view.log_message("<<<Inicializando OVA>>>")
        while self.running:
            self.view.speak("Bienvenido a OVA")
            self.view.speak("Di hola hola para comenzar.")
            
            self.view.log_message("Di 'Hola hola' para comenzar.")
            response = self.listen_for_response()
            if response and 'hola hola' in response.lower():
                break

        if self.running:
            self.ask_questions()

    def listen_for_response(self):
        with self.microphone as source:
            self.view.log_message("Escuchando...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            try:
                response = self.recognizer.recognize_google(audio, language='es-ES')
                self.view.log_message(f"Escuchaste: {response}")
                return response
            except sr.UnknownValueError:
                self.view.log_message("No se pudo entender el audio.")
                return None

    def ask_questions(self):
        # Hace preguntas al usuario y captura sus respuestas
        questions = [
            "¿Cuál es tu nombre y apellido?",
            "¿Cuál es tu edad?",
            "¿Cuál es tu dirección?",
            "¿Cuál es tu número de teléfono?",
            "¿Cuál es tu correo electrónico?",
        ] 
        
        responses = {}
        for question in questions:  
            valid_response = False
            while not valid_response:  
                self.view.speak(question)
                self.view.log_message(question)
                response = self.listen_for_response()
                if response:  
                    responses[question] = response
                    valid_response = True
                else:
                    self.view.speak("Por favor, repite la respuesta.")
                    self.view.log_message("Esperando una respuesta válida...")

        # Mostrar respuestas al usuario
        self.view.log_message("Aquí están tus respuestas:")
        for question, response in responses.items():
            self.view.log_message(f"{question}: {response}")
            self.view.speak(f"{question}: {response}")

        # Permitir modificar las respuestas
        self.view.fill_form_with_responses(responses)
        self.view.modify_responses(responses, questions, self)
        self.send_data()

    def ask_to_save(self, responses):
        self.view.speak("¿Deseas guardar tus respuestas? Responde sí o no.")
        response = self.listen_for_response()
        if response and re.search(r'sí|si|yes', response, re.IGNORECASE):
            self.view.log_message("Guardando datos...")
            user_data = {
                'name': responses.get("¿Cuál es tu nombre y apellido?", ""),
                'age': responses.get("¿Cuál es tu edad?", ""),
                'address': responses.get("¿Cuál es tu dirección?", ""),
                'phone': responses.get("¿Cuál es tu número de teléfono?", ""),
                'email': responses.get("¿Cuál es tu correo electrónico?", ""),
            }
            self.model.save_user_data(user_data)
            self.view.speak("Tus datos han sido guardados.")
        else:
            self.view.speak("No se guardarán los datos.")
            self.view.clear_form()


    def update_user_data(self):
        user_data = self.view.get_form_data()
        if not self.validate_data(user_data):
            return
        self.model.update_user_data(user_data)
        self.view.log_message("Datos actualizados correctamente.")
        self.view.speak("Los datos del usuario han sido actualizados.")
        self.view.clear_form()
        
    def validate_data(self, user_data):
        if not all(user_data.values()):
            self.view.log_message("Error: Todos los campos son obligatorios.")
            self.view.speak("Por favor, completa todos los campos.")
            return False

        try:
            age = int(user_data['age'])
            if age <= 0:
                self.view.log_message("Error: La edad debe ser un número positivo.")
                self.view.speak("La edad debe ser un número positivo.")
                return False
        except ValueError:
            self.view.log_message("Error: La edad debe ser un número válido.")
            self.view.speak("Por favor, ingresa una edad válida.")
            return False

        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data['email']):
            self.view.log_message("Error: El correo electrónico no es válido.")
            self.view.speak("Por favor, ingresa un correo electrónico válido.")
            return False

        return True
    
    def send_data(self):
        user_data = self.view.get_form_data()
        if not all(user_data.values()):
            self.view.show_error("Por favor, completa todos los campos.")
            return
        self.model.save_user_data(user_data)
        self.view.log_message("Datos enviados.")

