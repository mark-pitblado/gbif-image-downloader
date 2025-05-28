from pygbif import occurrences as occ

import requests
import shutil
import uuid
from rich.console import Console

from urllib.parse import urlparse
from os.path import splitext
from requests.exceptions import ReadTimeout, HTTPError, Timeout, RequestException


def get_ext(url):
    """Return the filename extension for a url"""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext


def download_image(url="", directory=""):
    """
    Downloads an image by calling the url.
    """
    try:
        r = requests.get(url, stream=True, timeout=3)
    except (ReadTimeout, HTTPError, Timeout, ConnectionError, RequestException):
        return None
    # Generate a random UUID for the image, we don't care what the original name was
    filename = uuid.uuid4()
    if r.status_code == 200:
        ext = get_ext(url)
        if ext == "":
            ext = ".jpg"  # Default to jpg if no extension is listed.
        with open(f"output/{filename}{ext}", "wb") as out_file:
            shutil.copyfileobj(r.raw, out_file)
    del r


def get_images_by_sciname(scientific_name: str, request_n_images=20) -> set():
    """
    Calls GBIF to get a set of image urls for a given scientific name.
    """
    image_set = set()
    counter = 0
    console = Console()

    with console.status("[bold green]Assembling image list..."):
        while len(image_set) < request_n_images:
            results = occ.search(
                mediaType="StillImage",
                basisOfRecord="PRESERVED_SPECIMEN",
                scientificName=scientific_name,
                limit=request_n_images,
                offset=counter,
            )
            counter += 1
            for r in results["results"]:
                # Crude implementation, checks if the first image listed has the fields
                # needed, if not, just moves to the next. Some publishers may have metadata
                # only, and not the image itself.
                try:
                    if r["media"][0]["format"] == "image/jpeg":
                        image_set.add(r["media"][0]["identifier"])
                except KeyError:
                    continue
    return image_set
