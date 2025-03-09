import jwt
import datetime
import os
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Charger les variables d'environnement
load_dotenv()

# Clé secrète pour signer les JWT
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe correspond au hachage stocké."""
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(user_id: int) -> str:
    """Crée un JWT valide pour 1 heure."""
    payload = {
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expiration dans 1 heure
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt_token(token: str):
    """Décode un JWT et retourne les informations utilisateur."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expiré
    except jwt.InvalidTokenError:
        return None  # Token invalide


security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Vérifie que le token JWT est valide et retourne l'ID utilisateur"""
    token = credentials.credentials  # Récupérer le token depuis l'en-tête Authorization
    payload = decode_jwt_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    return payload["sub"]  # Retourne l'ID utilisateur si le token est valide