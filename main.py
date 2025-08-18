import os

from modules.caller import get_images_by_sciname, request_download
from modules.files import read_integers_to_set, clean_excess_images

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
    input = console.input("Would you like to enable strict mode? (y/n) ")
    gbif_username = (
        os.getenv("GBIF_USERNAME")
        if os.getenv("GBIF_USERNAME")
        else console.input("What is your GBIF username? ")
    )
    gbif_password = (
        os.getenv("GBIF_PASSWORD")
        if os.getenv("GBIF_PASSWORD")
        else console.input("What is your GBIF password? ", password=True)
    )
    email = (
        os.getenv("GBIF_NOTIFICATION_EMAIL")
        if os.getenv("GBIF_NOTIFICATION_EMAIL")
        else console.input("Which email should the citation email be sent to? ")
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
