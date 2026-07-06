import logging
from dataclasses import asdict

from aiohttp import web

from crawler import SaraminCrawler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_crawler = SaraminCrawler()


async def health(request):
    return web.json_response({"status": "ok"})


async def crawl(request):
    try:
        body = await request.json() if request.can_read_body else {}
        items = await _crawler.crawl(body)
        logger.info("crawl 완료: %d개", len(items))
        return web.json_response([asdict(item) for item in items])
    except Exception as e:
        logger.error("crawl 실패: %s", e)
        return web.json_response({"error": str(e)}, status=500)


app = web.Application()
app.router.add_get("/health", health)
app.router.add_post("/crawl", crawl)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
