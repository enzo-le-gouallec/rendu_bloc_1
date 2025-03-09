import requests
import pandas as pd
import pandas as pd
from datetime import datetime
from pathlib import Path


# Création d'un DataFrame vide avec les colonnes attendues
d = {'name': ["ok"], 'institution_adress': ["ok"],   'postal_code': ["ok"], 'city': ["ok"], 'longitude' : ["ok"], 'latitude' : ["ok"], 'head_adress': ["ok"]}
df_gouv = pd.DataFrame(d)

# Requête HTTP GET pour récupérer les données
r = requests.get('https://recherche-entreprises.api.gouv.fr/near_point?lat=44.841613983266726&long=-0.5810928534306644&activite_principale=96.02A&radius=10&page=1&per_page=25', auth=('user', 'pass'))
r.status_code
r_result = r.json()

 # boucle pour récupérer tout salons de coiffure sur bordeaux
for index_page in range(1, r_result["total_pages"] + 1):
    r = requests.get(f'https://recherche-entreprises.api.gouv.fr/near_point?lat=44.841613983266726&long=-0.5810928534306644&activite_principale=96.02A&radius=10&page={index_page}&per_page=25', auth=('user', 'pass'))
    r_result = r.json()
    print(index_page)
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




#nettoyage du dataframe
df_gouv = df_gouv.drop([0])
df_gouv.reset_index(drop=True, inplace=True)

df_gouv_bordeaux = df_gouv[df_gouv["city"] == "BORDEAUX"]
df_gouv_bordeaux
df_gouv_bordeaux["name"] = df_gouv_bordeaux["name"].apply(lambda x: x[0] if isinstance(x, list) else x)

df_gouv_bordeaux = df_gouv_bordeaux[df_gouv_bordeaux['name'].notna()]
df_gouv_bordeaux.drop_duplicates(subset=['name', 'institution_adress'], inplace=True)
df_gouv_bordeaux.reset_index(drop=True, inplace= True)
df_gouv_bordeaux["longitude"] = df_gouv_bordeaux["longitude"].astype(float)
df_gouv_bordeaux["latitude"] = df_gouv_bordeaux["latitude"].astype(float)






def save_dataframe_with_date_and_time(df, output_directory=Path.cwd()):
    """
    Sauvegarde un DataFrame en CSV en ajoutant la date et l'heure actuelles dans le nom du fichier,
    tout en conservant exactement les noms de colonnes du DataFrame.
    
    Args:
        df (pd.DataFrame): Le DataFrame à sauvegarder.
        output_directory (Path, optional): Le répertoire de sauvegarde. Par défaut, le répertoire courant.

    Returns:
        Path: Le chemin complet du fichier CSV sauvegardé.
    """
    # Récupération de la date et de l'heure actuelles au format YYYYMMDD_HHMMSS
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"df_gouv_bordeaux_{current_datetime}.csv"
    file_path = output_directory / file_name

    # Sauvegarde du DataFrame en CSV
    df.to_csv(file_path, index=False, header=True)
    print(f"DataFrame sauvegardé dans : {file_path}")


if __name__ == "__main__":
    output_directory = Path("/mnt/c/Users/Utilisateur/Desktop/ia_development/bloc_1")
    save_dataframe_with_date_and_time(df_gouv_bordeaux, output_directory=output_directory)
