import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.toast import ToastNotification
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import threading
from datetime import datetime
from fpdf import FPDF

# Configuración de Tkinter y estilo
style = Style(theme='superhero')
root = style.master
root.title("Autolaft")
root.geometry("700x500")

df = None
archivo_cargado = ""

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

# Tabla para mostrar el historial de consultas
tree_historial = ttk.Treeview(root, columns=("Personas", "ID", "Resultado", "Fecha de Consulta"), show="headings")
tree_historial.heading("Personas", text="Personas")
tree_historial.heading("ID", text="ID")
tree_historial.heading("Resultado", text="Resultado")
tree_historial.heading("Fecha de Consulta", text="Fecha de Consulta")
tree_historial.column("Personas", anchor=tk.W, width=200)
tree_historial.column("ID", anchor=tk.W, width=100)
tree_historial.column("Resultado", anchor=tk.W, width=150)
tree_historial.column("Fecha de Consulta", anchor=tk.W, width=150)
tree_historial.pack(fill=tk.BOTH, expand=True)

# Función para abrir archivo Excel
def abrir_archivo():
    global df, archivo_cargado
    archivo_cargado = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
    if archivo_cargado:
        try:
            df = pd.read_excel(archivo_cargado)
            label_archivo.config(text=f"Archivo cargado: {archivo_cargado.split('/')[-1]}")
            btn_consulta['state'] = 'normal'
            btn_nuevo_proceso['state'] = 'disabled'
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")

# Función para mostrar notificación al finalizar consulta
def mostrar_notificacion(total_procesados):
    mensaje = f"Se han completado las consultas.\nTotal de datos procesados: {total_procesados}"
    toast = ToastNotification(
        title="Consulta Finalizada",
        message=mensaje,
        duration=5000,
        bootstyle="success"
    )
    toast.show_toast()

# Función para realizar consulta utilizando Selenium
def realizar_consulta():
    global df, archivo_cargado
    if df is None:
        messagebox.showerror("Error", "Primero debes cargar un archivo.")
        return

    # Configuración de Selenium (Headless)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    web_url = 'https://sanctionssearch.ofac.treas.gov/'

    def consultar():
        total = len(df)
        progreso['value'] = 0
        resultados = []
        fechas_consulta = []
        resultados_positivos = 0
        consultas_positivas = []

        for i, row in df.iterrows():
            person_id = row['ID']
            person_name = row['Personas']

            driver.get(web_url)
            search_box = driver.find_element(By.ID, 'ctl00_MainContent_txtID')
            search_box.clear()
            search_box.send_keys(person_id)
            search_button = driver.find_element(By.ID, 'ctl00_MainContent_btnSearch')
            search_button.click()

            try:
                # Usar WebDriverWait para esperar hasta que el elemento de resultados esté presente
                results_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'scrollResults'))
                )
                results_text = results_element.text if results_element.text else "No results"
            except Exception as e:
                results_text = "No results"

            resultados.append(results_text)
            fechas_consulta.append(datetime.now().strftime("%Y-%m-%d"))

            if results_text != "Your search has not returned any results.":
                resultados_positivos += 1
                consultas_positivas.append(f"ID: {person_id}, Persona: {person_name}")

            # Insertar datos en la tabla
            tree_historial.insert("", "end", values=(person_name, person_id, results_text, fechas_consulta[-1]))

            progreso['value'] += (100 / total)
            label_progreso.config(text=f"{int(progreso['value'])}% completado")
            root.update_idletasks()

        df['Resultado'] = resultados
        df['Fecha de Consulta'] = fechas_consulta
        driver.quit()
        mostrar_notificacion(total)
        
        if consultas_positivas:
            messagebox.showinfo("Coincidencias Encontradas", "\n".join(consultas_positivas))

        btn_consulta['state'] = 'normal'
        btn_nuevo_proceso['state'] = 'normal'

    btn_consulta['state'] = 'disabled'
    threading.Thread(target=consultar).start()

# Función para iniciar nuevo proceso
def nuevo_proceso():
    respuesta = messagebox.askokcancel(
        "Advertencia",
        "Recuerde descargar los datos antes de realizar un nuevo proceso. ¿Desea continuar?",
        icon='warning'
    )
    if respuesta:
        tree_historial.delete(*tree_historial.get_children())
        label_archivo.config(text="No se ha cargado ningún archivo")
        progreso['value'] = 0
        label_progreso.config(text="0% completado")
        btn_consulta['state'] = 'disabled'
        btn_nuevo_proceso['state'] = 'disabled'
        global df, archivo_cargado
        df = None
        archivo_cargado = ""

# Función para descargar en Excel
def descargar_excel():
    if df is None:
        messagebox.showerror("Error", "No hay datos para exportar.")
        return

    archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos Excel", "*.xlsx")])
    if archivo:
        try:
            columnas = ["Personas", "ID", "Resultado", "Fecha de Consulta"]
            historial_data = [tree_historial.item(item)['values'] for item in tree_historial.get_children()]
            df_historial = pd.DataFrame(historial_data, columns=columnas)
            df_historial.to_excel(archivo, index=False)
            messagebox.showinfo("Éxito", "Historial exportado a Excel.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

# Función para descargar en PDF
def descargar_pdf():
    archivo = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])
    if archivo:
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Historial de Reportes", ln=True, align='C')

            pdf.set_font("Arial", size=10)
            historial_data = [tree_historial.item(item)['values'] for item in tree_historial.get_children()]
            for row in historial_data:
                row_data = f"Persona: {row[0]}, ID: {row[1]}, Resultado: {row[2]}, Fecha: {row[3]}"
                pdf.cell(200, 10, txt=row_data, ln=True, align='L')

            pdf.output(archivo)
            messagebox.showinfo("Éxito", "Historial exportado a PDF.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

# Menú para exportar datos
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

descargar_menu = tk.Menu(menu_bar, tearoff=0)
descargar_menu.add_command(label="Exportar Excel", command=descargar_excel)
descargar_menu.add_command(label="Exportar PDF", command=descargar_pdf)
menu_bar.add_cascade(label="Exportar", menu=descargar_menu)

# Labels, Botones y Elementos de la interfaz gráfica
label_archivo = ttk.Label(frame, text="No se ha cargado ningún archivo", font=("Arial", 10, "bold"))
label_archivo.pack(pady=10)

btn_insertar = ttk.Button(frame, text="Insertar archivo", command=abrir_archivo)
btn_insertar.pack(pady=10)

btn_consulta = ttk.Button(frame, text="Realizar consulta", command=realizar_consulta, state='disabled')
btn_consulta.pack(pady=10)

btn_nuevo_proceso = ttk.Button(frame, text="Nuevo Proceso", command=nuevo_proceso, state='disabled')
btn_nuevo_proceso.pack(pady=10)

progreso = ttk.Progressbar(frame, orient='horizontal', length=300, mode='determinate')
progreso.pack(pady=10)
label_progreso = ttk.Label(frame, text="0% completado")
label_progreso.pack(pady=10)

root.mainloop()
