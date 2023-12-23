from datetime import datetime
from src.gmaps import Gmaps
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from amazon_paapi import AmazonApi
from credentials import KEY, SECRET, TAG, COUNTRY, Airtable_api_token
from pyairtable import Api



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

# @app.post('/asinData')
# async def asinData(asins: AsinModel):
#     asins = asins.asins
#     results = []

#     tasks = [amazon.get_items(asin) for asin in asins]
#     results = await asyncio.gather(*tasks)

#     return results


@app.post('/asinData')
async def asinData(asins: AsinModel):
    asins = asins.asins
    final_results = amazon.get_items(items = asins)
    return final_results
    

@app.get('/getExamcart')
async def getExamcart():
    airtable = getExamcartAirtable()
    records = airtable.all()
    return records

def getAirtable():
    airtable = Api(api_key=Airtable_api_token)
    return airtable

def getExamcartAirtable():
    airtable = getAirtable()
    examcart = airtable.table('apph7VmzXLax4KGj1', 'Examcart 2023')
    return examcart
