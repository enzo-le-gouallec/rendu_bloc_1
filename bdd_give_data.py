from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import pandas as pd
from dotenv import load_dotenv
import os
import pymysql
import pymongo
from pymongo import MongoClient


#--------------------------------------------------------Scrapping--------------------------------------------------------#

# Configuration du navigateur pour le scrapping avec Selenium
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  
chrome_options.add_argument("--window-size=1920x1080")  


driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.delete_all_cookies()

# Charge la page web
url = 'https://www.planity.com/'
driver.get(url)

try:
    # navigation sur le site web
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="didomi-notice-agree-button"]')))
    cookie_button = driver.find_element(By.XPATH, '//*[@id="didomi-notice-agree-button"]')
    cookie_button.click()

    

   
    input_institut_type = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder*="salon"]')))
    input_institut_type.send_keys("Coiffeurs")
    input_institut_type.send_keys(Keys.ARROW_DOWN)
    input_institut_type.send_keys(Keys.ENTER)

    
   
    input_city = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder*="Adresse"]')))
    input_city.send_keys("Bordeaux")
    time.sleep(2)
    input_city.send_keys(Keys.ARROW_DOWN)
    input_city.send_keys(Keys.ENTER)

    

    
    
    
 

    time.sleep(5)

   # Récupération des données sur la première page et ittération sur les pages suivantes avec des temps d'attente
   #  pour ne pas surcharger le serveur
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    current_url = driver.current_url
    print(f"URL actuelle : {current_url}")

    
   

    d = {'name': [], 'institution_adress': [], 'postal_code': [], 'city': []}
    df_planity = pd.DataFrame(d)

    divs = soup.find_all('div', class_=re.compile(r'business_item'))
    for div in divs:
        links = div.find_all('a')
        if links[0].text != '':
            name = links[0].text
        span = div.find_all('span')
    
        span = span[2].find_all('span')
        
        if span[2].text[-2:-1] != ")":
            adress = span[2].text
            postal_code = span[4].text
            city = span[5].text
            df_planity.loc[len(df_planity)] = [name, f"{adress} {postal_code} {city}", postal_code, city]

    
    links = soup.find_all('ol', class_=re.compile(r'pagination'))
    
    for page in links:
        for link in page.find_all('a'):
            
            nb_pages = int(link.text)

    print(nb_pages)

    for pages in range(2, nb_pages + 1):
        print(pages)
        url = f'{current_url}/page-{pages}'
        time.sleep(3)
        driver.get(url)
        time.sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        print(url)
        divs = soup.find_all('div', class_=re.compile(r'business_item'))
        for div in divs:
            links = div.find_all('a')
            if links[0].text != '':
                name = links[0].text
            span = div.find_all('span')
        
            span = span[2].find_all('span')
            
            if span[2].text[-2:-1] != ")":
                adress = span[2].text
                postal_code = span[4].text
                city = span[5].text
                df_planity.loc[len(df_planity)] = [name, f"{adress} {postal_code} {city}", postal_code, city]


except Exception as e:
    print(f"Une erreur est survenue : {e}")


driver.quit()

df_planity.drop_duplicates(subset=['name', 'institution_adress'], inplace=True)
df_planity = df_planity.apply(lambda x: x.str.upper())
df_planity_bordeaux = df_planity[df_planity["city"] == "BORDEAUX"]
df_planity_bordeaux.reset_index(drop=True, inplace= True)



#--------------------------------------------------------request api--------------------------------------------------------#



# Création d'un DataFrame pour stocker les données récupérées
d = {'name': ["ok"], 'institution_adress': ["ok"],   'postal_code': ["ok"], 'city': ["ok"], 'longitude' : ["ok"], 'latitude' : ["ok"], 'head_adress': ["ok"]}
df_gouv = pd.DataFrame(d)
df_gouv

