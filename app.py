import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import db, migrate
from flasgger import Swagger
from routes.rutas import usuario_bp

load_dotenv()

def create_app():
    app = Flask(__name__)

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
    
    Swagger(app, config=swagger_config)

    # Configuraciones principales
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'Clave secreta para examen')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Asegúrate de configurar esta variable en .env
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite máximo de 16 MB para archivos
    app.config['UPLOAD_FOLDER'] = './uploads'
    
    # Inicializar extensiones
    CORS(app)  # Habilitar CORS
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)
    
    # Registrar blueprints
    app.register_blueprint(usuario_bp, url_prefix='/usuario')
    
    # Ruta para la verificación de la API
    @app.route('/')
    def home():
        return 'API en correcto funcionamiento'
    
    # Ruta para servir archivos subidos
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return app

# Este bloque solo se ejecutará si el archivo se ejecuta directamente (no en producción con Gunicorn)
if __name__ == '__main__':
    app = create_app()
    # En producción, usamos host='0.0.0.0' para que sea accesible desde fuera de la EC2
    app.run(debug=False, host='0.0.0.0', port=5000)  # Esto es solo para pruebas locales. Para producción, usa Gunicorn.
