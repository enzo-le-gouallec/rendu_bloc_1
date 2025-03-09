import pymysql
import config

def get_connection():
    try:
        connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor  # Retourne les résultats sous forme de dictionnaire
        )
        return connection
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None
    
    
