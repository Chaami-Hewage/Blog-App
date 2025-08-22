import csv
import os
import time
from dataclasses import dataclass, asdict
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.midnightdivas.com"


@dataclass
class Product:
    title: str
    description: str
    price: str
    url: str
    category: str


def fetch(url: str) -> Optional[str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception:
        return None


def parse_product(product_url: str, category: str) -> Optional[Product]:
    html = fetch(product_url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html5lib")

    title_tag = soup.select_one("h1.product-title, h1.product__title, h1")
    title = title_tag.get_text(strip=True) if title_tag else ""

    desc_tag = soup.select_one(".product__description, #tab-description, .description, .product-info__description")
    description = desc_tag.get_text("\n", strip=True) if desc_tag else ""

    price_tag = soup.select_one(".price .money, .product__price, .price")
    price = price_tag.get_text(strip=True) if price_tag else ""

    return Product(title=title, description=description, price=price, url=product_url, category=category)


def parse_collection(collection_url: str, category: str) -> List[str]:
    html = fetch(collection_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html5lib")
    product_links = []
    for a in soup.select("a[href*='/products/']"):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("/"):
            href = BASE_URL + href
        if "/products/" in href and href not in product_links:
            product_links.append(href)
    return list(dict.fromkeys(product_links))


def scrape_to_csv(collection_urls: List[str], out_csv: str) -> None:
    products: List[Product] = []
    for url in collection_urls:
        category = url.rstrip("/").split("/")[-1]
        links = parse_collection(url, category)
        time.sleep(1)
        for link in links:
            prod = parse_product(link, category)
            if prod and prod.title:
                products.append(prod)
            time.sleep(0.5)

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "description", "price", "url", "category"])
        writer.writeheader()
        for p in products:
            writer.writerow(asdict(p))


if __name__ == "__main__":
    # Example categories; adjust as needed
    collections = [
        f"{BASE_URL}/collections/lingerie",
        f"{BASE_URL}/collections/babydolls",
        f"{BASE_URL}/collections/bra-and-panty-sets",
    ]
    scrape_to_csv(collections, "data/products.csv")