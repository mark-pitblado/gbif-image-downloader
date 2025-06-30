from pygbif import occurrences as occ
from pygbif import species

import requests
import shutil
import uuid
import json
import sys
import os
from rich.console import Console
from rich import print

from urllib.parse import urlparse
from os.path import splitext
from requests.exceptions import ReadTimeout, HTTPError, Timeout, RequestException
from dotenv import load_dotenv

from .checker import is_valid_url
from .statistics import create_http_pie_chart


def get_ext(url):
    """Return the filename extension for a url"""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext


def download_image(filename: str, url="", directory="") -> int:
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
    return r.status_code


def get_images_by_sciname(
    scientific_name: str, request_n_images=20, strict_mode=False
) -> set():
    """
    Calls GBIF to get a set of image urls for a given scientific name. Also returns the occurrence ids for each of the images successfully retrieved so that they can be used later to assemble the DOI.
    """
    load_dotenv()
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
    if os.getenv("COLLECT_STATISTICS"):
        collect_statistics = True
    else:
        collect_statistics = False
    with console.status("[bold green]Downloading images: ") as s:
        license_dict = {}
        statistics = {}
        offset_counter = 0
        success_counter = 0
        while success_counter <= request_n_images:
            s.update(f"{success_counter} images downloaded")
            results = occ.search(
                mediaType="StillImage",
                basisOfRecord="PRESERVED_SPECIMEN",
                scientificName=sci_name_parsed,
                limit=20,
                offset=(offset_counter * 20),
            )
            if len(results) == 0:
                raise ValueError(
                    "There were not enough images that match your criteria available to fulfil the request"
                )
            offset_counter += 1
            for r in results["results"]:
                if strict_mode:
                    if r["publishingOrg"] not in os.getenv("APPROVED_PUBLISHERS"):
                        continue
                # Log the license that is with the record.
                # Crude implementation, checks if the first image listed has the fields
                # needed, if not, just moves to the next. Some publishers may have metadata
                # only, and not the image itself.
                try:
                    if (
                        r["media"][0]["format"] == "image/jpeg"
                        or r["media"][0]["format"] == "image/png"
                    ):
                        image_status_code = download_image(
                            filename=f"{r['key']}",
                            url=r["media"][0]["identifier"],
                            directory="output",
                        )
                        if collect_statistics:
                            try:
                                statistics[image_status_code] += 1
                            except KeyError:
                                statistics[image_status_code] = 0
                            if image_status_code == 200:
                                gbif_ids.add(r["key"])
                                license_dict[r["key"]] = r["license"]
                                success_counter += 1
                except KeyError:
                    license_dict.pop(r["key"], None)
                    continue
        with open("output/licenses.json", "w") as f:
            json.dump(license_dict, f)
        with open("output/ids.txt", "w") as ids:
            for id in gbif_ids:
                ids.write(f"{id}\n")
    if collect_statistics:
        create_http_pie_chart(statistics)


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
