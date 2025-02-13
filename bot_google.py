import os
import time
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Reemplaza "path/to/credentials.json" por la ruta a tu archivo de credenciales de servicio
credentials = ServiceAccountCredentials.from_json_keyfile_name("path/to/credentials.json", scope)
client = gspread.authorize(credentials)

# Abrir la hoja por ID (reemplaza con tu propio ID de Google Sheet)
sheet = client.open_by_key("YOUR_GOOGLE_SHEET_ID").sheet1

# Leer datos de la hoja
data = pd.DataFrame(sheet.get_all_records())

# Directorio para resultados con fecha actual
current_date = datetime.now().strftime("%Y-%m-%d")
result_dir = os.path.join("Multas", current_date)
os.makedirs(result_dir, exist_ok=True)

error_log_file = os.path.join(result_dir, "errores_procesamiento.txt")

# Configurar Selenium con Edge y webdriver_manager
service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service)

print("Iniciando el procesamiento de todas las placas...")

try:
    # Abrir la página web una vez
    driver.get("https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos")

    for index, row in data.iterrows():
        placa = row['PLACAS']
        numero_serie = row['NO. DE SERIE']
        nombre_propietario = row['PROPIETARIO']
        numero_motor = row['NO. MOTOR']

        try:
            # Esperar a que el formulario esté listo
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#placa"))
            )

            # Limpiar campos
            driver.find_element(By.CSS_SELECTOR, "#placa").clear()
            driver.find_element(By.CSS_SELECTOR, "#numeroSerie").clear()
            driver.find_element(By.CSS_SELECTOR, "#nombrePropietario").clear()
            driver.find_element(By.CSS_SELECTOR, "#numeroMotor").clear()

            # Ingresar datos en el formulario
            driver.find_element(By.CSS_SELECTOR, "#placa").send_keys(placa)
            driver.find_element(By.CSS_SELECTOR, "#numeroSerie").send_keys(numero_serie)
            driver.find_element(By.CSS_SELECTOR, "#nombrePropietario").send_keys(nombre_propietario)
            driver.find_element(By.CSS_SELECTOR, "#numeroMotor").send_keys(numero_motor)

            # Enviar el formulario
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Esperar a que se cargue la respuesta
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#frmAdeudos"))
            )

            # Extraer texto del formulario cargado
            time.sleep(5)  # Asegurar que se cargue completamente
            resultado = driver.execute_script("""
                let container = document.querySelector("#frmAdeudos");
                if (container) {
                    return container.innerText;
                }
                return "No se encontró el contenedor.";
            """)

            # Crear la salida
            salida = f"""
            Resultado para la placa {placa}:
            Número de Serie: {numero_serie}
            Propietario: {nombre_propietario}
            Número de Motor: {numero_motor}

            Texto extraído del formulario:
            {resultado.strip()}
            """

            # Guardar en un archivo
            filename = os.path.join(result_dir, f"resultado_{placa}.txt")
            with open(filename, "w", encoding="utf-8") as file:
                file.write(salida)

            print(f"Resultado guardado en '{filename}'.")

            # Volver al formulario inicial (clic en "Regresar" si existe)
            try:
                regresar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Regresar')]")
                regresar_btn.click()
            except Exception:
                print("No se encontró el botón 'Regresar'. Recargando la página...")
                driver.refresh()

        except Exception as e:
            # Guardar captura de pantalla en caso de error
            driver.save_screenshot(f"error_{placa}.png")
            error_message = f"Error al capturar texto para placa {placa}: {e}"
            print(error_message)

            # Registrar el error en el archivo de log
            with open(error_log_file, "a", encoding="utf-8") as error_log:
                error_log.write(f"{error_message}\n")

        # Pausa entre consultas para evitar bloqueos
        delay = random.randint(10, 20)
        print(f"Esperando {delay} segundos antes de la siguiente consulta...")
        time.sleep(delay)

finally:
    # Cerrar el navegador
    driver.quit()
