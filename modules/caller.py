from pygbif import occurrences as occ
from pygbif import species

import requests
import shutil
import uuid
import sys
from rich.console import Console
from rich import print

from urllib.parse import urlparse
from os.path import splitext
from requests.exceptions import ReadTimeout


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
    except ReadTimeout:
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
    lookup_result = species.name_lookup(scientific_name)
    if lookup_result["count"] == 0:
        print("Scientific name appears to be invalid. Exiting")
        sys.exit(1)
    print(
        f"Match successful. Fetching images for: [bold blue]{lookup_result['results'][0]['species']}"
    )
    sci_name_parsed = lookup_result["results"][0]["species"]
    with console.status("[bold green]Assembling image list..."):
        while len(image_set) < request_n_images:
            results = occ.search(
                mediaType="StillImage",
                basisOfRecord="PRESERVED_SPECIMEN",
                scientificName=sci_name_parsed,
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
