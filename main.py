from datetime import datetime
from src.gmaps import Gmaps
from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# from amazon_paapi import AmazonApi
# from credentials import KEY, SECRET, TAG, COUNTRY, Airtable_api_token
# from pyairtable import Api
# amazon = AmazonApi(KEY, SECRET, TAG, COUNTRY)
import time
import requests


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ydcurl = 'http://164.52.208.218:8000'
second_endpoint = f"{ydcurl}/placesapi/store_places/"


class QueryModel(BaseModel):
    queries: List[str]


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.post("/MapsSearch")
async def search_places(query_model: QueryModel):
    result = Gmaps.places(query_model.queries)
    return result

############################################


async def places(query_list):
    result = Gmaps.places(query_list)
    return result


async def update_status(query_city_id, status):

    try:
        status_url = f"{ydcurl}/placesapi/update_query_id_status/{query_city_id}/{status}/"
        response = requests.get(status_url)

        if response.status_code == 200:
            return True
        else:
            return False

    except Exception as e:
        print(f"An unexpected error occurred while updating final status: {e}")
        return False


async def map_search():

    try:
        while True:
            get_Query_url = f"{ydcurl}/placesapi/get_query_city_by_status/Pending/"
            get_Query_response = requests.get(get_Query_url)
            get_Query_response.raise_for_status()

            if get_Query_response.status_code == 200:
                get_Query_response_data = get_Query_response.json()
                query = get_Query_response_data.get("query", "")
                query_city_id = get_Query_response_data.get(
                    "query_city_id", "")

                if query is None:
                    time.sleep(1200)
                else:
                    await update_status(query_city_id, "InProcess")
                    # update_status_url = f"{ydcurl}/placesapi/update_query_id_status/{query_city_id}/InProcess/"
                    # requests.get(update_status_url)

                    body = [query]

                    response_data = await places(body)

                    if len(response_data) < 1:
                        await update_status(query_city_id, "Cancelled")
                        # update_status_url = f"{ydcurl}/placesapi/update_query_id_status/{query_city_id}/Cancelled/"
                        # requests.get(update_status_url)
                        time.sleep(600)
                    else:
                        post_body = []
                        for place in response_data:
                            google_place_id = place.get("place_id", "")
                            name = place.get("name", "")
                            link = place.get("link", "")
                            phone_number = place.get("phone", "")
                            website = place.get("website", "")
                            detailed_address = place.get(
                                "detailed_address", {})
                            ward = detailed_address.get("ward", "")
                            state = detailed_address.get("state", "")
                            city = detailed_address.get("city", "")
                            postal_code = detailed_address.get(
                                "postal_code", "")
                            street = detailed_address.get("street", "")
                            status = 3

                            query_id = {"query_city_id": query_city_id}
                            competitors = [
                                {
                                    "competetor_place_id": None,
                                    "competetor_name": competitor.get("name", ""),
                                    "competetor_link": competitor.get("link", "")
                                }
                                for competitor in place.get("competitors", [])
                            ]

                            post_body.append({
                                "google_place_id": google_place_id,
                                "name": name,
                                "link": link,
                                "phone_number": phone_number,
                                "website": website,
                                "ward": ward,
                                "state": state,
                                "city": city,
                                "postal_code": postal_code,
                                "street": street,
                                "status": status,
                                "query_city_id": query_id,
                                "competitors": competitors
                            })

                        post_response = requests.post(
                            second_endpoint, json=post_body)
                        post_response.raise_for_status()

                        if post_response.status_code == 201:
                            await update_status(query_city_id, "Completed")
                            # final_status_url = f"{ydcurl}/placesapi/update_query_id_status/{query_city_id}/Completed/"
                            # requests.get(final_status_url)

    except requests.RequestException as req_error:
        print(f"Request error: {req_error}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


async def on_startup():
    # Call map_search at the start of the application
    await map_search()

# Register the on_startup event handler
app.add_event_handler("startup", on_startup)


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


###########################################################################################################################################
# @app.post('/asinData')
# async def asinData(asins: AsinModel):
#     asins = asins.asins
#     final_results = amazon.get_items(items=asins)
#     return final_results


# def getExamcart():
#     airtable = getExamcartAirtable()
#     records = airtable.all()
#     return records


# def getAirtable():
#     airtable = Api(api_key=Airtable_api_token)
#     return airtable


# def getExamcartAirtable():
#     airtable = getAirtable()
#     examcart = airtable.table('apph7VmzXLax4KGj1', 'Examcart 2023')
#     return examcart


# @app.post('/asin')
# async def asinData(asins: AsinModel):
#     asins = asins.asins
#     airtable_data = getExamcart()
#     items_table1 = []
#     items_table2 = []
#     items_table3 = []
#     asin_details = {}

#     try:
#         for entry in airtable_data:
#             asinId = entry["fields"].get("ASIN", None)
#             ecommerce_title = entry["fields"].get("E-commerce Title", None)
#             seller_sku = entry["fields"].get("Seller SKU", None)

#             if asinId in asins:
#                 asin_details[asinId] = {
#                     "title": ecommerce_title, "sku": seller_sku}

#         final_results = amazon.get_items(items=asins)

#         for item in final_results:

#             asin = item.asin
#             title = item._item_info._title._display_value
#             image_url = item._images._primary._medium._url
#             detail_page_url = item._detail_page_url
#             # airtable_title = airtable_data[asin]
#             publication_date = item._item_info._content_info._publication_date._display_value
#             parsed_date = datetime.strptime(
#                 publication_date, "%Y-%m-%dT%H:%M:%S.%f%z")

#             formatted_date = parsed_date.strftime("%Y-%m-%d")
#             details = asin_details[asin]
#             airtable_title = details.get("title", "Title not available")
#             airtable_sku = details.get("sku", "SKU not available")

#             items_table1.append({

#                 "ASIN": f'<a href="{detail_page_url}" target="_blank">{asin}</a>',
#                 "SKU": airtable_sku,
#                 "Title": title,
#                 "Image URL": f'<img src="{image_url}" alt="{title}" style="max-width:100px; max-height:100px;">',
#                 "Publication Date": formatted_date,
#                 "Airtable Title": airtable_title,
#                 "Title Maching": title == airtable_title
#             })
#             items_table2.append({

#                 "ASIN": f'<a href="{detail_page_url}" target="_blank">{asin}</a>',
#                 "SKU": airtable_sku,
#                 "Title": title,
#                 "Image URL": f'<img src="{image_url}" alt="{title}" style="max-width:100px; max-height:100px;">',
#                 "Publication Date": formatted_date,
#                 "Airtable Title": airtable_title,
#                 "Title Maching": title == airtable_title
#             })
#             items_table3.append({

#                 "ASIN": f'<a href="{detail_page_url}" target="_blank">{asin}</a>',
#                 "SKU": airtable_sku,
#                 "Title": title,
#                 "Image URL": f'<img src="{image_url}" alt="{title}" style="max-width:100px; max-height:100px;">',
#                 "Publication Date": formatted_date,
#                 "Airtable Title": airtable_title,
#                 "Title Maching": title == airtable_title
#             })

#         return {
#             "title": items_table1,
#             "category": items_table2,
#             "suppress": items_table3

#         }
#     except Exception as e:
#         print(f"Exception: {e}")


# def get_airtable_asin_title():
#     pass
