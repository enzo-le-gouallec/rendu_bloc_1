from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from auth import verify_jwt  # Vérifie le JWT
from dotenv import load_dotenv
import config
import os

load_dotenv()
router = APIRouter()


mongo_client = MongoClient(config.MONGO_URI)
db = mongo_client[config.MONGO_DB_NAME]
collection = db[config.MONGO_COLLECTION]

@router.get("/companies_to_target/", summary="Liste des entreprises à démarcher")
def get_companies_to_target(user_id: int = Depends(verify_jwt)):
    """
    **Récupérer les entreprises à Démrcher**

    - **Besoin d'un Token JWT** (`Authorization: Bearer <TOKEN>`)
    - **Retourne** : une liste des entreprises stockées dans MongoDB
    - **Status codes** :
        - `200` : Succès, retourne les entreprises
        - `401` : Token manqunt, invalide ou expiré
        - `404` : Aucune entreprise trouvée pour cette ville ou route non trouvée
        - `500` : Erreur interne du serveur
    
    **Exemple de réponse JSON :**
    ```json
        {
        "companies_to_target": [
            {
                "name": COIFF ME",
                "institution_address": "3 RUE HAIRSTYLE 33000 BORDEAUX",
                "head_address": "1 RUE HAIRSTYLE 33000 BORDEAUX",
                "longitude": -0.57918,
                "latitude": 44.8376,
                "city_name": "BORDEAUX",
                "postal_code": "33000"
            },
            {
                "name": COIFF ME",
                "institution_address": "3 RUE HAIRSTYLE 33000 BORDEAUX",
                "head_address": "1 RUE HAIRSTYLE 33000 BORDEAUX",
                "longitude": -0.57918,
                "latitude": 44.8376,
                "city_name": "BORDEAUX",
                "postal_code": "33000"
            }
        ]
    }

    ```
    """
    try:
       
        companies = list(collection.find({}, {"_id": 0}))  # Exclut `_id` de la réponse JSON
        
        if not companies:
            raise HTTPException(status_code=404, detail="Aucune entreprise trouvée")

        return {"companies_to_target": companies}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
