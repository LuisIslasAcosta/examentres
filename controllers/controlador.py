from models.modelo import Usuario
from flask import jsonify
from config import db
from flask_jwt_extended import create_access_token

# Crear usuario con Teléfono y Fecha de Nacimiento
def create_usuario(nombre, email, password, foto_perfil=None, telefono=None, fecha_nacimiento=None):
    try:
        nuevo_usuario = Usuario(nombre, email, password, foto_perfil=foto_perfil, telefono=telefono, fecha_nacimiento=fecha_nacimiento)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify(nuevo_usuario.to_dict()), 201
    except Exception as e:
        print(f"ERROR {e}")
        return jsonify({'msg': 'Error al crear el nuevo usuario'}), 500

# Actualizar foto de perfil
def actualizar_foto_perfil(user_id, foto_perfil):
    try:
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({'msg': 'Usuario no encontrado'}), 404
        
        usuario.foto_perfil = foto_perfil
        db.session.commit()
        return jsonify({'msg': 'Foto de perfil actualizada exitosamente', 'usuario': usuario.to_dict()}), 200
    except Exception as e:
        print(f"ERROR {e}")
        return jsonify({'msg': 'Error al actualizar la foto de perfil'}), 500

# Actualizar datos del usuario (incluyendo Teléfono y Fecha de Nacimiento)
def actualizar_datos_usuario(user_id, foto_perfil=None, telefono=None, fecha_nacimiento=None):
    try:
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({'msg': 'Usuario no encontrado'}), 404
        
        if foto_perfil:
            usuario.foto_perfil = foto_perfil
        if telefono:
            usuario.telefono = telefono
        if fecha_nacimiento:
            usuario.fecha_nacimiento = fecha_nacimiento
        
        db.session.commit()
        return jsonify({'msg': 'Datos actualizados exitosamente', 'usuario': usuario.to_dict()}), 200
    except Exception as e:
        print(f"ERROR {e}")
        return jsonify({'msg': 'Error al actualizar los datos del usuario'}), 500


# Obtener catálogo de fotos predefinidas
def obtener_catalogo_fotos():
    fotos_predefinidas = [
        "https://example.com/foto1.jpg",
        "https://example.com/foto2.jpg",
        "https://example.com/foto3.jpg",
        "https://example.com/foto4.jpg"
    ]
    return jsonify({"fotos": fotos_predefinidas}), 200

# Inicio de sesión con JWT
def login_usuario(email, password):
    try:
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(password):
            access_token = create_access_token(identity=usuario.id)
            return jsonify({
                'access_token': access_token,
                'usuario': {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "email": usuario.email,
                    "telefono": usuario.telefono,
                    "fecha_nacimiento": usuario.fecha_nacimiento.strftime('%Y-%m-%d') if usuario.fecha_nacimiento else None
                }
            })
        return jsonify({"msg": "Datos incorrectos"}), 401
    except Exception as e:
        print(f"ERROR {e}")
        return jsonify({'msg': 'Error en el inicio de sesión'}), 500

# Obtener todos los usuarios (incluye Teléfono y Fecha de Nacimiento)
def get_all_usuarios():
    try:
        usuarios = []
        for usuario in Usuario.query.all():
            user_data = usuario.to_dict()
            if user_data.get("foto_perfil"):
                # Asegura que la URL sea completa
                user_data["foto_perfil"] = f"http://127.0.0.1:5000{user_data['foto_perfil']}"
            usuarios.append(user_data)
        return jsonify(usuarios), 200
    except Exception as error:
        print(f"ERROR: {error}")
        return jsonify({'msg': 'Error al obtener los usuarios'}), 500