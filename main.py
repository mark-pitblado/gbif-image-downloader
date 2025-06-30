import os

from modules.caller import get_images_by_sciname, download_image, request_download
from modules.files import read_integers_to_set
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
    if os.getenv("COLLECT_STATISTICS"):
        statistics = True
    else:
        statistics = False
    strict_mode = True if input == "y" else False
    images = get_images_by_sciname(
        scientific_name=scientific_name,
        request_n_images=request_n_images,
        strict_mode=strict_mode,
    )
    if len(images) > 0:
        counter = 0
        http_code_tracker = {}
        for image in track(images, description="Downloading images:"):
            http_code = download_image(
                filename=str(scientific_name.replace(" ", "-") + "_" + str(counter)),
                url=image,
            )
            # Log the http code for statistics
            try:
                http_code_tracker[http_code] += 1
            except KeyError:
                http_code_tracker[http_code] = 1
            counter += 1
    if statistics:
        print(http_code_tracker)
        create_http_pie_chart(http_code_tracker)

    # Request a download to get the DOI
    gbif_ids = read_integers_to_set("output/ids.txt")
    request_download(
        gbif_ids, email=email, gbif_username=gbif_username, gbif_password=gbif_password
    )


if __name__ == "__main__":
    main()
