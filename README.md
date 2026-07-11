# crawler-saramin

사람인 채용공고 검색 결과 크롤러. `BaseCrawler` 구현 — `httpx`로 검색 결과 페이지를 직접 GET한다. 사람인 검색 결과는 서버사이드 렌더링(SSR)이라 JS 실행이 필요 없다.

## `watch-playwright`를 안 쓰는 이유

사람인은 Playwright의 기본 headless Chromium 지문을 차단한다(connection reset/hang). 반면 검색 결과는 SSR로 내려오므로 굳이 브라우저를 거칠 필요 없이 `httpx` + 위장 User-Agent로 바로 GET하는 게 더 안정적이다.

## API

### POST /crawl

```json
{"keyword": "SLAM"}
```

`keyword` 없으면 기본값 `"SLAM"`. `https://www.saramin.co.kr/zf_user/search/recruit?searchword={keyword}`를 GET해서 `div.item_recruit` 목록을 파싱한다.

응답: `Item[]` — `data`에 `company`, `deadline` 포함

### GET /health

`{"status": "ok"}`

## id (중복 감지 키)

```python
rec_idx = parse_qs(urlparse(href).query).get("rec_idx", [None])[0]
items.append(Item(id=rec_idx or href, ...))
```

공고 상세 링크(href)에는 `search_uuid`라는 검색 세션마다 랜덤 발급되는 쿼리스트링이 들어있다. 같은 공고라도 크롤링할 때마다 `search_uuid`가 달라져서 href를 그대로 `id`로 쓰면 매번 다른 아이템으로 오인식되어 중복 알림이 발생한다. 사람인이 공고마다 부여하는 안정적인 값인 `rec_idx`를 쿼리스트링에서 추출해 `id`로 쓴다(추출 실패 시에만 href로 폴백).

## 환경변수

없음 — 검색어는 env가 아니라 `crawlers.params.keyword`로 POST body에 실려 온다.

## 포트

| 포트 | 용도 |
|---|---|
| 8080 | aiohttp — 컴포즈 내부에서만 노출 |
