import sys
from PIL import Image
from parse_products import parse_pages, LABEL_URLS
from yaml import load
import dateparser
import pytz
import argparse
import math
import os
import requests
import shutil


def download_release(release):
    url = release["image_url"]
    filename = os.path.basename(url)
    path = "image_cache/" + filename
    if os.path.exists(path):
        return path
    print("Downloading {} to {}...".format(filename, path))
    r = requests.get(url, stream=True)
    with open(path, "wb") as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
    return path


def download_images(data):
    return list(map(lambda x: (x, download_release(x)), data))


def generate_collage(data, key_dates, blacklist, key_start, key_end, square_size, rows=None, cols=None, **kwargs):
    # First, find the start and end key dates
    start_key = next(x for x in key_dates if x["name"] == key_start)
    end_key = next(x for x in key_dates if x["name"] == key_end)

    # Next, find all the releases in between the key dates
    releases = [x for x in data if start_key["date"]
                < x["release_date"] < end_key["date"]]
    
    # Remove blacklisted releases
    releases = [x for x in releases if x["id"] not in blacklist]

    # Next, find all key dates between the start and end (inclusive)
    relevant_key_dates = [
        x for x in key_dates if start_key["date"] <= x["date"] <= end_key["date"]]

    # Now, calculate the size of the collage
    # If rows and cols are both given, just use that
    # Otherwise, if rows is given, use that many rows and calculate cols to match
    # Otherwise, if cols is given, use that many and calculate rows to match
    # Otherwise, get the collage to be as square-ish as possible
    number_of_things = len(releases) + len(relevant_key_dates)
    final_rows = 0
    final_cols = 0
    if rows is not None and cols is not None:
        final_rows = rows
        final_cols = cols
    elif rows is None and cols is not None:
        final_cols = cols
        final_rows = math.ceil(number_of_things / cols)
    elif cols is None and rows is not None:
        final_rows = rows
        final_cols = math.ceil(number_of_things / rows)
    else:
        side_len = math.sqrt(number_of_things)
        final_rows = math.ceil(side_len)
        final_cols = math.ceil(side_len)

    print("Creating a {}x{} collage ({})".format(
        final_rows, final_cols, number_of_things))

    img = Image.new("RGB", (final_cols * square_size,
                            final_rows * square_size))

    image_urls = download_images(releases)

    image_urls.extend([(x, x["image"]) for x in relevant_key_dates])

    image_urls = sorted(image_urls, key=lambda x: x[0]["date"] if "date" in x[0] else x[0]["release_date"])

    for idx, val in enumerate(image_urls):
        release, image_url = val
        # We special-case the last release
        if idx + 1 == len(image_urls):
            row = final_rows - 1
            col = final_cols - 1
        else:
            row = math.floor(idx / final_rows)
            col = math.floor(idx % final_rows)
        rel = Image.open(image_url)
        resized = rel.resize((square_size, square_size))
        img.paste(resized, (col * square_size, row * square_size))
    
    img.save("collage.png", "PNG")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("label", type=str, help="Which label to generate for")
    parser.add_argument(
        "pages", type=int, help="How many pages of releases to scrape from music.anjunabeats.com")
    parser.add_argument("key_start", type=str,
                        help="Which key date should we generate from")
    parser.add_argument("key_end", type=str,
                        help="Which key date should we generate until")
    parser.add_argument("--rows", type=int,
                        help="How many rows of releases should we generate")
    parser.add_argument("--cols", type=int,
                        help="How many columns of releases should we generate")
    parser.add_argument("--square_size", type=int,
                        help="How big should each square be", default=800)
    args = vars(parser.parse_args())

    with open("key_dates.yaml", "r") as key_stream:
        key_dates = load(key_stream)
        key_dates = list(map(lambda x: {
                         **x, "date": dateparser.parse(x["date"]).replace(tzinfo=pytz.UTC)}, key_dates))
        with open("blacklist.yaml", "r") as blacklist_stream:
            blacklist = load(blacklist_stream)
            data = parse_pages(LABEL_URLS[args["label"]], args["pages"])
            generate_collage(data, key_dates, blacklist, **args)
