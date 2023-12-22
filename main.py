from src.gmaps import Gmaps
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from amazon_paapi import AmazonApi
from credentials import KEY, SECRET, TAG, COUNTRY

class QueryModel(BaseModel):
    queries: List[str]
    
class AsinModel(BaseModel):
    asins: List[str]
    
amazon = AmazonApi(KEY, SECRET, TAG, COUNTRY)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.post("/MapsSearch")
async def search_places(query_model: QueryModel):
    result = Gmaps.places(query_model.queries)
    return result

@app.get('/test')
async def test():
    return {'message': 'hello world'}

@app.post('/asinData')
async def asinData(asins: AsinModel):
    asins = asins.asins
    results = []
    for asin in asins:
        result = amazon.get_items(asin)
        results.append(result)
    return results