# Requête HTTP GET pour récupérer les données sur les salons de coiffure à Bordeaux
r = requests.get('https://recherche-entreprises.api.gouv.fr/near_point?lat=44.841613983266726&long=-0.5810928534306644&activite_principale=96.02A&radius=10&page=1&per_page=25', auth=('user', 'pass'))
r.status_code
r_result = r.json()
for index_page in range(1, r_result["total_pages"] + 1):
    r = requests.get(f'https://recherche-entreprises.api.gouv.fr/near_point?lat=44.841613983266726&long=-0.5810928534306644&activite_principale=96.02A&radius=10&page={index_page}&per_page=25', auth=('user', 'pass'))
    r_result = r.json()
    print(index_page)

    # Boucle pour récupérer tout salons de coiffure sur bordeaux en itérant sur les pages et
    # en prenant en compte les différents cas de figure pour les données manquantes 
    # dans l'API suivant la position des informations dans le JSON
    for i in range(len(r_result["results"])):
        print(" ")
        for index_etablissement in range(len(r_result["results"][i]["matching_etablissements"])):
            if r_result["results"][i]["matching_etablissements"][index_etablissement]["liste_enseignes"] != None :
                if r_result["results"][i]["matching_etablissements"][index_etablissement]["activite_principale"] == "96.02A":
                    print(r_result["results"][i]["matching_etablissements"][index_etablissement]["liste_enseignes"])
                    name = r_result["results"][i]["matching_etablissements"][index_etablissement]["liste_enseignes"]
                    print("adresse enseigne :", r_result["results"][i]["matching_etablissements"][index_etablissement]["adresse"])
                    institution_adress = r_result["results"][i]["matching_etablissements"][index_etablissement]["adresse"]
                    print("adresse siège : ",  r_result["results"][i]["siege"]["adresse"])
                    head_adress = r_result["results"][i]["siege"]["adresse"]

                    print("code postal :", r_result["results"][i]["matching_etablissements"][index_etablissement]["code_postal"])
                    postal_code = r_result["results"][i]["matching_etablissements"][index_etablissement]["code_postal"]

                    print("ville :", r_result["results"][i]["matching_etablissements"][index_etablissement]["libelle_commune"])
                    city = r_result["results"][i]["matching_etablissements"][index_etablissement]["libelle_commune"]

                    print("longitude :", r_result["results"][i]["matching_etablissements"][index_etablissement]["longitude"])
                    longitude = r_result["results"][i]["matching_etablissements"][index_etablissement]["longitude"]

                    print("latitude :", r_result["results"][i]["matching_etablissements"][index_etablissement]["latitude"])
                    latitude = r_result["results"][i]["matching_etablissements"][index_etablissement]["latitude"]

                    df_gouv.loc[len(df_gouv)] = [name, institution_adress, postal_code, city, longitude, latitude, head_adress]
            
            
            else:
                if  r_result["results"][i]["activite_principale"] == "96.02A" and r_result["results"][i]["siege"]["code_postal"] == "33000" :
                    print(r_result["results"][i]["nom_raison_sociale"])
                    name = r_result["results"][i]["nom_raison_sociale"]

                    print("adresse enseigne :", r_result["results"][i]["matching_etablissements"][0]["adresse"])
                    institution_adress = r_result["results"][i]["siege"]["adresse"]

                    print("adresse siège : ",  r_result["results"][i]["siege"]["adresse"])
                    head_adress = r_result["results"][i]["matching_etablissements"][0]["adresse"]

                    print("code postal :", r_result["results"][i]["matching_etablissements"][0]["code_postal"])
                    postal_code = r_result["results"][i]["matching_etablissements"][0]["code_postal"]

                    print("ville :", r_result["results"][i]["matching_etablissements"][0]["libelle_commune"])
                    city = r_result["results"][i]["matching_etablissements"][0]["libelle_commune"]

                    print("longitude :", r_result["results"][i]["matching_etablissements"][0]["longitude"])
                    longitude = r_result["results"][i]["matching_etablissements"][0]["longitude"]

                    print("latitude :", r_result["results"][i]["matching_etablissements"][0]["latitude"])
                    latitude = r_result["results"][i]["matching_etablissements"][0]["latitude"]

                    df_gouv.loc[len(df_gouv)] = [[name], institution_adress, postal_code, city, longitude, latitude, head_adress]
                elif  r_result["results"][i]["activite_principale"] == "96.02A" and r_result["results"][i]["matching_etablissements"][0]["activite_principale"] == "96.02A" :
                    print(r_result["results"][i]["nom_raison_sociale"])
                    name = r_result["results"][i]["nom_raison_sociale"]

                    print("adresse enseigne :", r_result["results"][i]["matching_etablissements"][0]["adresse"])
                    institution_adress = r_result["results"][i]["siege"]["adresse"]

                    print("adresse siège : ",  r_result["results"][i]["siege"]["adresse"])
                    head_adress = r_result["results"][i]["matching_etablissements"][0]["adresse"]

                    print("code postal :", r_result["results"][i]["matching_etablissements"][0]["code_postal"])
                    postal_code = r_result["results"][i]["matching_etablissements"][0]["code_postal"]

                    print("ville :", r_result["results"][i]["matching_etablissements"][0]["libelle_commune"])
                    city = r_result["results"][i]["matching_etablissements"][0]["libelle_commune"]

                    print("longitude :", r_result["results"][i]["matching_etablissements"][0]["longitude"])
                    longitude = r_result["results"][i]["matching_etablissements"][0]["longitude"]

                    print("latitude :", r_result["results"][i]["matching_etablissements"][0]["latitude"])
                    latitude = r_result["results"][i]["matching_etablissements"][0]["latitude"]

                    df_gouv.loc[len(df_gouv)] = [[name], institution_adress, postal_code, city, longitude, latitude, head_adress]



#-------------------------------------Nettoyage des données et comparaison des deux dataframes--------------------------------------------#


df_gouv = df_gouv.drop([0])
df_gouv.reset_index(drop=True, inplace=True)

df_gouv_bordeaux = df_gouv[df_gouv["city"] == "BORDEAUX"]
df_gouv_bordeaux

# transformation des array en string, Suppression des doublons, des valeurs nulles, des valeurs vides et formatage des données
df_gouv_bordeaux["name"] = df_gouv_bordeaux["name"].apply(lambda x: x[0] if isinstance(x, list) else x)


