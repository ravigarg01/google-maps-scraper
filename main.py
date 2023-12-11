from src.gmaps import Gmaps
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class QueryModel(BaseModel):
    queries: List[str]

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
