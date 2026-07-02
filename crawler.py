import logging
import os
from dataclasses import asdict
from watch_contract import BaseCrawler, Item, CrawlerException

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.saramin.co.kr"
_SEARCH_URL = (
    "https://www.saramin.co.kr/zf_user/search/recruit"
    "?searchType=search&searchword={keyword}&recruitPage=1"
)

# 아래 셀렉터는 실제 페이지 구조 확인 후 수정 필요
_JOB_SELECTOR = "li.item_recruit"
_TITLE_SELECTOR = "h2.job_tit a"
_COMPANY_SELECTOR = ".corp_name a"
_DEADLINE_SELECTOR = ".job_date .date"


class SaraminCrawler(BaseCrawler):
    def __init__(self):
        self._keyword = os.getenv("SEARCH_KEYWORD", "SLAM")

    async def crawl(self, page) -> list[Item]:
        url = _SEARCH_URL.format(keyword=self._keyword)
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector(_JOB_SELECTOR, timeout=10000)

            jobs = await page.query_selector_all(_JOB_SELECTOR)
            items = []
            for job in jobs:
                try:
                    title_el = await job.query_selector(_TITLE_SELECTOR)
                    if not title_el:
                        continue

                    title = (await title_el.inner_text()).strip()
                    href = await title_el.get_attribute("href")
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"{_BASE_URL}{href}"

                    company_el = await job.query_selector(_COMPANY_SELECTOR)
                    company = (await company_el.inner_text()).strip() if company_el else ""

                    deadline_el = await job.query_selector(_DEADLINE_SELECTOR)
                    deadline = (await deadline_el.inner_text()).strip() if deadline_el else ""

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
            logger.error("crawl 예외: %s", e)
            raise CrawlerException(str(e)) from e
