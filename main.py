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
#     final_results = amazon.get_items(items=asins)
#     return final_results


def getExamcart():
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


@app.post('/asin')
async def asinData(asins: AsinModel):
    asins = asins.asins
    airtable_data = getExamcart()
    items_table1 = []
    items_table2 = []
    items_table3 = []
    asin_details = {}

    try:
        for entry in airtable_data:
            asinId = entry["fields"].get("ASIN", None)
            ecommerce_title = entry["fields"].get("E-commerce Title", None)
            seller_sku = entry["fields"].get("Seller SKU", None)

            if asinId in asins:
                asin_details[asinId] = {
                    "title": ecommerce_title, "sku": seller_sku}

        final_results = amazon.get_items(items=asins)

        for item in final_results:

            asin = item.asin
            title = item._item_info._title._display_value
            image_url = item._images._primary._medium._url
            detail_page_url = item._detail_page_url
            # airtable_title = airtable_data[asin]
            publication_date = item._item_info._content_info._publication_date._display_value
            parsed_date = datetime.strptime(
                publication_date, "%Y-%m-%dT%H:%M:%S.%f%z")

            formatted_date = parsed_date.strftime("%Y-%m-%d")
            details = asin_details[asin]
            airtable_title = details.get("title", "Title not available")
            airtable_sku = details.get("sku", "SKU not available")

            items_table1.append({

                "ASIN": f'<a href="{detail_page_url}" target="_blank">{asin}</a>',
                "SKU": airtable_sku,
                "Title": title,
                "Image URL": f'<img src="{image_url}" alt="{title}" style="max-width:100px; max-height:100px;">',
                "Publication Date": formatted_date,
                "Airtable Title": airtable_title,
                "Title Maching": title == airtable_title
            })
            items_table2.append({

                "ASIN": f'<a href="{detail_page_url}" target="_blank">{asin}</a>',
                "SKU": airtable_sku,
                "Title": title,
                "Image URL": f'<img src="{image_url}" alt="{title}" style="max-width:100px; max-height:100px;">',
                "Publication Date": formatted_date,
                "Airtable Title": airtable_title,
                "Title Maching": title == airtable_title
            })
            items_table3.append({

                "ASIN": f'<a href="{detail_page_url}" target="_blank">{asin}</a>',
                "SKU": airtable_sku,
                "Title": title,
                "Image URL": f'<img src="{image_url}" alt="{title}" style="max-width:100px; max-height:100px;">',
                "Publication Date": formatted_date,
                "Airtable Title": airtable_title,
                "Title Maching": title == airtable_title
            })

        return {
            "title": items_table1,
            "category": items_table2,
            "suppress": items_table3

        }
    except Exception as e:
        print(f"Exception: {e}")


def get_airtable_asin_title():
    pass
