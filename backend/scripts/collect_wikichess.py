import csv
import re
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_URL = "https://ficgs.com"

START_URLS = [
    "https://ficgs.com/wikichess_1.html",
    "https://ficgs.com/wikichess_3.html",
]

OUTPUT_FILE = Path("data/wikichess_articles.csv")

MAX_ARTICLES = 10
MAX_PAGES = 60
MIN_TEXT_LENGTH = 150
REQUEST_DELAY = 2

USER_AGENT = "ChessAIAgent/0.1 (educational project)"

ARTICLE_PATTERN = re.compile(
    r"^/wikichess_\d+\.html$"
)

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

robots = RobotFileParser()
robots.set_url(f"{BASE_URL}/robots.txt")

try:
    robots.read()
    robots_available = True
except Exception as exc:
    print(f"Impossible de vérifier robots.txt : {exc}")
    robots_available = False


# ============================================================
# 2. FONCTIONS UTILITAIRES
# ============================================================

def normalize_url(url):
    """Conserve uniquement les URL d'articles Wikichess."""

    absolute_url = urljoin(BASE_URL, url)
    parsed = urlparse(absolute_url)

    if parsed.netloc.lower() not in {
        "ficgs.com",
        "www.ficgs.com",
    }:
        return None

    if not ARTICLE_PATTERN.fullmatch(parsed.path):
        return None

    return f"{BASE_URL}{parsed.path}"


def extract_links(soup):
    """Récupère les liens vers d'autres articles Wikichess."""

    links = set()

    for tag in soup.find_all("a", href=True):
        url = normalize_url(tag["href"])

        if url:
            links.add(url)

    return sorted(links)


def extract_article(soup, url):
    """
    Extrait le contenu textuel d'une page Wikichess.

    Les éléments de navigation et les contenus non pertinents
    seront filtrés progressivement après inspection.
    """

    for tag in soup([
        "script",
        "style",
        "noscript",
        "iframe",
    ]):
        tag.decompose()

    # Recherche des paragraphes explicatifs.
    paragraphs = []

    for tag in soup.find_all(["p", "td", "div"]):
        text = tag.get_text(" ", strip=True)

        if len(text) < 80:
            continue

        if "Wikichess" in text[:100] and len(text) > 3000:
            continue

        if text not in paragraphs:
            paragraphs.append(text)

    # Évite de répéter les textes imbriqués.
    filtered = []

    for text in sorted(paragraphs, key=len):
        if not any(text in other for other in filtered):
            filtered.append(text)

    content = "\n\n".join(filtered)

    # Évite de conserver une page sans texte exploitable.
    if len(content) < MIN_TEXT_LENGTH:
        return None

    article_id = re.search(
        r"wikichess_(\d+)",
        url,
    ).group(1)

    return {
        "article_id": article_id,
        "source": "Wikichess - FICGS",
        "url": url,
        "content": content,
        "text_length": len(content),
    }


# ============================================================
# 3. COLLECTE DES ARTICLES
# ============================================================

def collect_articles():

    if not robots_available:
        print("Collecte arrêtée : robots.txt non vérifié.")
        return []

    queue = deque(START_URLS)

    visited = set()
    articles = []

    while (
        queue
        and len(articles) < MAX_ARTICLES
        and len(visited) < MAX_PAGES
    ):

        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        if not robots.can_fetch(USER_AGENT, url):
            print(f"Accès non autorisé par robots.txt : {url}")
            continue

        print(f"\nAnalyse : {url}")

        try:
            response = session.get(
                url,
                timeout=20,
            )

            response.raise_for_status()
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            article = extract_article(soup, url)

            if article:
                articles.append(article)

                print(
                    f"Article retenu : "
                    f"{article['article_id']} "
                    f"({article['text_length']} caractères)"
                )

            else:
                print("Page ignorée : texte insuffisant.")

            for link in extract_links(soup):
                if link not in visited and link not in queue:
                    queue.append(link)

        except requests.RequestException as exc:
            print(f"Erreur HTTP : {exc}")

        time.sleep(REQUEST_DELAY)

    return articles


# ============================================================
# 4. EXPORT CSV
# ============================================================

def save_articles(articles):

    if not articles:
        print("\nAucun article exploitable trouvé.")
        return

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "article_id",
                "source",
                "url",
                "content",
                "text_length",
            ],
        )

        writer.writeheader()
        writer.writerows(articles)

    print("\n===================================")
    print("COLLECTE TERMINÉE")
    print("===================================")

    print(f"Articles collectés : {len(articles)}")
    print(f"Fichier enregistré : {OUTPUT_FILE}")


# ============================================================
# 5. EXÉCUTION
# ============================================================

if __name__ == "__main__":

    articles = collect_articles()

    save_articles(articles)