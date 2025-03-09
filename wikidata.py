from SPARQLWrapper import SPARQLWrapper, JSON

# Endpoint SPARQL de Wikidata
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# Requête SPARQL pour récupérer la population de Bordeaux
query = """
SELECT ?population WHERE {
  ?city rdfs:label "Bordeaux"@fr ;
        wdt:P1082 ?population .
}
LIMIT 1
"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print("Population de Bordeaux :", result["population"]["value"])