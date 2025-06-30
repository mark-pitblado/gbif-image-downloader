import os

from modules.caller import get_images_by_sciname, download_image, request_download
from modules.files import read_integers_to_set, clean_excess_images
from modules.statistics import create_http_pie_chart

from rich.progress import track
from rich.console import Console

from dotenv import load_dotenv


def main():
    console = Console()
    load_dotenv()
    scientific_name = console.input(
        "Which scientific name would you like to fetch images for? "
    )
    request_n_images = int(
        console.input("What is the minimum number of images that you need? ")
    )
    input = console.input("Would you like to enable strict mode? (y/n)")
    if os.getenv("GBIF_USERNAME"):
        gbif_username = os.getenv("GBIF_USERNAME")
    else:
        gbif_username = console.input("What is your GBIF username? ")
    if os.getenv("GBIF_PASSWORD"):
        gbif_password = os.getenv("GBIF_PASSWORD")
    else:
        gbif_password = console.input("What is your GBIF password? ", password=True)
    if os.getenv("GBIF_NOTIFICATION_EMAIL"):
        email = os.getenv("GBIF_NOTIFICATION_EMAIL")
    else:
        email = console.input(
            "Which email should the download notification be sent to? "
        )
    strict_mode = True if input == "y" else False
    get_images_by_sciname(
        scientific_name=scientific_name,
        request_n_images=request_n_images,
        strict_mode=strict_mode,
    )

    # Clean excess images
    clean_excess_images(request_n_images)

    # Request a download to get the DOI
    gbif_ids = read_integers_to_set("output/ids.txt")
    request_download(
        gbif_ids, email=email, gbif_username=gbif_username, gbif_password=gbif_password
    )


if __name__ == "__main__":
    main()
