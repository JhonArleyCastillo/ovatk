import tkinter as tk
from controller import OvaController
from view import OvaView
from model import OvaModel

if __name__ == "__main__":
    root = tk.Tk()

    # Instancia del modelo
    model = OvaModel()
    model.connect_to_database()

    # Instancia de la vista
    view = OvaView(root)

    # Instancia del controlador
    controller = OvaController(view, model)

    root.mainloop()