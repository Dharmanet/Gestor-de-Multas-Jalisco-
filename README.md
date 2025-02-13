# Automatización de Gestión de Multas

## Descripción

Este proyecto optimiza la administración de multas vehiculares en el sector público mediante la automatización de tareas repetitivas, mejorando la eficiencia, transparencia y reduciendo significativamente el tiempo de trabajo. Utiliza Python, Selenium, Pandas y las APIs de Google (Sheets, Drive y Docs) para capturar datos de formularios web, consolidarlos en Google Sheets y generar oficios automáticamente en Google Docs.

## Características Principales

- **Automatización del procesamiento de datos** desde una página web de adeudos vehiculares.
- **Integración con Google Sheets** para almacenar y consolidar la información.
- **Generación automática de oficios** con Google Docs API a partir de plantillas predefinidas.
- **Reducción de tiempos administrativos**, ahorrando hasta tres días de trabajo en el área de vehículos.

## Requisitos

- **Python** 3.8 o superior.
- **APIs de Google habilitadas** en Google Cloud:
  - Google Sheets API
  - Google Drive API
  - Google Docs API
- **Credenciales JSON** de autenticación con permisos adecuados.
- **Dependencias instaladas** desde `requirements.txt`.

## Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu_usuario/gestion-multas.git
   cd gestion-multas
   ```
2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configura las credenciales:**
   - Agrega tu archivo de credenciales (`credentials.json`) en la ruta indicada.
   - Modifica los scripts para incluir tu `GOOGLE_SHEET_ID` y `GOOGLE_DRIVE_FOLDER_ID`.

## Uso

### 1. Procesamiento de Resultados
Ejecuta el siguiente comando para capturar y procesar la información de la página web:
```bash
python bot_google.py
```

### 2. Análisis y Subida de Datos
Ejecuta este comando para consolidar los datos y actualizarlos en Google Sheets:
```bash
python bus_inf_goo.py
```

### 3. Generación de Oficios
Para generar los oficios personalizados a partir de una plantilla, ejecuta:
```bash
python crea_doc_goo.py
```

## Estructura del Proyecto

```
gestion-multas/
├── bot_google.py            # Procesa resultados desde el formulario web
├── bus_inf_goo.py           # Consolida datos y actualiza Google Sheets
├── crea_doc_goo.py          # Genera oficios automáticos en Google Docs
├── requirements.txt         # Lista de dependencias
├── README.md                # Documentación del proyecto
└── template.docx            # Plantilla de oficios (editable)
```

## Contribuciones

Si deseas contribuir, abre un _issue_ o _pull request_ en GitHub. Todas las mejoras son bienvenidas para optimizar el proceso y ampliar su aplicación.

## Licencia

Este proyecto está disponible bajo la [MIT License](LICENSE).

**#Automatización #GestónPública #Transparencia #InnovaciónDigital**

