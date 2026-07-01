import os
from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
from crawler import SaraminCrawler

PLAYWRIGHT_WS = os.getenv("PLAYWRIGHT_WS_ENDPOINT", "ws://watch-playwright:3000")

app = FastAPI()
_crawler = SaraminCrawler()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/crawl")
async def crawl():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect(PLAYWRIGHT_WS)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                items = await _crawler.crawl(page)
                return [asdict(item) for item in items]
            finally:
                await context.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
