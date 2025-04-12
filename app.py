import os
from flask import Flask, send_from_directory, render_template
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import db, migrate
from flasgger import Swagger
from routes.rutas import usuario_bp  # Solo el blueprint de 'usuario'

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de CORS para permitir solo el dominio específico
CORS(app, resources={
    r"/usuario/*": {"origins": "https://main.d3gd2kcl7rhrjn.amplifyapp.com"}
})

# Configuración de Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apidoc.json',  # Ruta para el archivo json de Swagger
            "rule_filter": lambda rule: True,  # Aseguramos que todas las rutas estén disponibles
            "model_filter": lambda tag: True,  # Todos los modelos disponibles
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs",  # Ruta personalizada para Swagger UI
}

# Inicialización de Swagger
Swagger(app, config=swagger_config)

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'Clave secreta para examen')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Asegúrate de configurar esta variable en .env
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite máximo de 16 MB para archivos
app.config['UPLOAD_FOLDER'] = './uploads'

# Inicializar SQLAlchemy, Flask-Migrate y JWTManager
db.init_app(app)
migrate.init_app(app, db)
jwt = JWTManager(app)

# Registrar el Blueprint de usuario
app.register_blueprint(usuario_bp, url_prefix='/usuario')

# Ruta de prueba
@app.route("/")
def home():
    return render_template("index.html")

# Ruta para servir archivos subidos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Función para crear y configurar la app
def create_app():
    return app

# Este bloque solo se ejecutará si el archivo se ejecuta directamente (no en producción con Gunicorn)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Esto es solo para pruebas locales. Para producción, usa Gunicorn.