df_gouv_bordeaux = df_gouv_bordeaux[df_gouv_bordeaux['name'].notna()]
df_gouv_bordeaux.drop_duplicates(subset=['name', 'institution_adress'], inplace=True)
df_gouv_bordeaux.reset_index(drop=True, inplace= True)
df_gouv_bordeaux["longitude"] = df_gouv_bordeaux["longitude"].astype(float)
df_gouv_bordeaux["latitude"] = df_gouv_bordeaux["latitude"].astype(float)

df_planity_bordeaux = df_planity_bordeaux.applymap(lambda x: str(x).replace("\xa0", "").strip())
df_planity_bordeaux = df_planity_bordeaux[df_planity_bordeaux["postal_code"].astype(str).str.strip() != ""]


df_postal_code_planity = df_planity_bordeaux[["postal_code", "city"]].drop_duplicates()
df_postal_code_planity.reset_index(drop=True, inplace= True)

df_postal_code_gouv = df_gouv_bordeaux[["postal_code", "city"]].drop_duplicates()

df_postal_code = pd.concat([df_postal_code_gouv, df_postal_code_planity], ignore_index=True).drop_duplicates()
df_postal_code.reset_index(drop=True, inplace= True)




#Comparaison des entreprises présentes dans les deux DataFrames
df_common = df_gouv_bordeaux.merge(
    df_planity_bordeaux,
    on=["name"], 
    how="inner",
    suffixes=("_gouv", "_planity")  
)

# Suppression lds colonnes de `planity` pour garder uniquement celles de `gouv`
df_common = df_common[[col for col in df_common.columns if not col.endswith("_planity")]]

# Trouver les entreprises qui sont dans `company_gouv` mais pas dans `company_planity`
df_to_target = df_gouv_bordeaux.merge(
    df_planity_bordeaux,
    on=["name"],
    how="left", 
    indicator=True  
).query('_merge == "left_only"').drop(columns=["_merge"])


print("Entreprises présentes dans les deux bases (colonnes Gouv uniquement) :")
print(df_common.head())  

print("\n Entreprises à démarcher (uniques à company_gouv) :")
print(df_to_target.head())  



#--------------------------------------------------------MYSQL--------------------------------------------------------#


# Chargement des variables d'environnement depuis le fichier .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,   
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        
       

        
        sql = """
        INSERT INTO CITY (code, name) VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name);
        """

        # Exécuter les insertions
        for _, row in df_postal_code.iterrows():
            cursor.execute(sql, (row["postal_code"], row["city"]))

        # Validation de  la transaction
        conn.commit()

        print("✅ Insertion city terminée avec succès !")

        sql_get_city_id = "SELECT id FROM CITY WHERE code = %s"
        
        city_id_map = {}
        cursor.execute("SELECT id, code FROM CITY")
        for row in cursor.fetchall():
            city_id_map[row["code"]] = row["id"]

        # Insertion les entreprises dans `COMPANY_GOUV`
        sql_insert_gouv = """
        INSERT INTO COMPANY_GOUV (name, institution_address, head_address, longitude, latitude, city_ID)
        VALUES (%s, %s, %s, %s, %s, %s);
        """

        for _, row in df_gouv_bordeaux.iterrows():
            city_id = city_id_map.get(row["postal_code"])
            if city_id:
                cursor.execute(sql_insert_gouv, (
                    row["name"], row["institution_adress"], row["head_adress"], 
                    row["longitude"], row["latitude"], city_id
                ))

        # Insertion des entreprises dans `COMPANY_PLANITY`
        sql_insert_planity = """
        INSERT INTO COMPANY_PLANITY (name, institution_address, city_ID)
        VALUES (%s, %s, %s);
        """

        for _, row in df_planity_bordeaux.iterrows():
            city_id = city_id_map.get(row["postal_code"])
            if city_id:
                cursor.execute(sql_insert_planity, (
                    row["name"], row["institution_adress"], city_id
                ))

        # Validation des insertions
        conn.commit()

        print("✅ Données insérées avec succès dans COMPANY_GOUV et COMPANY_PLANITY.")

except Exception as e:
    print(f"❌ Erreur : {e}")
    conn.rollback()

finally:
    conn.close()



#--------------------------------------------------------MONGO DB--------------------------------------------------------#



mongo_uri = os.environ.get("MONGO_URI")
mongo_db_name = os.environ.get("MONGO_DB_NAME")
mongo_collection = os.environ.get("MONGO_COLLECTION")


client = MongoClient(mongo_uri)
db = client[mongo_db_name]
posts = db[mongo_collection]

posts = db.companies_to_target

# Insértion des entreprises à démarcher dans la collection `companies_to_target`
for i in range(0, len(df_to_target)):

    companies_to_target = {
    "name" : df_to_target["name"][i],
    "institution_address" : df_to_target["institution_address_x"][i],
    "head_address" : df_to_target["head_address"][i],
    "longitude" : df_to_target["longitude"][i],
    "latitude" : df_to_target["latitude"][i],
    "city_name" : df_to_target["city_name_x"][i],
    "postal_code" : df_to_target["postal_code_x"][i]
    }
    companies_to_target_id = posts.insert_one(companies_to_target).inserted_id

