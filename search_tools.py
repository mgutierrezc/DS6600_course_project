import re, os
import requests, logging, urllib.request
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

## set up logging
logging.basicConfig(filename="image_search.log", 
                    filemode="w", # change to "a" in production
                    format="%(asctime)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S", 
                    level=logging.INFO)


## set up functions

def clean_filename(filename: str) -> str:
    """
    Removes special characters from a string to 
    make it suitable for a filename.
    """
    filename = re.sub(r'[\\/*?:"<>~ ]', "_", filename) # remove special characters and replace spaces
    return filename

def build_payload(query: str, api_key: str, 
                  search_engine_id: str, start=1, 
                  num=10, **params) -> dict:
    """
    Creates a dictionary with the parameters for the
    Google Custom Search API.
    """
    
    logging.info(f"build_payload: building for query: {query}")
    payload = {
        "key": api_key,
        "q": query,
        "cx": search_engine_id,
        "start": start,
        "num": num
    }

    payload.update(params)
    logging.info("build_payload: success")
    return payload

def search_images(payload):
    """
    Fetches images from the Google Custom Search API
    based on the payload provided.
    """

    logging.info("search_images: fetching images for current payload")
    response = requests.get("https://www.googleapis.com/customsearch/v1",
                            params=payload)
    
    if response.status_code != 200:
        logging.info(f"failed to fetch images: {response.json()}")
        return None
    else:
        logging.info("search_images: images fetched successfully")
        return response.json()

def main(query: str, api_key: str, search_engine_id: str,
         start_page_index: int, outpath: str, result_total=10) -> None:
    """
    Fetches images from the Google Custom Search API 
    and saves them to a CSV file.
    """

    logging.info(f"main: starting search for query: {query}")

    items = [] # placeholder for image data
    reminder = result_total % 10 # num images found in last page

    logging.info(f"main: total results: {result_total}")
    if reminder > 0: # calculate number of pages
        pages = (result_total // 10) + 1
    else:
        pages = result_total // 10
    logging.info(f"main: total pages: {pages}")

    try:
        for i in range(start_page_index, pages): 
            # build payload for search
            logging.info(f"main: fetching images for page: {i + 1}")
            if pages == i + 1 and reminder > 0: # final page
                payload = build_payload(query, api_key, search_engine_id, start=(i + 1)*10, num=reminder)
            else:  # all other pages
                payload = build_payload(query, api_key, search_engine_id, start=(i + 1)*10)

            response = search_images(payload) # fetch images
            items.extend(response["items"]) # store image data
            logging.info(f"main: images fetched for page: {i + 1}")
    except Exception as e:
        logging.error(f"main: no more images available: {e}")
        result_total = len(items) # update num total results

    query_string_clean = clean_filename(query) # clean query string
    df = pd.json_normalize(items) # convert to df
    filename = f"{outpath}/{query_string_clean}_start_{start_page_index}_results_{result_total}.csv"
    df.to_csv(f"{filename}", index=False)
    logging.info(f"main: images saved to {filename}.csv")


def download_image(image_url: str, save_path: str) -> str:
    """
    Downloads an image from a URL to a specified path. Returns
    a status message about download success.
    """
    try:
        urllib.request.urlretrieve(image_url, save_path)
        logging.info(f"download_image: successfully downloaded {image_url} to {save_path}")
        return "success"
    except Exception as e:
        logging.error(f"download_image: failed to download {image_url}. Error: {e}")
        return "failed"
    
def download_images_from_dataframe(df_path: str, url_column: str, output_path: str) -> None:
    """
    Loops across all the values from a column in a dataframe containing URLs
    and applies the function download_image sequentially.
    """

    df = pd.read_csv(df_path)
    
    for index, row in df.iterrows():
        image_url = row[url_column]
        save_path = os.path.join(output_path, f"image_{index}.jpg")
        status = download_image(image_url, save_path)
        logging.info(f"download_images_from_dataframe: {status} for {image_url}")


if __name__ == "__main__":
    
    # load environment variables
    API_KEY = os.environ.get("API_KEY")
    SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
    OUTPATH = os.environ.get("OUTPATH")
    START_PAGE_INDEX = int(os.environ.get("START_PAGE_INDEX")) # needs to be integer (num_page - 1)
    SEARCH_QUERY = os.environ.get("SEARCH_QUERY")
    TOTAL_RESULTS = int(os.environ.get("TOTAL_RESULTS")) # needs to be integer

    # set up search query and store results
    main(SEARCH_QUERY, API_KEY, SEARCH_ENGINE_ID, START_PAGE_INDEX, OUTPATH, TOTAL_RESULTS)