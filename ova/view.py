import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import pyttsx3
import re
class OvaView:
    def __init__(self, root):
        self.root = root
        self.root.title("OVA Interface")

        # Frame para el formulario
        form_frame = tk.Frame(root)
        form_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Campos del formulario
        self.create_form(form_frame)

        # Text area para mostrar mensajes
        self.text_area = ScrolledText(root, wrap=tk.WORD, width=50, height=20, font=("Arial", 12))
        self.text_area.pack(pady=10, padx=10)

        # Frame para los botones
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)  # Colocamos el contenedor de botones debajo del área de texto


        # Botón 1: Iniciar OVA
        self.start_button = tk.Button(button_frame, text="Iniciar OVA")
        self.start_button.grid(row=0, column=0, padx=5)  # Botón 1 en la primera posición

        # Botón 2: Reiniciar
        self.reset_button = tk.Button(button_frame, text="Reiniciar", command=self.reset_system, state=tk.DISABLED)
        self.reset_button.grid(row=0, column=1, padx=5)  # Botón 2 en la segunda posición

        # Botón 3: Terminar OVA
        self.terminate_button = tk.Button(button_frame, text="Terminar OVA", command=self.terminate_system, state=tk.DISABLED)
        self.terminate_button.grid(row=0, column=2, padx=5)  # Botón 3 en la tercera posición
 
        # Botón para enviar datos
        self.submit_button = tk.Button(form_frame, text="Enviar Datos")
        self.submit_button.grid(row=5, column=1, pady=10)
        
        # Motor de texto a voz
        self.tts_engine = self.init_tts_engine()
        self.is_speaking = False 
    def create_form(self, form_frame):
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

    def reset_system(self):
        """
        Restablece la aplicación al estado inicial. Detiene cualquier operación y limpia los campos.
        """
        self.clear_form()
        self.log_message("El sistema ha sido reiniciado.")
        self.start_button.config(state=tk.NORMAL)  # Habilitar botón "Iniciar OVA"
        self.terminate_button.config(state=tk.DISABLED)  # Deshabilitar el botón "Terminar"
        self.reset_button.config(state=tk.DISABLED)  # Deshabilitar el botón "Reiniciar"

    def terminate_system(self):
        """
        Termina la OVA y deshabilita los botones de reiniciar y terminar.
        """
        self.clear_form()
        self.log_message("OVA terminada por el usuario.")
        self.start_button.config(state=tk.NORMAL)  # Habilitar botón "Iniciar OVA"
        self.terminate_button.config(state=tk.DISABLED)  # Deshabilitar el botón "Terminar"
        self.reset_button.config(state=tk.NORMAL)  # Habilitar el botón "Reiniciar"


    def init_tts_engine(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)
        return engine

    def speak(self, text):
        if not self.is_speaking:
            self.is_speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            self.is_speaking = False
        else:
            print("El motor TTS ya está hablando, espera a que termine.")

    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)

    def get_form_data(self):
        return {
            'name': self.name_entry.get(),
            'age': self.age_entry.get(),
            'address': self.address_entry.get(),
            'phone': self.phone_entry.get(),
            'email': self.email_entry.get(),
        }

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def clear_form(self):
        """
        Limpia los campos del formulario en la vista.
        """
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)


    def fill_form_with_responses(self, responses):
        """
        Llena el formulario con las respuestas almacenadas en el diccionario de respuestas.
        """
        # Asignar valores del diccionario responses a los campos del formulario
        self.name_entry.delete(0, tk.END)  # Limpiar el campo antes de insertar el valor
        self.name_entry.insert(0, responses.get("¿Cuál es tu nombre y apellido?", ""))

        self.age_entry.delete(0, tk.END)
        self.age_entry.insert(0, responses.get("¿Cuál es tu edad?", ""))

        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, responses.get("¿Cuál es tu dirección?", ""))

        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, responses.get("¿Cuál es tu número de teléfono?", ""))

        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, responses.get("¿Cuál es tu correo electrónico?", ""))

        # Mostrar mensaje en el área de texto
        self.log_message("Formulario rellenado con las respuestas del usuario.")
        
        # Posteriormente, se envian los datos a la base de datos con el botón "Enviar Datos"
        
    def modify_responses(self, responses, questions, controller):
        # Diccionario de mapeo para convertir las respuestas de número en palabras
        number_mapping = {
            '1': 1, 'uno': 1, 'primera': 1, 'la primera': 1,
            '2': 2, 'dos': 2, 'segunda': 2, 'la segunda': 2,
            '3': 3, 'tres': 3, 'tercera': 3, 'la tercera': 3,
            '4': 4, 'cuatro': 4, 'cuarta': 4, 'la cuarta': 4,
            '5': 5, 'cinco': 5, 'quinta': 5, 'la quinta': 5
        }

        # Ciclo para permitir al usuario modificar respuestas múltiples veces si así lo desea
        modifying_responses = True
        while modifying_responses:
            self.speak("¿Te gustaría cambiar alguna de tus respuestas? Responde sí o no.")
            self.log_message("¿Te gustaría cambiar alguna de tus respuestas? Responde sí o no.")
            change_response = controller.listen_for_response()

            if change_response and re.search(r'(sí|si|yes)', change_response.lower()):
                valid_change_response = True
                self.speak("Dime qué respuesta te gustaría cambiar.")
                self.log_message("Dime qué respuesta te gustaría cambiar.")

                # Mostrar preguntas actuales y respuestas para que el usuario elija
                for i, question in enumerate(questions):
                    self.log_message(f"{i+1}. {question}: {responses[question]}")
                    self.speak(f"{i+1}. {question}: {responses[question]}")

                valid_question_choice = False
                while not valid_question_choice:
                    self.speak("Indica el número de la respuesta que quieres cambiar.")
                    self.log_message("Indica el número de la respuesta que quieres cambiar.")
                    question_choice = controller.listen_for_response()

                    if question_choice:
                        question_choice_normalized = question_choice.lower()

                        # Convertir la respuesta hablada a un número usando el diccionario
                        if question_choice_normalized in number_mapping:
                            chosen_number = number_mapping[question_choice_normalized]
                            chosen_question = questions[chosen_number - 1]  # Ajustar índice
                            self.speak(f"Vas a cambiar la respuesta a: {chosen_question}. Por favor, di la nueva respuesta.")
                            self.log_message(f"Vas a cambiar la respuesta a: {chosen_question}. Por favor, di la nueva respuesta.")

                            valid_new_response = False
                            while not valid_new_response:
                                new_response = controller.listen_for_response()
                                if new_response:
                                    responses[chosen_question] = new_response
                                    valid_new_response = True
                                    self.speak("Respuesta actualizada.")
                                    self.log_message(f"Respuesta actualizada para {chosen_question}: {new_response}")
                                    break
                        else:
                            self.speak("Opción no válida. Por favor, elige un número correcto.")
                            self.log_message("Opción no válida. Por favor, elige un número correcto.")
                    else:
                        self.speak("No se entendió la respuesta. Por favor, intenta nuevamente.")

                # Preguntar si quiere modificar otra respuesta después de modificar una
                self.speak("¿Te gustaría cambiar otra respuesta? Responde sí o no.")
                self.log_message("¿Te gustaría cambiar otra respuesta? Responde sí o no.")
                change_another = controller.listen_for_response()

                # Verificar si el usuario quiere cambiar otra respuesta
                if not (change_another and re.search(r'(sí|si|yes)', change_another.lower())):
                    modifying_responses = False  # Salir del ciclo si no quiere cambiar otra respuesta

            elif change_response and re.search(r'(no|no quiero|no necesito)', change_response.lower()):
                modifying_responses = False
                self.speak("Gracias, no se realizarán cambios.")
                self.log_message("El usuario decidió no realizar cambios.")
            else:
                self.speak("Por favor, responde 'si' o 'no'.")
                self.log_message("Esperando una respuesta válida...")

        # Después de modificaciones, preguntar si desea guardar las respuestas
        controller.ask_to_save(responses)