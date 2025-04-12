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
        "specs_route": "/apidocs",  # Ruta personalizada para Swagger UI (cambiar a '/apidocs')
    }
    
    Swagger(app, config=swagger_config)

    # Configuraciones principales
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'Clave secreta para examen')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite máximo de 16 MB para archivos
    app.config['UPLOAD_FOLDER'] = './uploads'
    
    # Inicializar extensiones
    CORS(app)
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

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
