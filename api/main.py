from fastapi import FastAPI
from routes import users, company_planity, company_gouv, companies_to_target

app = FastAPI()

# Enregistrement des routes
app.include_router(users.router)
app.include_router(company_planity.router)
app.include_router(company_gouv.router)
app.include_router(companies_to_target.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de gestion des démarchages de salons de coiffure"}

