import fitz  # PyMuPDF
import re

# Ruta del archivo PDF
pdf_path = "/Users/juancazas/Downloads/cif-LURJ970628UK5_s981iH5sbd.pdf"

# Función para extraer texto del PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Función para extraer datos usando expresiones regulares
def extract_data(text):
    data = {}

    # Extraer información clave de manera segura
    data["RFC"] = re.search(r"RFC:\s*([\w\d]+)", text)
    data["CURP"] = re.search(r"CURP:\s*([\w\d]+)", text)

    data["RFC"] = data["RFC"].group(1) if data["RFC"] else "No encontrado"
    data["CURP"] = data["CURP"].group(1) if data["CURP"] else "No encontrado"

    # Extraer nombre, apellido paterno y materno
    nombre = re.search(r"Nombre \(s\):\s*(.+)", text)
    apellido1 = re.search(r"Primer Apellido:\s*(.+)", text)
    apellido2 = re.search(r"Segundo Apellido:\s*(.+)", text)

    # Construir nombre completo
    nombres = [
        nombre.group(1) if nombre else "",
        apellido1.group(1) if apellido1 else "",
        apellido2.group(1) if apellido2 else ""
    ]
    data["Nombre Completo"] = " ".join(filter(None, nombres))

    # Extraer otros datos de dirección
    campos = {
        "Código Postal": r"Código Postal:\s*(\d+)",
        "Calle": r"Nombre de Vialidad:\s*(.+)",
        "Número Exterior": r"Número Exterior:\s*(\d+)",
        "Colonia": r"Nombre de la Colonia:\s*(.+)",
        "Municipio": r"Nombre del Municipio o Demarcación Territorial:\s*(.+)",
        "Estado": r"Nombre de la Entidad Federativa:\s*(.+)"
    }

    for key, pattern in campos.items():
        match = re.search(pattern, text)
        data[key] = match.group(1) if match else "No encontrado"

    return data

# Extraer texto y obtener los datos
pdf_text = extract_text_from_pdf(pdf_path)

# Depuración: ver el texto extraído del PDF
# print("Texto extraído del PDF:\n", pdf_text)

# Obtener los datos estructurados
datos_extraidos = extract_data(pdf_text)

# Mostrar resultados
for key, value in datos_extraidos.items():
    print(f"{key}: {value}")
