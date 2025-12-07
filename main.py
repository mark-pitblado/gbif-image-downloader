import os

from dotenv import load_dotenv
from rich.console import Console

from modules.caller import get_images_by_sciname, request_download
from modules.files import create_output_dir, clean_excess_images, read_integers_to_set


def main():
    console = Console()
    load_dotenv()
    # Create an output directory for the user based on a selected prefix (allows them to have multiple output dirs easily)
    output_dir = create_output_dir()
    scientific_name = console.input(
        "Which scientific name would you like to fetch images for? "
    )
    request_n_images = int(console.input("How many images would you like to fetch? "))
    strict_mode_input = console.input("Would you like to enable strict mode? (y/n) ")
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
    strict_mode = True if strict_mode_input == "y" else False
    get_images_by_sciname(
        scientific_name=scientific_name,
        request_n_images=request_n_images,
        strict_mode=strict_mode,
        output_dir=output_dir,
    )

    # Clean excess images
    clean_excess_images(request_n_images, id_filepath=f"{output_dir}/ids.txt")

    # Request a download to get the DOI
    gbif_ids = read_integers_to_set(f"{output_dir}/ids.txt")
    request_download(
        gbif_ids, email=email, gbif_username=gbif_username, gbif_password=gbif_password
    )
    print(
        "Process complete. An email with a DOI for your the occurrences associated with the images should arrive shortly."
    )


if __name__ == "__main__":
    main()
