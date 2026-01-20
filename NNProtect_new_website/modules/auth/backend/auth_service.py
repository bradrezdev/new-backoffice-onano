import jwt
import bcrypt
import datetime
from typing import Dict, Any
from database.users import Users
from NNProtect_new_website.utils.timezone_mx import get_mexico_now
from NNProtect_new_website.utils.environment import Environment

class AuthService:
    """Servicio para manejo de tokens JWT y encriptación."""

    @staticmethod
    def get_jwt_secret() -> str:
        """Obtiene la clave JWT de forma segura."""
        return Environment.get_jwt_secret()

    @classmethod
    def create_jwt_token(cls, user: Users) -> str:
        """Crea un JWT token para el usuario autenticado."""
        try:
            secret = cls.get_jwt_secret()
            
            user_id = int(user.id) if user.id is not None else 0
            username = f"{user.first_name} {user.last_name}".strip() if user.first_name else "unknown"
            
            # Expiración: 60 minutos desde ahora (MX Time)
            # Convertimos a timestamp entero para cumplir con estándar JWT "numeric"
            exp_timestamp = int((get_mexico_now() + datetime.timedelta(minutes=60)).timestamp())
            
            payload = {
                "id": user_id,
                "username": username,
                "exp": exp_timestamp,
            }
            
            token = jwt.encode(payload, secret, algorithm="HS256")
            
            # Asegurar retorno string
            if isinstance(token, bytes):
                return token.decode('utf-8')
            return str(token)
            
        except Exception as e:
            # Log seguro: No imprimir secretos ni payloads sensibles
            print(f"Error generando JWT Auth: {str(e)}")
            raise e

    @classmethod
    def decode_jwt_token(cls, token: str) -> Dict[str, Any]:
        """Decodifica un token JWT."""
        if not token or "." not in token:
            return {}
            
        try:
            secret = cls.get_jwt_secret()
            return jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            print("Token expirado")
            return {}
        except Exception as e:
            print(f"Error decodificando JWT: {str(e)}")
            return {}

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        if not password or not hashed:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
