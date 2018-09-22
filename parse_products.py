import requests
from bs4 import BeautifulSoup
import sys
import dateparser


def parse_products(url, page=1):
    r = requests.get(url.format(str(page)))
    soup = BeautifulSoup(r.text, "html.parser")
    products = soup.select(".product.release")
    filtered = filter(lambda x: "product-release-date-future" not in x.find("dd",
                                                                            class_="product-release-date")["class"], products)
    data = map(lambda x: {
        "artist": x.find("dd", class_="artist").find("span").string,
        "title": x.find("dd", class_="release-title").find("a").string,
        "url": "https://music.anjunabeats.com" + x.find("dd", class_="release-title").find("a")["href"],
        "image_url": x.find("a", class_="artwork").find("img")["src"].replace("/r/s/", "/r/b/"),
        "catalogue": x.find("dd", class_="catalogue-number").string.strip(),
        "release_date": dateparser.parse(x.find("dd", class_="product-release-date").find("meta")["content"], settings={"RETURN_AS_TIMEZONE_AWARE": True}),
        "release_date_src": x.find("dd", class_="product-release-date").find("meta")["content"],
        "id": x["data-id"]
    }, filtered)
    return list(data)


def parse_pages(url, pages=5):
    result = []
    for page in range(1, pages + 1):
        print("Parsing page {}".format(page))
        data = parse_products(url, page)
        result.extend(data)
        print(len(result))
    return sorted(result, key=lambda x: x["release_date"], reverse=False)


LABEL_URLS = {
    "anjunabeats": "https://music.anjunabeats.com/music/label/6825-anjunabeats/page/{}?loadPageContentOnly=true",
    "anjunadeep": "https://music.anjunabeats.com/music/label/6826-anjunadeep/page/{}?loadPageContentOnly=true"
}

if __name__ == "__main__":
    data = parse_pages(LABEL_URLS[sys.argv[1]], int(
        sys.argv[2]) if sys.argv[2] else None)
    for product in data:
        print(repr(product))
