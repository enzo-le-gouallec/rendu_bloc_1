from fastapi import APIRouter, HTTPException, Depends, Query
from database import get_connection
from auth import verify_jwt

router = APIRouter()

@router.get("/company_planity/", summary="Liste des entreprises à démarcher")
def get_companies(
    city_name: str = None, 
    user_id: int = Depends(verify_jwt)  # 👈 Vérifie que l'utilisateur est authentifié
):
    """
    **Récupérer toutes les salon de coiffure disponible sur l'application planity**  

    - **Besoin d'un Token JWT** (`Authorization: Bearer <TOKEN>`)
    - **Paramètres** :
        - `city_name` (str, optionnel) : Nom de la ville pour filtrer les entreprises (ex: `Bordeaux`).
    - **Retourne** : Une liste des entreprises stockées dans la base de données MySQL.
    - **Status codes** :
        - `200` : Succès, retourne les entreprises
        - `401` : Token manquant, invalide ou expiré
        - `404` : Aucune entreprise trouvée pour cette ville ou route non trouvée
        - `500` : Erreur interne du serveur

    **Exemples de réponse JSON :**
    
    - **Sans filtre** (toutes les entreprises) :
    ```json
    {
        "companies": [
            {
                "id": 1,
                "name": "COIFF ME",
                "institution_address": "3 RUE HAIRSTYLE 33000 BORDEAUX",
                "city_name": "BORDEAUX",
                "postal_code": "33000"
            },
            {
                "id": 2,
                "name": "HAIR STYLE PRO",
                "institution_address": "25 RUE DES COIFFEURS 75000 PARIS",
                "city_name": "PARIS",
                "postal_code": "75000"
            }
        ]
    }
    ```
    
    - **Avec `?city_name=Bordeaux`** (filtré par ville) :
    ```json
    {
        "companies": [
            {
                "id": 1,
                "name": "COIFF ME",
                "institution_address": "3 RUE HAIRSTYLE 33000 BORDEAUX",
                "head_address": "1 RUE HAIRSTYLE 33000 BORDEAUX",
                "city_name": "BORDEAUX",
                "postal_code": "33000"
            }
        ]
    }
    ```
    """  
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Erreur de connexion à la base de données")

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    company_planity.id, 
                    company_planity.name, 
                    company_planity.institution_address, 
                    city.name AS city_name, 
                    city.code AS postal_code
                FROM company_planity 
                LEFT JOIN city ON company_planity.city_ID = city.id
            """
            
            if city_name:
                sql += " WHERE city.name = %s"
                cursor.execute(sql, (city_name,))
            else:
                cursor.execute(sql)
            
            companies = cursor.fetchall()
        
        return {"companies": companies}  
    
    finally:
        connection.close()
