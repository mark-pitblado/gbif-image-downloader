from pygbif import occurrences as occ
from pygbif import species

import requests
import shutil
import uuid
import json
import sys
from rich.console import Console
from rich import print

from urllib.parse import urlparse
from os.path import splitext
from requests.exceptions import ReadTimeout, HTTPError, Timeout, RequestException

from settings import APPROVED_PUBLISHERS
from .checker import is_valid_url


def get_ext(url):
    """Return the filename extension for a url"""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext


def download_image(filename: str, url="", directory=""):
    """
    Downloads an image by calling the url.
    """
    try:
        # Check for a simple response before downloading the full image
        if not is_valid_url(url):
            return None
        r = requests.get(url, stream=True, timeout=3)
    except (ReadTimeout, HTTPError, Timeout, ConnectionError, RequestException):
        return None
    filename = filename if (filename is not None) else uuid.uuid()
    if r.status_code == 200:
        ext = get_ext(url)
        if ext not in (".JPG", ".PNG", ".JPEG", ".TIF", ".TIFF", ""):
            return None
        # Assign jpeg extension for those missing an extension
        if ext == "":
            ext = ".jpg"
        with open(f"output/{filename}{ext}", "wb") as out_file:
            shutil.copyfileobj(r.raw, out_file)
    del r


def get_images_by_sciname(
    scientific_name: str, request_n_images=20, strict_mode=False
) -> set():
    """
    Calls GBIF to get a set of image urls for a given scientific name. Also returns the occurrence ids for each of the images successfully retrieved so that they can be used later to assemble the DOI.
    """
    image_urls = set()
    gbif_ids = set()
    console = Console()
    lookup_result = species.name_lookup(scientific_name)
    if lookup_result["count"] == 0:
        print("Scientific name appears to be invalid. Exiting")
        sys.exit(1)
    print(
        f"Match successful. Fetching image_urls for: [bold blue]{lookup_result['results'][0]['species']}"
    )
    sci_name_parsed = lookup_result["results"][0]["species"]
    with console.status("[bold green]Assembling image list..."):
        license_dict = {}
        offset_counter = 0
        while len(image_urls) < request_n_images:
            results = occ.search(
                mediaType="StillImage",
                basisOfRecord="PRESERVED_SPECIMEN",
                scientificName=sci_name_parsed,
                # 10 is an arbitrary number, but strikes a good balance. Too small
                # and too many requests are made. Too large and the number of image_urls
                # returned will be much more than the user asked for.
                limit=300 if request_n_images > 300 else request_n_images + 10,
                offset=(offset_counter * (request_n_images + 10))
                if request_n_images < 300
                else (offset_counter * 300),
            )
            offset_counter += 1
            license_sync_counter = 0
            for r in results["results"]:
                if strict_mode:
                    if r["publishingOrg"] not in APPROVED_PUBLISHERS:
                        continue
                # Log the license that is with the record.
                license_dict[license_sync_counter] = r["license"]
                # Crude implementation, checks if the first image listed has the fields
                # needed, if not, just moves to the next. Some publishers may have metadata
                # only, and not the image itself.
                try:
                    if r["media"][0]["format"] == "image/jpeg":
                        gbif_ids.add(r["key"])
                        image_urls.add(r["media"][0]["identifier"])
                except KeyError:
                    license_dict.pop(license_sync_counter, None)
                    continue
                license_sync_counter += 1
        with open("output/licenses.json", "w") as f:
            json.dump(license_dict, f)
        with open("output/ids.txt", "w") as ids:
            for id in gbif_ids:
                ids.write(f"{id}\n")
    return image_urls


def request_download(gbif_ids: set, email="", gbif_username="", gbif_password=""):
    """
    Requests a GBIF download for the gbif ids provided.
    """
    data = {
        "creator": gbif_username,
        "sendNotification": True,
        "notification_address": [email],
        "format": "DWCA",
        "description": "Download of requests matching image download.",
        "predicate": {"type": "in", "key": "GBIF_ID", "values": list(gbif_ids)},
        "verbatimExtensions": ["http://rs.tdwg.org/ac/terms/Multimedia"],
    }
    try:
        r = requests.post(
            "https://api.gbif.org/v1/occurrence/download/request",
            headers={"Content-Type": "application/json"},
            auth=(gbif_username, gbif_password),
            json=data,
        )
        if r.status_code != 201:
            return HTTPError(
                f"GBIF download request failed with status code {r.status_code}. Expected 201."
            )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
