  import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# Configuración de credenciales y APIs de Google
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets"
]
# Reemplaza "path/to/credentials.json" por la ruta a tu archivo de credenciales
credentials = Credentials.from_service_account_file("path/to/credentials.json", scopes=SCOPES)
drive_service = build("drive", "v3", credentials=credentials)
docs_service = build("docs", "v1", credentials=credentials)
sheets_service = build("sheets", "v4", credentials=credentials)

# Función para subir y convertir un archivo Word a Google Docs
def upload_and_convert_word_to_google_docs(word_file_path, parent_folder_id):
    file_metadata = {
        "name": word_file_path.split("\\")[-1].replace(".docx", ""),
        "mimeType": "application/vnd.google-apps.document",
        "parents": [parent_folder_id]
    }
    media = MediaFileUpload(word_file_path, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file["id"]

# Leer datos desde Google Sheets
def read_google_sheet(sheet_id):
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range="A1:Z1000").execute()
    values = result.get("values", [])
    if not values:
        raise Exception("No se encontraron datos en el Google Sheet.")
    headers = values[0]
    rows = values[1:]
    return pd.DataFrame(rows, columns=headers)

# Crear una nueva carpeta para los oficios en Google Drive
def create_output_folder(parent_folder_id, folder_name):
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id]
    }
    folder = drive_service.files().create(body=metadata, fields="id").execute()
    return folder["id"]

# Crear un oficio desde la plantilla y guardar en Google Drive
def create_office_from_template(template_id, output_name, replacements, output_folder_id):
    # Copiar el documento de plantilla
    copy = drive_service.files().copy(
        fileId=template_id,
        body={"name": output_name, "parents": [output_folder_id]}
    ).execute()
    document_id = copy["id"]

    # Reemplazar texto en el documento
    requests = []
    for key, value in replacements.items():
        requests.append({
            "replaceAllText": {
                "containsText": {"text": f"{{{{{key}}}}}", "matchCase": True},
                "replaceText": value
            }
        })
    docs_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
    return document_id

# Configuración de IDs y rutas
# Reemplaza con el ID de tu carpeta en Google Drive y la ruta de la plantilla Word
res_multas_folder_id = "YOUR_GOOGLE_DRIVE_FOLDER_ID"
word_template_path = r"path/to/template.docx"

# Convertir Word a Google Docs
print("Convirtiendo el archivo Word a Google Docs...")
template_doc_id = upload_and_convert_word_to_google_docs(word_template_path, res_multas_folder_id)
print(f"Archivo convertido. ID del documento: {template_doc_id}")

# Solicitar el enlace del Google Sheet
sheet_url = input("Por favor, proporciona el enlace del Google Sheet con los datos: ")
sheet_id = sheet_url.split("/d/")[1].split("/")[0]

# Leer los datos del Google Sheet
data = read_google_sheet(sheet_id)

# Mostrar las columnas disponibles
print("Columnas detectadas en el Google Sheet:")
print(data.columns.tolist())

# Crear una nueva carpeta en la carpeta principal para los oficios
output_folder_name = f"Oficios-{datetime.now().strftime('%Y-%m-%d')}"
output_folder_id = create_output_folder(res_multas_folder_id, output_folder_name)

# Fecha actual en formato legible
fecha_actual = datetime.now().strftime("%d de %B del %Y")

# Generar los oficios para cada fila
for _, row in data.iterrows():
    folios = str(row.get("FOLIOS", "")) if not pd.isna(row.get("FOLIOS")) else "Sin Folios"
    replacements = {
        "FECHA": fecha_actual,
        "NUMERO_ECONOMICO": str(row.get("ECON", "Desconocido")),
        "PLACAS": str(row.get("PLACAS", "Desconocido")),
        "MARCA": str(row.get("MARCA", "Desconocido")),
        "TIPO": f'"{row.get("TIPO", "Desconocido")}"' if row.get("TIPO") else "Desconocido",
        "MODELO": str(row.get("MODELO", "Desconocido")),
        "NUMERO_SERIE": str(row.get("NO. DE SERIE", "Desconocido")),
        "NUMERO_MOTOR": str(row.get("NO. MOTOR", "Desconocido")),
        "CILINDROS": str(row.get("CILINDROS", "Desconocido")),
        "NOMBRE_RESGUARDANTE": str(row.get("RESGUARDANTE", "Desconocido")),
        "PUESTO": str(row.get("PUESTO", "Desconocido")),
        "PROPIETARIO": str(row.get("PROPIETARIO", "Desconocido")),
        "FOLIOS": folios,
    }

    output_name = f"Oficio_{replacements['PLACAS']}"
    document_id = create_office_from_template(template_doc_id, output_name, replacements, output_folder_id)
    print(f"Oficio creado: https://docs.google.com/document/d/{document_id}")

print("Todos los oficios han sido generados correctamente.")
