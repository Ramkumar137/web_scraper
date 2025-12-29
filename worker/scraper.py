import requests
from recipe_scrapers import scrape_html

from db.postgres import fetch_next_url, mark_done, mark_failed
from db.mongo import save_recipe
from utils.delay import polite_sleep
from utils.mailer import send_email


def fetch_recipe_data(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    scraper = scrape_html(
        html=response.text,
        org_url=url,
        wild_mode=True
    )

    total_time = scraper.total_time()
    if not total_time:
        total_time = (scraper.prep_time() or 0) + (scraper.cook_time() or 0)

    data = {
        "title": scraper.title(),
        "image_url": scraper.image(),
        "ingredients": scraper.ingredients(),
        "instructions": scraper.instructions_list(),
        "total_time_minutes": total_time,
        "nutrients": scraper.nutrients(),
        "original_url": url,
    }

    if not data["ingredients"]:
        raise ValueError("No ingredients found")

    return data


def main():
    print("🚀 Scraper batch started")

    processed = 0
    failed = 0

    while True:
        job = fetch_next_url()

        if not job:
            print("✅ Queue empty. Scraping finished.")
            break

        job_id, url = job
        print(f"📥 Scraping: {url}")

        try:
            recipe = fetch_recipe_data(url)
            save_recipe(recipe)
            mark_done(job_id)
            processed += 1
            print("✅ Saved & marked done")

        except Exception as e:
            failed += 1
            print(f"❌ Failed: {e}")
            mark_failed(job_id)

        polite_sleep()

    print("📊 Scraping summary")
    print(f"   ✔ Success: {processed}")
    print(f"   ✖ Failed : {failed}")
    print("🏁 Scraping completed")


if __name__ == "__main__":
    main()
