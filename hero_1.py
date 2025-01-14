from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Déclaration des modèles avec SQLModel
class HeroBase(SQLModel):
    # Modèle de base contenant les attributs communs
    name: str = Field(index=True)  # Nom du héros (indexé pour les recherches)
    secret_name: str  # Nom secret du héros
    age: int | None = Field(default=None, index=True)  # Âge du héros (optionnel et indexé)

class Hero(HeroBase, table=True):
    # Modèle de table qui inclut HeroBase et sera utilisé pour créer la table dans la base de données
    id: int | None = Field(default=None, primary_key=True)  # Clé primaire pour identifier les héros

class HeroCreate(HeroBase):
    # Modèle utilisé pour la création de nouveaux héros (hérite de HeroBase)
    pass

class HeroPublic(HeroBase):
    # Modèle utilisé pour la réponse publique (inclut l'ID)
    id: int

# Configuration de la base de données SQLite
sqlite_file_name = "database.db"  # Nom du fichier de la base de données
sqlite_url = f"sqlite:///{sqlite_file_name}"  # URL pour se connecter à la base SQLite

connect_args = {"check_same_thread": False}  # Nécessaire pour éviter les erreurs avec SQLite dans un environnement multi-thread
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)  # Crée le moteur pour la connexion à la base

def create_db_and_tables():
    # Fonction pour créer la base de données et les tables
    SQLModel.metadata.create_all(engine)  # Crée toutes les tables définies dans les modèles avec table=True

app = FastAPI()  # Initialise l'application FastAPI

@app.on_event("startup")
def on_startup():
    # Événement exécuté au démarrage de l'application
    create_db_and_tables()  # Appelle la fonction pour créer la base de données et les tables

@app.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate):
    # Endpoint pour créer un nouveau héros
    with Session(engine) as session:  # Ouvre une session avec la base de données
        db_hero = Hero.model_validate(hero)  # Valide les données du héros et les transforme en un objet Hero
        session.add(db_hero)  # Ajoute le nouveau héros à la session
        session.commit()  # Enregistre les changements dans la base de données
        session.refresh(db_hero)  # Rafraîchit l'objet pour récupérer l'ID généré
        return db_hero  # Retourne le héros créé sous forme publique (HeroPublic)

@app.get("/heroes/", response_model=list[HeroPublic])
def read_heroes():
    # Endpoint pour lire tous les héros
    with Session(engine) as session:  # Ouvre une session avec la base de données
        heroes = session.exec(select(Hero)).all()  # Exécute une requête pour sélectionner tous les héros
        return heroes  # Retourne la liste des héros

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int):
    # Endpoint pour lire un héros spécifique par son ID
    with Session(engine) as session:  # Ouvre une session avec la base de données
        hero = session.get(Hero, hero_id)  # Recherche le héros par ID
        if not hero:  # Si le héros n'est pas trouvé
            raise HTTPException(status_code=404, detail="Hero not found")  # Retourne une erreur 404
        return hero  # Retourne le héros trouvé
