from modules.caller import get_images_by_sciname, download_image, request_download
from modules.files import read_integers_to_set

from rich.progress import track
from rich.console import Console


def main():
    console = Console()
    scientific_name = console.input(
        "Which scientific name would you like to fetch images for? "
    )
    request_n_images = int(
        console.input("What is the minimum number of images that you need? ")
    )
    input = console.input("Would you like to enable strict mode? (y/n)")
    gbif_username = console.input("What is your GBIF username? ")
    gbif_password = console.input("What is your GBIF password? ", password=True)
    email = console.input("Which email should the download notification be sent to? ")
    strict_mode = True if input == "y" else False
    images = get_images_by_sciname(
        scientific_name=scientific_name,
        request_n_images=request_n_images,
        strict_mode=strict_mode,
    )
    if len(images) > 0:
        counter = 0
        for image in track(images, description="Downloading images:"):
            download_image(
                filename=str(scientific_name.replace(" ", "-") + "_" + str(counter)),
                url=image,
            )
            counter += 1
    # Request a download to get the DOI
    gbif_ids = read_integers_to_set("output/ids.txt")
    request_download(
        gbif_ids, email=email, gbif_username=gbif_username, gbif_password=gbif_password
    )


if __name__ == "__main__":
    main()
