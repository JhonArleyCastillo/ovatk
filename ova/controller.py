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
        self.view.send_data()

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
            
            # Validar los datos antes de guardarlos
            if self.validate_data(user_data):
                print("Datos a guardar:", user_data)
                self.model.save_user_data(user_data)
                self.view.speak("Tus datos han sido guardados.")
            else:
                self.view.speak("No se guardarán los datos debido a errores de validación.")
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
        # Diccionario para mapear números en palabras a su representación numérica
        number_word_mapping = {
            # Números del 1 al 19
            'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9,
            'diez': 10, 'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14, 'quince': 15, 'dieciséis': 16,
            'diecisiete': 17, 'dieciocho': 18, 'diecinueve': 19,

            # Decenas del 20 al 99
            'veinte': 20, 'treinta': 30, 'cuarenta': 40, 'cincuenta': 50, 'sesenta': 60, 'setenta': 70, 'ochenta': 80, 'noventa': 90,

            # Combinaciones de decenas (veintiuno, treinta y uno, etc.)
            'veintiuno': 21, 'veintidós': 22, 'veintitrés': 23, 'veinticuatro': 24, 'veinticinco': 25, 'veintiséis': 26,
            'veintisiete': 27, 'veintiocho': 28, 'veintinueve': 29,

            # Para formar combinaciones del 31 al 99
            'y': None  # 'y' se usa para separar las decenas de las unidades
        }

        # Añadir números del 31 al 99 formados con "y"
        for decena, decena_value in {'treinta': 30, 'cuarenta': 40, 'cincuenta': 50, 'sesenta': 60, 'setenta': 70, 'ochenta': 80, 'noventa': 90}.items():
            for unidad, unidad_value in {'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9}.items():
                number_word_mapping[f'{decena} y {unidad}'] = decena_value + unidad_value

        # Validar nombre: Primer letra mayúscula, resto minúscula
        if 'name' in user_data:
            user_data['name'] = ' '.join([word.capitalize() for word in user_data['name'].split()])
        
        # Validar que todos los campos tengan algún valor
        if not all(user_data.values()):
            self.view.log_message("Error: Todos los campos son obligatorios.")
            self.view.speak("Por favor, completa todos los campos.")
            return False

        try:
                # Convertir número en palabras a su equivalente numérico
                age_input = user_data['age'].lower()  # Convertir la entrada a minúsculas para facilitar la búsqueda

                # Revisar si el input está en el diccionario de mapeo
                if age_input in number_word_mapping:
                    age = number_word_mapping[age_input]
                else:
                    # Si no es una palabra exacta, buscar números dentro del string
                    age_match = re.search(r'(\d+)', age_input)
                    if age_match:
                        age = int(age_match.group(1))  # Obtener solo el número
                    else:
                        raise ValueError

                # Validar que la edad sea positiva
                if age <= 0:
                    self.view.log_message("Error: La edad debe ser un número positivo.")
                    self.view.speak("La edad debe ser un número positivo.")
                    return False

                # Guardar la edad como número en el diccionario de respuestas
                user_data['age'] = str(age)  # Guardar solo la parte numérica

        except ValueError:
                self.view.log_message("Error: La edad debe ser un número válido.")
                self.view.speak("Por favor, ingresa una edad válida.")
                return False
            
        # Validar dirección: Convertir la primera letra de cada palabra a mayúscula
        if 'address' in user_data:
            user_data['address'] = ' '.join([word.capitalize() for word in user_data['address'].split()])

        # Validar número de teléfono: Convertir palabras en números y eliminar espacios
        if 'phone' in user_data:
            phone_input = user_data['phone'].lower().replace(' ', '')  # Convertir a minúsculas y eliminar espacios

            # Convertir palabras a números
            for word, digit in number_word_mapping.items():
                phone_input = phone_input.replace(word, digit)

            # Eliminar cualquier carácter que no sea dígito (letras, símbolos, etc.)
            phone_input = re.sub(r'\D', '', phone_input)

            # Validar que el número tenga al menos 10 dígitos
            if len(phone_input) < 10:
                self.view.log_message("Error: El número de teléfono debe tener al menos 10 dígitos.")
                self.view.speak("El número de teléfono debe contener al menos 10 dígitos.")
                return False

            # Guardar el número validado
            user_data['phone'] = phone_input

        # Validar correo electrónico: Eliminar espacios y verificar el formato
        if 'email' in user_data:
            user_data['email'] = user_data['email'].replace(' ', '')

            # Lista de dominios válidos (puedes agregar o modificar según necesidad)
            valid_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', "soy.sena.edu.co", "sena.edu.co"]

            if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data['email']):
                self.view.log_message("Error: El correo electrónico no tiene un formato válido.")
                self.view.speak("Por favor, ingresa un correo electrónico válido con un '@' y un dominio válido.")
                return False

            # Verificar que el dominio del correo sea válido
            domain = user_data['email'].split('@')[-1]
            if domain not in valid_domains:
                self.view.log_message(f"Error: El dominio '{domain}' no está permitido.")
                self.view.speak("Por favor, ingresa un correo electrónico con un dominio válido, como 'gmail.com' o 'yahoo.com'.")
                return False

        # Si todas las validaciones pasan
        self.view.log_message("Validaciones exitosas. Los datos son correctos.")
        self.view.speak("Los datos han sido validados correctamente.")
        return True
    


