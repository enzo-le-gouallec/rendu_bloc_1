from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from auth import hash_password, verify_password, create_jwt_token, decode_jwt_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Modèle pour l'inscription et la connexion
class UserSchema(BaseModel):
    email: str
    name: str
    firstname: str
    password: str

# Modèle pour la mise à jour du profil (besoin du token)
class UpdateProfileSchema(BaseModel):
    name: Optional[str] = None
    firstname: Optional[str] = None
    token : str


# Modèle pour la suppression d'un compte (besoin du token)
class DeleteAccountSchema(BaseModel):
    token: str

# Inscription d'un utilisateur
@router.post("/register/")
def register(user: UserSchema):
    """
    Inscription d'un nouvel utilisateur.

    Cette route permet d'enregistrer un nouvel utilisateur dans la base de données en effectuant les opérations suivantes :
    
    - Établir une connexion à la base de données.
    - Vérifier si l'email fourni existe déjà. Si oui, retourne une erreur 400.
    - Hacher le mot de passe de l'utilisateur via la fonction `hash_password`.
    - Insérer l'utilisateur dans la table `users`.
    - Retourner un message de succès en cas d'inscription réussie.

    **Corps de la requête (Request Body) :**
    - **user** (UserSchema) : Un objet JSON contenant les informations de l'utilisateur à inscrire.  
      Les champs attendus incluent :
      - `email` : L'adresse email de l'utilisateur.
      - `name` : Le nom de l'utilisateur.
      - `firstname` : Le prénom de l'utilisateur.
      - `password` : Le mot de passe de l'utilisateur (qui sera haché avant insertion).

    **Réponses :**
    - **200 OK** : Inscription réussie.  
      Exemple de réponse :
      ```json
      {
        "message": "Utilisateur créé avec succès"
      }
      ```
    - **400 Bad Request** : L'email fourni est déjà utilisé.
    - **500 Internal Server Error** : Erreur de connexion à la base de données.

    """
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")
    
    try:
        with connection.cursor() as cursor:
            # Vérifier si l'email existe déjà
            cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            existing_user = cursor.fetchone()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email déjà utilisé")

            # Insérer l'utilisateur avec un mot de passe haché
            hashed_password = hash_password(user.password)
            cursor.execute(
                "INSERT INTO users (email, name, firstname, password) VALUES (%s, %s, %s, %s)",
                (user.email, user.name, user.firstname, hashed_password)
            )
            connection.commit()
        
        return {"message": "Utilisateur créé avec succès"}
    
    finally:
        connection.close()

# 2. Connexion (génère un token JWT)
class LoginSchema(BaseModel):
    email: str
    password: str

@router.post("/login/")
def login(user: LoginSchema):
    """
    Connexion d'un utilisateur.

    Cette route permet à un utilisateur de se connecter en vérifiant ses identifiants. Le processus est le suivant :

    - Établir une connexion à la base de données.
    - Rechercher l'utilisateur correspondant à l'email fourni.
    - Vérifier que l'utilisateur existe et que le mot de passe fourni correspond au mot de passe haché stocké.
    - En cas de succès, générer et retourner un token JWT pour l'utilisateur.

    **Corps de la requête (Request Body) :**
    - **user** (LoginSchema) : Un objet JSON contenant :
      - `email` : L'adresse email de l'utilisateur.
      - `password` : Le mot de passe de l'utilisateur.

    **Réponses :**
    - **200 OK** : Connexion réussie avec renvoi du token JWT.
      Exemple de réponse :
      ```json
      {
          "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      }
      ```
    - **401 Unauthorized** : Les identifiants sont incorrects (email ou mot de passe invalide).
    - **500 Internal Server Error** : Erreur de connexion à la base de données.

    """
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, password FROM users WHERE email = %s", (user.email,))
            user_data = cursor.fetchone()
            if not user_data or not verify_password(user.password, user_data["password"]):
                raise HTTPException(status_code=401, detail="Identifiants incorrects")

            # Générer un JWT
            token = create_jwt_token(user_data["id"])
        
        return {"token": token}
    
    finally:
        connection.close()

