import re, os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

def clean_filename(filename):
    filename = re.sub(r'[\\/*?:"<>~]', "_", filename) # remove special characters
    return filename

def build_payload(query, api_key, search_engine_id, start=1, num=10, **params):
    payload = {
        "key": api_key,
        "q": query,
        "cx": search_engine_id,
        "start": start,
        "num": num
    }

    payload.update(params)
    return payload

def search_images(payload):
    response = requests.get("https://www.googleapis.com/customsearch/v1", params=payload)
    if response.status_code != 200:
        print(f"Failed to fetch images: {response.json()}")
        return None
    else:
        return response.json()

def main(query, api_key, search_engine_id, result_total=10):
    items = []
    reminder = result_total % 10

    if reminder > 0:
        pages = (result_total // 10) + 1
    else:
        pages = result_total // 10

    for i in range(pages):
        if pages == i + 1 and reminder > 0:
            payload = build_payload(query, api_key, search_engine_id, start=(i + 1)*10, num=reminder)
        else:
            payload = build_payload(query, api_key, search_engine_id, start=(i + 1)*10)
        response = search_images(payload)
        items.extend(response["items"])

    query_string_clean = clean_filename(query)
    df = pd.json_normalize(items)
    df.to_csv(f"{query_string_clean}.csv", index=False)


if __name__ == "__main__":
    API_KEY = os.environ.get("API_KEY")
    SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
    search_query = "ryan gosling"
    total_results = 35
    main(search_query, API_KEY, SEARCH_ENGINE_ID, total_results)