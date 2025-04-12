from config import db
from werkzeug.security import generate_password_hash, check_password_hash

# Modelo de Usuario actualizado
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    foto_perfil = db.Column(db.String(200), nullable=True)  # Foto de perfil opcional
    telefono = db.Column(db.String(15), nullable=True)  # Nuevo campo para teléfono
    fecha_nacimiento = db.Column(db.Date, nullable=True)  # Nuevo campo para fecha de nacimiento

    def __init__(self, nombre, email, password, foto_perfil=None, telefono=None, fecha_nacimiento=None):
        self.nombre = nombre
        self.email = email
        self.password = generate_password_hash(password)
        self.foto_perfil = foto_perfil
        self.telefono = telefono
        self.fecha_nacimiento = fecha_nacimiento

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "foto_perfil": self.foto_perfil,
            "telefono": self.telefono,
            "fecha_nacimiento": self.fecha_nacimiento.strftime('%Y-%m-%d') if self.fecha_nacimiento else None
        }