import logging

from bs4 import BeautifulSoup
from watch_contract import RenderCrawler, Item, CrawlerException

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


class SaraminCrawler(RenderCrawler):
    def render_request(self, params: dict) -> dict:
        keyword = params.get("keyword", "SLAM")
        return {
            "url": _SEARCH_URL.format(keyword=keyword),
            "wait_for": _JOB_SELECTOR,
        }

    def parse(self, html: str, params: dict) -> list[Item]:
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
