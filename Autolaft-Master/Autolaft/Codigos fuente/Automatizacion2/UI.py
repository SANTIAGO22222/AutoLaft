import tkinter as tk
from tkinter import Menu

# Crear la ventana principal
root = tk.Tk()
root.title("Autolaft")
root.geometry("300x400")  # Tamaño reducido de la ventana (ancho x alto)

# Crear una barra de menú
menu_bar = Menu(root)

# Añadir opciones al menú
ver_menu = Menu(menu_bar, tearoff=0)
ver_menu.add_command(label="Ver archivo")
ver_menu.add_command(label="Ver configuración")
menu_bar.add_cascade(label="Ver", menu=ver_menu)

config_menu = Menu(menu_bar, tearoff=0)
config_menu.add_command(label="Preferencias")
config_menu.add_command(label="Ajustes avanzados")
menu_bar.add_cascade(label="Configuración", menu=config_menu)

historial_menu = Menu(menu_bar, tearoff=0)
historial_menu.add_command(label="Ver historial")
historial_menu.add_command(label="Borrar historial")
menu_bar.add_cascade(label="Historial de reportes", menu=historial_menu)

# Configurar la barra de menú en la ventana principal
root.config(menu=menu_bar)

# Crear un marco centrado que contenga el botón "Insertar archivo"
frame = tk.Frame(root, bg="white")
frame.place(relx=0.5, rely=0.3, anchor="center", relwidth=0.7, relheight=0.3)

# Botón para "Insertar archivo"
btn_insertar = tk.Button(frame, text="Insertar archivo", height=2, width=20, font=("Arial", 12))
btn_insertar.pack(pady=20)

# Botón para "Realizar consulta" justo debajo
btn_consulta = tk.Button(root, text="Realizar consulta", height=2, width=15, font=("Arial", 10))
btn_consulta.place(relx=0.5, rely=0.65, anchor="center")

# Botón para "Cancelar" paralelo al botón "Realizar consulta"
btn_cancelar = tk.Button(root, text="Cancelar", height=2, width=15, font=("Arial", 10))
btn_cancelar.place(relx=0.5, rely=0.75, anchor="center")

# Botón adicional para "Generar Archivo"
btn_generar = tk.Button(root, text="Generar Archivo", height=2, width=15, font=("Arial", 10))
btn_generar.place(relx=0.5, rely=0.85, anchor="center")

# Ejecutar el bucle principal de la aplicación
root.mainloop()