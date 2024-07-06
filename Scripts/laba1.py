from fastapi import FastAPI

import wikipedia

from pydantic import BaseModel



app = FastAPI()



class Article(BaseModel):

    сonclusion: str



class ArticleInput(BaseModel):

    article: str



@app.get("/{request}", response_model=Article)

def get_article_by_article(article: str):

    """Получаем необходимую статью из поиска по запросу"""

    return Article(сonclusion=f"{wikipedia.search(article)[0]} - самая релевантная статья по запросу {article}")



@app.get("/multi/{request}", response_model=Article)

def get_articles_by_article(article: str, article_count: int):

    """Получаем необходимые статьи из поиска по запросу"""

    return Article(сonclusion=f"{', '.join(wikipedia.search(article)[:article_count])} - нужное количество самых релевантных статей по запросу {article}")



@app.post("/", response_model=Article)

def get_article_by_request_2(req: ArticleInput):

    """Поиск необходиме статьи по запросу с передачей параметра в теле"""



    return Article(article=req.article,

                        сonclusion=f"{wikipedia.search(req.article)[0]} - самая релевантная статья по запросу {req.article}")