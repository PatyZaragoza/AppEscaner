from flask import Flask, render_template, request, jsonify
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de la carpeta para guardar imágenes
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

# API Key de Plant.id (asegúrate de usar tu propia clave)
API_KEY = 'RFPBSTyncR94i32QTyBLyP1lA8H8TvGLoJvn6Or5Q6BeUW18aS'

# Función para verificar la extensión de la imagen
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Función para consultar la API de Plant.id
def consultar_api(image_path):
    url = "https://api.plant.id/v2/identify"
    headers = {
        "Api-Key": API_KEY
    }
    files = {
        'image': open(image_path, 'rb')
    }
    response = requests.post(url, headers=headers, files=files)
    return response.json()

# Función para determinar si la planta está sana
def identificar_plantas(response_json):
    if response_json["is_plant"]:
        return "Planta identificada correctamente, probablemente sana."
    
    highest_probability = max(response_json["suggestions"], key=lambda x: x["probability"])["probability"]
    
    if highest_probability > 0.5:
        return "La planta tiene una alta probabilidad de ser sana."
    else:
        return "La planta no fue identificada correctamente o no es una planta conocida."

# Ruta principal para cargar y mostrar la interfaz
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para subir la imagen y procesar la respuesta de la API
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Consultar la API de Plant.id
        response_json = consultar_api(file_path)

        # Determinar si la planta está sana
        resultado = identificar_plantas(response_json)

        return jsonify({
            "mensaje": resultado,
            "imagen_url": response_json.get("images", [{}])[0].get("url", ""),
            "planta_sugerida": response_json.get("suggestions", [{}])[0].get("plant_name", "No identificada")
        })

    return "Archivo no permitido", 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
