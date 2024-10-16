import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import pyttsx3
import re
from model import OvaModel
from PIL import Image, ImageTk


model = OvaModel()

class OvaView:
    def __init__(self, root):
        # Obtener el tamaño completo de la pantalla
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        self.root = root
        #Ajustar el tamaño completo de la pantalla
        root.geometry(f"{screen_width}x{screen_height}")
        self.root.title("OVA Interface")
        
        # Cargar la imagen original
        self.original_image = Image.open("ova/sri.jpg")
        self.background_image = ImageTk.PhotoImage(self.original_image.resize((screen_height, screen_width)))

        # Crear un Canvas y agregar la imagen de fondo
        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height)
        self.canvas.pack(fill="both", expand=True)
        
        # Colocar la imagen en el Canvas
        self.background = self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        # Redimensionar la imagen cuando se ajusta la ventana
        self.root.bind("<Configure>", self.ajustar_imagen)
        
        # Título principal del proyecto con sombreado
        self.canvas.create_text(screen_width // 2 + 3, 53, text="Ordenes de Voz Aplicadas (OVA)", font=("Arial", 26, "bold"), fill="gray")  # Sombra
        self.canvas.create_text(screen_width // 2, 50, text="Ordenes de Voz Aplicadas (OVA)", font=("Arial", 26, "bold"), fill="white")  # Texto principal

        # Frame para el formulario (colocado dentro del canvas)
        form_frame = tk.Frame(self.canvas, bg="white", bd=2)
        self.canvas.create_window(screen_width // 2, 100, window=form_frame, anchor="n")

        # Campos del formulario
        self.create_form(form_frame)

        # Text area para mostrar mensajes (colocado dentro del canvas)
        message_label_frame = tk.LabelFrame(self.canvas, text="Ventana de Mensajes del Asistente", font=("Arial", 14, "bold"))
        self.canvas.create_window(screen_width // 2, 400, window=message_label_frame, anchor="n")

        # Text area dentro del label frame
        self.text_area = ScrolledText(message_label_frame, wrap=tk.WORD, width=80, height=10, font=("Arial", 12))
        self.text_area.pack()

        # Frame para los botones (colocado dentro del canvas)
        button_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window(screen_width // 2, 620, window=button_frame, anchor="n")

        # Botones
        self.start_button = tk.Button(button_frame, bg="green", text="Iniciar OVA")
        self.start_button.grid(row=0, column=0, padx=5)

        self.reset_button = tk.Button(button_frame, text="Reiniciar", state=tk.DISABLED)
        self.reset_button.grid(row=0, column=1, padx=5)

        self.terminate_button = tk.Button(button_frame, text="Terminar OVA", state=tk.DISABLED)
        self.terminate_button.grid(row=0, column=2, padx=5)
        
        self.quit_button = tk.Button(button_frame, text="Cerrar OVA", command=self.root.destroy)
        self.quit_button.grid(row=0, column=3, padx=5)

        # Botón para enviar datos
        self.submit_button = tk.Button(form_frame, text="Enviar Datos", command=self.send_data)
        self.submit_button.grid(row=5, column=1, pady=10)
        
        # Motor de texto a voz
        self.tts_engine = self.init_tts_engine()
        self.is_speaking = False 
        
        
    def ajustar_imagen(self, event):
        if event.width > 0 and event.height > 0:
            nueva_imagen = self.original_image.resize((event.width, event.height))
            self.background_image = ImageTk.PhotoImage(nueva_imagen)
            self.canvas.itemconfig(self.background, image=self.background_image)

    def create_form(self, form_frame):
        # Título del formulario
        form_label_frame = tk.LabelFrame(form_frame, text="Formulario de Datos del Usuario", font=("Arial", 16, "bold"), padx=10, pady=10)
        form_label_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")
        
        # Nombre
        tk.Label(form_label_frame, text="Nombre:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.name_entry = tk.Entry(form_label_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Edad
        tk.Label(form_label_frame, text="Edad:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.age_entry = tk.Entry(form_label_frame, width=30)
        self.age_entry.grid(row=1, column=1, padx=10, pady=5)

        # Dirección
        tk.Label(form_label_frame, text="Dirección:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.address_entry = tk.Entry(form_label_frame, width=30)
        self.address_entry.grid(row=2, column=1, padx=10, pady=5)

        # Teléfono
        tk.Label(form_label_frame, text="Teléfono:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.phone_entry = tk.Entry(form_label_frame, width=30)
        self.phone_entry.grid(row=3, column=1, padx=10, pady=5)

        # Email
        tk.Label(form_label_frame, text="Correo Electrónico:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.email_entry = tk.Entry(form_label_frame, width=30)
        self.email_entry.grid(row=4, column=1, padx=10, pady=5)


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
                valid_change_response = False
                self.speak("Dime qué respuesta te gustaría cambiar.")
                self.log_message("Dime qué respuesta te gustaría cambiar.")

                # Mostrar preguntas y respuestas actuales
                for i, question in enumerate(questions):
                    self.log_message(f"{i+1}. {question}: {responses[question]}")
                    self.speak(f"{i+1}. {question}: {responses[question]}")

                while not valid_change_response:  # Usar bandera para controlar el flujo
                    self.speak("Indica el número de la respuesta que quieres cambiar.")
                    self.log_message("Indica el número de la respuesta que quieres cambiar.")
                    question_choice = controller.listen_for_response()

                    if question_choice:
                        question_choice_normalized = question_choice.lower()

                        # Convertir respuesta hablada a número usando el diccionario
                        if question_choice_normalized in number_mapping:
                            chosen_number = number_mapping[question_choice_normalized]

                            # Validar que el número esté dentro del rango de preguntas
                            if 1 <= chosen_number <= len(questions):
                                chosen_question = questions[chosen_number - 1]  # Ajustar índice
                                self.speak(f"Vas a cambiar la respuesta a: {chosen_question}. Por favor, di la nueva respuesta.")
                                self.log_message(f"Vas a cambiar la respuesta a: {chosen_question}. Por favor, di la nueva respuesta.")

                                valid_new_response = False
                                while not valid_new_response:
                                    new_response = controller.listen_for_response()

                                    # Validar que la nueva respuesta no esté vacía
                                    if new_response:
                                        responses[chosen_question] = new_response
                                        valid_new_response = True
                                        self.speak("Respuesta actualizada.")
                                        self.log_message(f"Respuesta actualizada para {chosen_question}: {new_response}")
                                        valid_change_response = True  # Actualización válida, salir del ciclo
                                    else:
                                        self.speak("La respuesta no puede estar vacía. Intenta nuevamente.")
                                        self.log_message("El usuario intentó dar una respuesta vacía.")
                            else:
                                self.speak("El número que elegiste no es válido. Intenta de nuevo.")
                                self.log_message("El usuario seleccionó un número fuera de rango.")
                        else:
                            self.speak("Opción no válida. Por favor, elige un número correcto.")
                            self.log_message("Opción no válida. Por favor, elige un número correcto.")
                    else:
                        self.speak("No se entendió la respuesta. Por favor, intenta nuevamente.")
                        self.log_message("Respuesta del usuario no entendida, pidiendo nuevamente.")

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
                self.speak("Por favor, responde 'sí' o 'no'.")
                self.log_message("Respuesta inválida, esperando respuesta válida.")

        # Preguntar si desea guardar los cambios
        self.speak("¿Te gustaría guardar las respuestas modificadas? Responde sí o no.")
        self.log_message("¿Te gustaría guardar las respuestas modificadas? Responde sí o no.")
        save_response = controller.listen_for_response()

        if save_response and re.search(r'(sí|si|yes)', save_response.lower()):
            controller.ask_to_save(responses)  # Guardar las respuestas
        else:
            self.speak("No se guardarán los cambios.")
            self.log_message("El usuario decidió no guardar los cambios.")

    def send_data(self,):
        user_data = self.get_form_data()
        if not all(user_data.values()):
            self.show_error("Por favor, completa todos los campos.")
            return
        model.save_user_data(user_data)
        self.log_message("Datos enviados.")