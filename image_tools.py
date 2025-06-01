# image_tools.py
import os
import requests
import boto3
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

SAVE_DIR = "./downloaded_images"
os.makedirs(SAVE_DIR, exist_ok=True)
REGION = os.getenv("BUCKET_REGION")
# AWS S3 setup
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
    region_name=REGION,
)
BUCKET_NAME = os.getenv("BUCKET_NAME")

def search_and_download_image(query):
    print(f"extracting the product name from the given Query and searching for that image: {query}")
    params = {
        "q": query,
        "tbm": "isch",
        "engine": "google",
        "ijn": "0",
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }

    res = requests.get("https://serpapi.com/search.json", params=params)
    data = res.json()

    if "images_results" not in data or not data["images_results"]:
        raise Exception("No image results found.")

    img_url = data["images_results"][0]["original"]
    img_data = requests.get(img_url).content

    filename = f"{quote_plus(query)}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(img_data)

    s3.upload_file(filepath, BUCKET_NAME, filename)

    # Return only the image filename
    return filename
