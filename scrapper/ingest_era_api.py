import sys
import json
import asyncio
import yaml
import requests
from utils import class_scrapper
from utils import class_db

try:
    with open("scrapper/utils/config_era.yaml", "r") as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("Config file not found")
    sys.exit()


async def fetch_data(scrapper, location_id):
    try:

        payload = [{"Id": location_id, "IsDevelopment": False}]
        payload_json = json.dumps(payload)

        response = scrapper.post_requests(url=config["card_url"], data=payload_json)

        adds = [
            (
                scrapper.feed,
                scrapper.scrape_date,
                scrapper.execution_id,
                scrapper.locator,
                i["Photo"]["Url"],
                i["Photo"]["Description"],
                i["DetailUrl"],
                i["BusinessType"][0]["Name"],
                i["Elevator"],
                i["Floor"],
                i["Id"],
                i["LandArea"],
                i["Lat"],
                i["Lng"],
                i["Localization"],
                i["NetArea"],
                i["Owner"],
                i["Parking"],
                i["PropertyType"],
                i["Rooms"],
                (i["SellPrice"] or i["RentPrice"])["Name"],
                (i["SellPrice"] or i["RentPrice"])["Value"],
                (i["SellPrice"] or i["RentPrice"])["PreviousValue"],
                (i["SellPrice"] or i["RentPrice"])["Variation"],
                i["Title"],
                i["Wcs"],
                i["FractionNumb"],
                i["FloorNumb"],
                i["HousingArea"],
                i["ListingBuildingArea"],
                i["ImplantationArea"],
                i["ConstructionFeasibility"],
                i["Walled"],
                i["PriceNetArea"],
                i["PriceListingArea"],
                i["PriceLandArea"],
                i["RentPriceNetArea"],
                i["RentPriceListingArea"],
                i["RentPriceLandArea"],
                i["SubLeasePriceNetArea"],
                i["SubLeasePriceListingArea"],
                i["SubLeasePriceLandArea"],
            )
            for i in response
        ]

        db_instace = class_db.DbMethods()

        db_instace.create_cursor(
            db_name=config["db_name"],
            user=config["user"],
            password=config["password"],
            port=config["port"],
        )

        for add in adds:
            db_instace.execute_query(config["insert_raw_api"], add, True)

        db_instace.close()

    except TypeError:
        print(f"{location_id} not done")


async def main(id_list, scrapper):

    tasks = []
    async with asyncio.TaskGroup() as tg:
        for id in id_list:
            task = tg.create_task(fetch_data(scrapper, id))
            tasks.append(task)

    results = [task.result() for task in tasks]

    return results


if __name__ == "__main__":
    try:
        scrapper = class_scrapper.Scrapper()
        scrapper.feed = config["feed"]
        scrapper.locator = config["locator"]
        scrapper.configure_retry(5)

        cookies_token, token_html = scrapper.get_request(config["base_url"])
        verification_token = scrapper.fetch_token(token_html)
        scrapper.session.headers.update(
            {
                "cookie": f"__RequestVerificationToken={cookies_token};",
                "requestverificationtoken": verification_token,
                "Content-Type": "application/json",
            }
        )

        body_search = config["body_search"]

        body_search_json = json.dumps(body_search)
        response_search = scrapper.post_requests(
            config["search_url"], data=body_search_json
        )

        all_ids = [i["Id"] for i in response_search["Properties"]]

        full_data = asyncio.run(main(all_ids, scrapper))

    except AttributeError:
        print("It was not possible to generate token!")
    except requests.RequestException as e:
        print("A network or HTTP error occurred:", e)
    except ValueError:
        print("Response was not valid JSON.")
    except Exception as e:
        print(f"Please check {e}")
