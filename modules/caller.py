import json
import os
import shutil
import sys
import tomllib
import uuid
from os.path import splitext
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from pygbif import occurrences as occ
from pygbif import species
from requests.exceptions import HTTPError, ReadTimeout, RequestException, Timeout
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text
from rich.traceback import install

from .checker import is_valid_url
from .statistics import create_http_pie_chart, image_license_described

install(show_locals=False)
c = Console()


def get_ext(url):
    """Return the filename extension for a url"""
    parsed = urlparse(url)
    root, ext = splitext(parsed.path)
    return ext


def load_search_params(path="search_parameters.toml"):
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)  # Returns a dict; may be empty
    except FileNotFoundError:
        print("Search parameter file not found")
        return {}


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
    lookup_result = species.name_lookup(scientific_name)
    if lookup_result["count"] == 0:
        print("Scientific name appears to be invalid. Exiting")
        sys.exit(1)
    print(
        f"Scientific name is valid. Fetching images for: [bold blue]{lookup_result['results'][0]['species']}"
    )
    sci_name_parsed = lookup_result["results"][0]["species"]
    collect_statistics = bool(os.getenv("COLLECT_STATISTICS"))
    license_dict = {}
    http_statistics = {}
    number_of_explicitly_licensed_images = 0
    req_increment = min(max(50, request_n_images * 2), 300)
    offset_counter = 0
    success_counter = 0

    search_cfg = load_search_params()

    with Progress() as progress:
        task = progress.add_task("[green]Downloading images: ", total=request_n_images)
        while success_counter < request_n_images:
            # Base arguments are always present
            base_args = {
                "scientificName": sci_name_parsed,
                "mediaType": "StillImage",
                "limit": req_increment,
                "offset": offset_counter * req_increment,
            }

            if search_cfg:  # True when dict has at least one key
                api_kwargs = {**base_args, **search_cfg}
            else:
                api_kwargs = base_args
            results = occ.search(
                **api_kwargs,
            )
            if len(results["results"]) == 0:
                progress.stop()
                msg = Text(
                    "Unfortunately, there were not enough images to meet your request. Stopping and providing all images found.",
                    style="bold yellow",
                )
                c.print(Panel(msg, border_style="yellow", expand=False))
                break
            offset_counter += 1
            for r in results["results"]:
                if strict_mode:
                    if r["publishingOrg"] not in os.getenv("APPROVED_PUBLISHERS"):
                        continue
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
                                http_statistics[image_status_code] += 1
                            except KeyError:
                                http_statistics[image_status_code] = 0
                        if image_status_code == 200:
                            if collect_statistics:
                                if image_license_described(r["media"]):
                                    number_of_explicitly_licensed_images += 1
                            gbif_ids.add(r["key"])
                            license_dict[r["key"]] = r["license"]
                            success_counter += 1
                            progress.update(task, advance=1)
                            if success_counter >= request_n_images:
                                break
                except KeyError:
                    continue

    with open("output/licenses.json", "w") as f:
        json.dump(license_dict, f)
    with open("output/ids.txt", "w") as ids:
        for id in gbif_ids:
            ids.write(f"{id}\n")
    if collect_statistics:
        create_http_pie_chart(http_statistics)
        with open("statistics/image_licenses.txt", "w") as img_licenses:
            img_licenses.write(
                f"{number_of_explicitly_licensed_images} images had an explicit license"
            )


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
