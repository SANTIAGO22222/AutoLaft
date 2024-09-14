from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import pandas as pd

# Inicializar el navegador
driver = webdriver.Chrome()

# Cargar el archivo Excel con los nombres e IDs
excel_file = 'personas1.xlsx'  # Nombre del archivo a solicitar
df = pd.read_excel(excel_file)

# URL de la página web
web_url = 'https://sanctionssearch.ofac.treas.gov/'  # URL de la página web

# Iterar a través de las filas del archivo Excel
for index, row in df.iterrows():
    person_id = row['ID']  # Columna 'ID' en tu archivo Excel

    # Abrir la página web
    driver.get(web_url)

    # Localizar el cuadro de búsqueda y enviar el ID
    search_box = driver.find_element(By.ID, 'ctl00_MainContent_txtID')  # ID del cuadro de búsqueda
    search_box.clear()
    search_box.send_keys(person_id)
    
    # clic en el botón de búsqueda
    search_button = driver.find_element(By.ID, 'ctl00_MainContent_btnSearch')  # ID del botón de búsqueda
    search_button.click()

    # TIEMPO DE CARGA
    time.sleep(4)
    
    

input("Presiona Enter para cerrar el navegador...")
