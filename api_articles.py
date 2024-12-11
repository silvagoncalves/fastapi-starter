from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

articles = {
    1: {"name": "Unité centrale", "price": 750},
    2: {"name": "Ecran", "price": 350},
}

class Article(BaseModel):
    name: str
    price: int
    
@app.get("/articles/{article_id}", response_model=Article)
async def get_articles(article_id: int):
    if article_id in articles:
        return articles[article_id]
    raise HTTPException(status_code=404, detail="Article not found")

@app.post("/articles/", response_model=Article)
async def create_article(article: Article):
    new_id = max(articles.keys()) + 1
    articles[new_id] = article.model_dump()
    return article

@app.post("/info/")
async def info(article: Article):
    return {
        "version": "0.1"
    }