# Déconnexion (suppression côté client)
@router.post("/logout/")
def logout():
    """
    Déconnexion d'un utilisateur.

    Cette route permet de déconnecter un utilisateur. 
    La déconnexion est principalement gérée côté client, et cette route retourne uniquement un message de confirmation.

    **Corps de la requête (Request Body) :**
      Aucun paramètre n'est requis.

    **Réponses :**
      - **200 OK** : Retourne un message confirmant la déconnexion.
        Exemple de réponse :
        ```json
        {
            "message": "Déconnexion réussie (à gérer côté client)"
        }
        ```
    """
    return {"message": "Déconnexion réussie (à gérer côté)"}

# Suppression d'un compte (seulement si connecté)
@router.delete("/delete_account/")
def delete_account(delete_data: DeleteAccountSchema):
    """
    Suppression du compte utilisateur.

    Cette route permet à un utilisateur de supprimer son compte à partir de son token JWT.
    Le processus est le suivant :
    
    - Le token JWT fourni dans le corps de la requête est décodé pour récupérer l'identifiant de l'utilisateur (clé "sub").
    - Si le token est invalide ou expiré, une erreur 401 est retournée.
    - Établit une connexion à la base de données.
    - Supprime l'utilisateur correspondant dans la table `users`.
    - Retourne un message de confirmation en cas de suppression réussie.

    **Corps de la requête (Request Body) :**
    - **delete_data** (DeleteAccountSchema) : Un objet JSON contenant :
      - `token` : Le token JWT de l'utilisateur.

    **Réponses :**
    - **200 OK** : Le compte a été supprimé avec succès.
      Exemple de réponse :
      ```json
      {
          "message": "Compte supprimé avec succès"
      }
      ```
    - **401 Unauthorized** : Le token est invalide ou expiré.
    - **500 Internal Server Error** : Erreur de connexion à la base de données.

    """
    token_payload = decode_jwt_token(delete_data.token)
    if not token_payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    user_id = token_payload["sub"]

    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
        
        return {"message": "Compte supprimé avec succès"}
    
    finally:
        connection.close()



@router.put("/update_profile/")
def update_profile(update_data: UpdateProfileSchema):
    """
    Met à jour le profil de l'utilisateur.

    Cette route permet de mettre à jour certaines informations du profil de l'utilisateur, en fonction des champs fournis.
    Le processus est le suivant :

    - Décoder le token JWT pour récupérer l'identifiant de l'utilisateur (clé "sub").
    - Vérifier la connexion à la base de données.
    - Vérifier l'existence de l'utilisateur dans la base de données.
    - Construire dynamiquement une requête SQL de mise à jour en fonction des champs non nuls dans `update_data`
      (les champs mis à jour possibles sont `name` et `firstname`).
    - Exécuter la mise à jour et valider les modifications dans la base de données.

    **Corps de la requête (Request Body) :**
    - **update_data** (UpdateProfileSchema) : Un objet JSON contenant :
      - `token` : Le token JWT de l'utilisateur.
      - `name` (optionnel) : Le nouveau nom de l'utilisateur.
      - `firstname` (optionnel) : Le nouveau prénom de l'utilisateur.

    **Réponses :**
    - **200 OK** : Retourne un message de confirmation.
      Exemple de réponse :
      ```json
      {
          "message": "Profil mis à jour avec succès"
      }
      ```
    - **400 Bad Request** : Aucun champ n'a été spécifié pour la mise à jour.
    - **401 Unauthorized** : Token invalide ou expiré.
    - **404 Not Found** : Utilisateur non trouvé.
    - **500 Internal Server Error** : Erreur de connexion à la base de données.
    """
    # Décoder le token JWT
    token_payload = decode_jwt_token(update_data.token)
    if not token_payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    user_id = token_payload["sub"]

    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        with connection.cursor() as cursor:
            # Vérifier si l'utilisateur existe
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            existing_user = cursor.fetchone()
            if not existing_user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

            # Construire dynamiquement la requête de mise à jour
            update_fields = []
            update_values = []

            if update_data.name:
                update_fields.append("name = %s")
                update_values.append(update_data.name)

            if update_data.firstname:
                update_fields.append("firstname = %s")
                update_values.append(update_data.firstname)

            # S'assurer qu'au moins un champ est mis à jour
            if not update_fields:
                raise HTTPException(status_code=400, detail="Aucune modification spécifiée")

            # Ajouter l'ID utilisateur pour la condition WHERE
            update_values.append(user_id)

            # Construire la requête SQL
            sql_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(sql_query, tuple(update_values))
            connection.commit()

        return {"message": "Profil mis à jour avec succès"}
    
    finally:
        connection.close()
