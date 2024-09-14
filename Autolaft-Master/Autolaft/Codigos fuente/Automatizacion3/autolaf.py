import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.toast import ToastNotification
import pandas as pd
import time
import threading
from fpdf import FPDF

style = Style(theme='superhero')
root = style.master
root.title("Autolaft")
root.geometry("700x500")

df = None
archivo_cargado = ""

frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

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

def mostrar_notificacion():
    toast = ToastNotification(
        title="Consulta Finalizada",
        message="Se han completado las consultas.",
        duration=3000,
        bootstyle="success"
    )
    toast.show_toast()

def realizar_consulta():
    if df is None:
        messagebox.showerror("Error", "Primero debes cargar un archivo.")
        return

    def consultar():
        total = len(df)
        progreso['value'] = 0
        for i in range(total):
            time.sleep(1)
            progreso['value'] += (100 / total)
            label_progreso.config(text=f"{int(progreso['value'])}% completado")
            root.update_idletasks()
        
        if total > 0:
            messagebox.showinfo("Consulta finalizada", f"Se realizaron {total} consultas.")
            mostrar_notificacion()
            agregar_a_historial()
            alertar_resultados_positivos()

        btn_consulta['state'] = 'normal'
        btn_nuevo_proceso['state'] = 'normal'

    btn_consulta['state'] = 'disabled'
    threading.Thread(target=consultar).start()

def agregar_a_historial():
    for index, row in df.iterrows():
        persona = row.get("Personas", "Desconocido")
        id_ = row.get("ID", "Desconocido")
        resultado = "No results"
        fecha = pd.Timestamp.now().strftime("%Y-%m-%d")
        tree_historial.insert("", tk.END, values=(persona, id_, resultado, fecha))

def alertar_resultados_positivos():
    for item in tree_historial.get_children():
        values = tree_historial.item(item, 'values')
        if "No results" not in values[2]:
            tree_historial.item(item, tags=('resultado_positivo',))
    
    tree_historial.tag_configure('resultado_positivo', foreground='red')

def descargar_excel():
    if archivo_cargado:
        try:
            columnas = ["Personas", "ID", "Resultado", "Fecha de Consulta"]
            historial_data = [tree_historial.item(item)['values'] for item in tree_historial.get_children()]
            df_historial = pd.DataFrame(historial_data, columns=columnas)
            df_historial.to_excel(archivo_cargado, index=False)
            messagebox.showinfo("Éxito", f"Historial sobrescrito en {archivo_cargado}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo sobrescribir el archivo: {str(e)}")

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
            messagebox.showinfo("Éxito", f"Historial guardado en {archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

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

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

descargar_menu = tk.Menu(menu_bar, tearoff=0)
descargar_menu.add_command(label="Descargar en Excel", command=descargar_excel)
descargar_menu.add_command(label="Descargar en PDF", command=descargar_pdf)
menu_bar.add_cascade(label="Descargar", menu=descargar_menu)

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
label_progreso = ttk.Label(frame, text="0% completado", font=("Arial", 10, "bold"))
label_progreso.pack()

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

root.mainloop()





