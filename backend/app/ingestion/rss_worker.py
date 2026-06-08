import logging
import feedparser
import httpx
from bs4 import BeautifulSoup
from app.models.relationships import ArticleIngestion
from app.ingestion.deduplicator import is_processed, mark_processed
from app.ingestion.mapper import map_to_graph
from app.services.extraction_service import extract_entities

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "Light Reading": "https://www.lightreading.com/rss.xml",
    "Fierce Telecom": "https://www.fiercetelecommunications.com/rss.xml",
    "Fierce Wireless": "https://www.fiercewireless.com/rss.xml",
    "RCR Wireless": "https://www.rcrwireless.com/feed",
    "SDxCentral": "https://www.sdxcentral.com/feed/",
    "Telecom TV": "https://www.telecomtv.com/rss/",
    "3GPP News": "https://www.3gpp.org/news-events/news/feed",
    "GSMA News": "https://www.gsma.com/newsroom/feed/",
    "ITU News": "https://www.itu.int/en/mediacentre/newsroom/Feed/Pages/default.aspx",
    "O-RAN Alliance": "https://www.o-ran.org/blog?format=rss",
    "Telegeography": "https://www.telegeography.com/products/commsupdate/rss.xml",
    "The Verge Tech": "https://www.theverge.com/tech/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
}

HEADERS = {"User-Agent": "TMT-Knowledge-Graph-Bot/1.0 (research; contact@tmt-kg.io)"}


async def fetch_article_text(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers=HEADERS)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        article_tag = soup.find("article") or soup.find("main") or soup.body
        paragraphs = article_tag.find_all("p") if article_tag else []
        return " ".join(p.get_text(strip=True) for p in paragraphs[:30])
    except Exception as e:
        logger.debug(f"Failed to fetch {url}: {e}")
        return ""


async def poll_all_feeds(driver) -> int:
    processed_count = 0
    for source, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # process latest 10 per feed
                url = getattr(entry, "link", "")
                if not url or await is_processed(url):
                    continue
                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "")
                published = str(getattr(entry, "published", ""))
                full_text = await fetch_article_text(url)
                content = full_text or summary
                if len(content) < 100:
                    await mark_processed(url)
                    continue
                article = ArticleIngestion(
                    title=title, url=url, source=source,
                    published_at=published, content=content,
                )
                try:
                    extraction = await extract_entities(content, title, source)
                    new_rels = await map_to_graph(extraction, article, driver)
                    if new_rels > 0:
                        logger.info(f"[{source}] '{title[:60]}' → {new_rels} new relationships")
                    processed_count += 1
                except Exception as e:
                    logger.warning(f"Extraction failed for {url}: {e}")
                await mark_processed(url)
        except Exception as e:
            logger.warning(f"Failed to poll {source}: {e}")
    return processed_count
