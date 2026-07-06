import logging

import httpx
from bs4 import BeautifulSoup
from watch_contract import BaseCrawler, Item, CrawlerException

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.saramin.co.kr"
_SEARCH_URL = (
    "https://www.saramin.co.kr/zf_user/search/recruit"
    "?searchType=search&searchword={keyword}&recruitPage=1"
)
# saramin은 Playwright 기본 headless 지문을 차단(connection reset/hang)하지만
# 검색 결과가 SSR로 내려오므로 JS 렌더링 없이 직접 GET으로 가져온다.
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_JOB_SELECTOR = "div.item_recruit"
_TITLE_SELECTOR = "h2.job_tit a"
_COMPANY_SELECTOR = ".corp_name a"
_DEADLINE_SELECTOR = ".job_date .date"


class SaraminCrawler(BaseCrawler):
    async def crawl(self, params: dict) -> list[Item]:
        keyword = params.get("keyword", "SLAM")
        url = _SEARCH_URL.format(keyword=keyword)
        try:
            async with httpx.AsyncClient(
                timeout=30, headers={"User-Agent": _USER_AGENT}
            ) as client:
                res = await client.get(url)
                res.raise_for_status()
                html = res.text
        except Exception as e:
            logger.error("crawl 예외: %s", e)
            raise CrawlerException(str(e)) from e

        try:
            soup = BeautifulSoup(html, "html.parser")
            items = []
            for job in soup.select(_JOB_SELECTOR):
                try:
                    title_el = job.select_one(_TITLE_SELECTOR)
                    if not title_el:
                        continue

                    title = title_el.get_text(strip=True)
                    href = title_el.get("href")
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"{_BASE_URL}{href}"

                    company_el = job.select_one(_COMPANY_SELECTOR)
                    company = company_el.get_text(strip=True) if company_el else ""

                    deadline_el = job.select_one(_DEADLINE_SELECTOR)
                    deadline = deadline_el.get_text(strip=True) if deadline_el else ""

                    items.append(Item(
                        id=href,
                        title=title,
                        url=href,
                        data={"company": company, "deadline": deadline},
                    ))
                except Exception:
                    continue

            logger.info("파싱 완료: %d개", len(items))
            return items
        except Exception as e:
            logger.error("parse 예외: %s", e)
            raise CrawlerException(str(e)) from e
