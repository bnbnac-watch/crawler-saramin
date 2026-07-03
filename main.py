import logging
import os
from dataclasses import asdict

from aiohttp import web
from playwright.async_api import async_playwright

from crawler import SaraminCrawler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PLAYWRIGHT_WS = os.getenv("PLAYWRIGHT_WS_ENDPOINT", "ws://watch-playwright:3000")

_crawler = SaraminCrawler()


async def health(request):
    return web.json_response({"status": "ok"})


async def crawl(request):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect(PLAYWRIGHT_WS)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                items = await _crawler.crawl(page)
                logger.info("crawl 완료: %d개", len(items))
                return web.json_response([asdict(item) for item in items])
            finally:
                await context.close()
    except Exception as e:
        logger.error("crawl 실패: %s", e)
        return web.json_response({"error": str(e)}, status=500)


app = web.Application()
app.router.add_get("/health", health)
app.router.add_post("/crawl", crawl)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
