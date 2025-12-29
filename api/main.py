from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cloudscraper
import xml.etree.ElementTree as ET
from db.mongo import get_recipes, get_recipe_by_id, recipes
from fastapi import HTTPException
from bson.errors import InvalidId



from db.postgres import insert_urls
from utils.mailer import send_email


app = FastAPI(title="Cookit Ingestion API")


class SitemapRequest(BaseModel):
    sitemap_url: str
    source: str = "bbcgoodfood"
    notify_email: str | None = None


def fetch_sitemap_urls(sitemap_url: str):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(sitemap_url)

    if response.status_code != 200:
        raise HTTPException(400, "Failed to fetch sitemap")

    root = ET.fromstring(response.content)

    if '}' in root.tag:
        ns = {'ns': root.tag.split('}')[0].strip('{')}
        locs = root.findall('ns:url/ns:loc', ns)
    else:
        locs = root.findall('url/loc')

    return [loc.text for loc in locs if loc is not None]


@app.get("/")
def root():
    return {"status": "Cookit Scraper API is running"}


@app.post("/upload-sitemap")
def upload_sitemap(data: SitemapRequest):
    urls = fetch_sitemap_urls(data.sitemap_url)

    if not urls:
        raise HTTPException(400, "No URLs found")

    insert_urls(urls, source=data.source)

    if data.notify_email:
        send_email(
            "Cookit – URLs Queued",
            f"{len(urls)} URLs added to scraping queue.",
            data.notify_email
        )

    return {
        "message": "URLs queued successfully",
        "total_urls": len(urls)
    }


@app.get("/recipes")
def list_recipes(limit: int = 20):
    data = get_recipes(limit)
    for r in data:
        r["_id"] = str(r["_id"])
    return data


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: str):
    try:
        recipe = get_recipe_by_id(recipe_id)
    except InvalidId:
        raise HTTPException(400, "Invalid recipe ID")

    if not recipe:
        raise HTTPException(404, "Recipe not found")

    recipe["_id"] = str(recipe["_id"])
    return recipe

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/mongo-health")
def mongo_health():
    recipes.find_one()
    return {"mongo": "ok"}
