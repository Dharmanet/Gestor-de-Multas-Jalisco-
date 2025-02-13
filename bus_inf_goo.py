import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de credenciales y Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Reemplaza "path/to/credentials.json" por la ruta a tu archivo de credenciales
credentials = ServiceAccountCredentials.from_json_keyfile_name("path/to/credentials.json", scope)
client = gspread.authorize(credentials)

# Definir la fecha actual y la carpeta donde se encuentran los resultados
current_date = datetime.now().strftime("%Y-%m-%d")
result_dir = os.path.join("Multas", current_date)

# Obtener lista de archivos .txt en el directorio de resultados
txt_files = [os.path.join(result_dir, f) for f in os.listdir(result_dir) if f.endswith(".txt")]

data_list = []
for file_path in txt_files:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        # Extraer datos del contenido si es necesario. Aquí se guarda el contenido completo.
        data_list.append({"Archivo": os.path.basename(file_path), "Contenido": content})

# Crear un DataFrame con los datos consolidados
df = pd.DataFrame(data_list)

# Actualizar la hoja de cálculo en Google Sheets
# Reemplaza 'YOUR_GOOGLE_SHEET_ID' con el ID de tu hoja de cálculo
sheet = client.open_by_key("YOUR_GOOGLE_SHEET_ID").sheet1

# Limpiar la hoja
sheet.clear()

# Escribir encabezados y datos
headers = list(df.columns)
sheet.append_row(headers)

for _, row in df.iterrows():
    sheet.append_row(row.tolist())

print("Datos consolidados y actualizados en Google Sheets.")
