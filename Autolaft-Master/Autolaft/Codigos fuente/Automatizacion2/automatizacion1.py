from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from datetime import datetime

# Configuración para ejecutar el navegador en modo headless
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

# Inicializar el navegador en modo headless
driver = webdriver.Chrome(options=chrome_options)

# Cargar el archivo Excel con los nombres e IDs
excel_file = 'personas1.xlsx'  # Cambia esto al nombre de tu archivo Excel
df = pd.read_excel(excel_file)

# Copia del DataFrame original
df_copia = df.copy()

# URL de la página web
web_url = 'https://sanctionssearch.ofac.treas.gov/'  # URL de la página web

# Inicializar una lista para almacenar los resultados y fechas de consulta
resultados = []
fechas_consulta = []

# Iterar a través de las filas del archivo Excel
for index, row in df.iterrows():
    person_id = row['ID']  # Columna 'ID' en tu archivo Excel

    # Abrir la página web
    driver.get(web_url)

    # Localizar el cuadro de búsqueda y enviar el ID
    search_box = driver.find_element(By.ID, 'ctl00_MainContent_txtID')  # ID del cuadro de búsqueda
    search_box.clear()
    search_box.send_keys(person_id)
    
    # Dar clic en el botón de búsqueda
    search_button = driver.find_element(By.ID, 'ctl00_MainContent_btnSearch')  # ID del botón de búsqueda
    search_button.click()

    # Esperar un poco para que la página cargue (ajusta el tiempo según sea necesario)
    time.sleep(1)
    
    # Obtener los resultados y mostrarlos en la consola
    results_element = driver.find_element(By.ID, 'scrollResults')
    results_text = results_element.text
    print(results_text)
    
    # Agregar los resultados y la fecha actual a las listas
    resultados.append(results_text)
    fechas_consulta.append(datetime.now())

# Agregar los resultados y fechas a la copia del DataFrame
df_copia['Resultado'] = resultados
df_copia['Fecha de Consulta'] = fechas_consulta

# Guardar la copia de resultados en un nuevo archivo Excel
excel_copia = 'copia_resultados.xlsx'  # Nombre del nuevo archivo Excel
df_copia.to_excel(excel_copia, index=False)
print("Copia de resultados guardada en", excel_copia)

# Limpiar el DataFrame original para nuevas búsquedas
df['Resultado'] = ""
df['Fecha de Consulta'] = ""
df.to_excel(excel_file, index=False)
print("Excel original limpiado para nuevas búsquedas")

# Cerrar el navegador
driver.quit()

input("Presiona Enter para cerrar el script...")
