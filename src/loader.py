import json
import logging
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class Document:
    url: str
    title: str
    content: str


def fetch_url(url: str) -> Document | None:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else url
        text = soup.get_text(separator="\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = text.strip()

        return Document(url=url, title=title, content=text)
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def load_local_file(path: str, source_url: str = "") -> Document | None:
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        title = content.split("\n", 1)[0].lstrip("# ").strip() if content else path
        return Document(url=source_url or path, title=title, content=content)
    except Exception as e:
        logger.error(f"Failed to read {path}: {e}")
        return None


def load_sources(sources_path: str = "data/sources.json") -> list[Document]:
    with open(sources_path) as f:
        data = json.load(f)

    documents = []
    for source in data["sources"]:
        local_path = source.get("local_path")
        if local_path:
            doc = load_local_file(local_path, source_url=source.get("url", local_path))
        else:
            doc = fetch_url(source["url"])

        if doc:
            documents.append(doc)
        else:
            logger.warning(f"Skipped: {source.get('url') or source.get('local_path')}")

    return documents
