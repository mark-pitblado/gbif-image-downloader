from modules.caller import get_images_by_sciname, download_image

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
    images = get_images_by_sciname(
        scientific_name=scientific_name, request_n_images=request_n_images
    )
    for image in track(images, description="Downloading images:"):
        download_image(url=image)


if __name__ == "__main__":
    main()
