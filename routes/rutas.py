from flask import Blueprint, jsonify, request, send_from_directory
from controllers.controlador import create_usuario, login_usuario, get_all_usuarios
from controllers.controlador import actualizar_datos_usuario, obtener_catalogo_fotos
from models.modelo import Usuario, db
from werkzeug.utils import secure_filename
import os

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/', methods=['POST'])
def user_store():
    """
    Crear un nuevo usuario
    ---
    tags:
      - Usuarios
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - nombre
            - password
          properties:
            email:
              type: string
            nombre:
              type: string
            password:
              type: string
            foto_perfil:
              type: string
            telefono:
              type: string
            fecha_nacimiento:
              type: string
              format: date
    responses:
      201:
        description: Usuario creado exitosamente
      400:
        description: Faltan campos requeridos
      500:
        description: Error del servidor
    """
    data = request.get_json()
    email = data.get('email')
    nombre = data.get('nombre')
    password = data.get('password')
    foto_perfil = data.get('foto_perfil', None)
    telefono = data.get('telefono', None)
    fecha_nacimiento = data.get('fecha_nacimiento', None)

    if not all([email, nombre, password]):
        return jsonify({"error": "Rellena todos los campos obligatorios (nombre, email, password)"}), 400

    return create_usuario(nombre, email, password, foto_perfil, telefono, fecha_nacimiento)


@usuario_bp.route('/actualizar', methods=['PUT'])
def update_datos_usuario():
    """
    Actualizar datos del usuario
    ---
    tags:
      - Usuarios
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - id
          properties:
            id:
              type: integer
            foto_perfil:
              type: string
            telefono:
              type: string
            fecha_nacimiento:
              type: string
              format: date
    responses:
      200:
        description: Datos actualizados exitosamente
      400:
        description: ID del usuario requerido
      404:
        description: Usuario no encontrado
      500:
        description: Error del servidor
    """
    data = request.get_json()
    user_id = data.get('id')
    foto_perfil = data.get('foto_perfil', None)
    telefono = data.get('telefono', None)
    fecha_nacimiento = data.get('fecha_nacimiento', None)

    if not user_id:
        return jsonify({"error": "El ID del usuario es requerido"}), 400

    return actualizar_datos_usuario(user_id, foto_perfil, telefono, fecha_nacimiento)


@usuario_bp.route('/catalogo-fotos', methods=['GET'])
def obtener_catalogo_fotos_route():
    """
    Obtener catálogo de fotos predefinidas
    ---
    tags:
      - Usuarios
    responses:
      200:
        description: Lista de fotos predefinidas
        schema:
          type: object
          properties:
            fotos:
              type: array
              items:
                type: string
      500:
        description: Error del servidor
    """
    return obtener_catalogo_fotos()


@usuario_bp.route('/iniciar', methods=['POST'])
def login_usuario_route():
    """
    Iniciar sesión
    ---
    tags:
      - Autenticación
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Inicio de sesión exitoso
        schema:
          type: object
          properties:
            access_token:
              type: string
            usuario:
              type: object
              properties:
                id:
                  type: integer
                nombre:
                  type: string
                email:
                  type: string
                telefono:
                  type: string
                fecha_nacimiento:
                  type: string
      400:
        description: Faltan datos
      401:
        description: Credenciales inválidas
      500:
        description: Error del servidor
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "El email y la contraseña son requeridos para iniciar sesión"}), 400
    
    return login_usuario(email, password)


@usuario_bp.route('/todos', methods=['GET'])
def get_usuarios():
    """
    Obtener todos los usuarios
    ---
    tags:
      - Usuarios
    responses:
      200:
        description: Lista de usuarios
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              nombre:
                type: string
              email:
                type: string
              telefono:
                type: string
              fecha_nacimiento:
                type: string
              foto_perfil:
                type: string
      500:
        description: Error al obtener usuarios
    """
    return get_all_usuarios()


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@usuario_bp.route('/subir-foto', methods=['POST'])
def subir_foto_perfil():
    """
    Subir foto de perfil
    ---
    tags:
      - Usuarios
    consumes:
      - multipart/form-data
    parameters:
      - name: id
        in: formData
        type: string
        required: true
        description: ID del usuario
      - name: foto_perfil
        in: formData
        type: file
        required: true
        description: Imagen del usuario
    responses:
      200:
        description: Foto subida exitosamente
      400:
        description: Datos inválidos o archivo no permitido
      404:
        description: Usuario no encontrado
      500:
        description: Error en el servidor
    """
    try:
        user_id = request.form.get('id')
        foto = request.files.get('foto_perfil')

        if not user_id or not foto:
            return jsonify({"error": "El ID del usuario y la foto son requeridos"}), 400

        if not allowed_file(foto.filename):
            return jsonify({"error": "Tipo de archivo no permitido"}), 400

        ext = os.path.splitext(secure_filename(foto.filename))[1]
        ruta_foto = f"/uploads/{user_id}{ext}"
        foto.save("." + ruta_foto)

        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({"msg": "Usuario no encontrado"}), 404

        usuario.foto_perfil = ruta_foto
        db.session.commit()

        return jsonify({"msg": "Foto subida exitosamente", "foto_perfil": ruta_foto}), 200
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"msg": f"Error al subir la foto: {str(e)}"}), 500


@usuario_bp.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    """
    Obtener archivo subido
    ---
    tags:
      - Archivos
    parameters:
      - name: filename
        in: path
        type: string
        required: true
        description: Nombre del archivo
    responses:
      200:
        description: Archivo servido correctamente
      404:
        description: Archivo no encontrado
    """
    return send_from_directory('./uploads', filename)
