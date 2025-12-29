from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cloudscraper
import xml.etree.ElementTree as ET

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
