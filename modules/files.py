import glob
import os
import sys
from pathlib import Path
from rich.console import Console

console = Console()


def get_valid_prefix():
    while True:
        prefix = console.input("Enter a prefix for the output directory: ").strip()
        if not prefix:
            console.print("[red]Prefix cannot be empty.[/red]")
            continue
        # Disallow characters that are invalid for folder names on most OSes
        if any(c in r'<>:"/\|?*' for c in prefix):
            console.print("[red]Prefix contains illegal characters.[/red]")
            continue
        return prefix


def confirm_overwrite(path: Path) -> bool:
    answer = (
        console.input(f"The directory '{path}' already exists. Overwrite? (y/N): ")
        .strip()
        .lower()
    )
    return answer == "y"


def create_output_dir():
    prefix = get_valid_prefix()
    out_path = Path(f"{prefix}-output")

    if out_path.exists():
        if not confirm_overwrite(out_path):
            console.print("[yellow]Operation cancelled.[/yellow]")
            sys.exit(0)
        # Remove existing contents safely
        for child in out_path.iterdir():
            if child.is_file():
                child.unlink()
            else:
                # Recursively delete sub‑directories
                import shutil

                shutil.rmtree(child)
    else:
        out_path.mkdir(parents=True)

    console.print(f"[green]Output directory ready:[/green] {out_path}")
    return str(out_path)


def read_integers_to_set(filename):
    with open(filename, "r") as file:
        return {int(line.strip()) for line in file}


def clean_excess_images(n_images: int, id_filepath="output/ids.txt"):
    """
    Reduces the number of images in the output directory down to the number requested.
    """
    image_extensions = ["*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join("output", ext)))
    # Sort images by modificaiton time (no real to do, or not do this, over any other method)
    image_files.sort(key=os.path.getmtime)

    # Read the ids.txt file to get the id numbers logged
    if os.path.exists(id_filepath):
        with open(id_filepath, "r") as f:
            lines = f.read().splitlines()
    else:
        lines = []

    # Remove excess images and update txt file

    while len(image_files) >= n_images + 1:
        image_path = image_files.pop(0)
        filename = os.path.splitext(os.path.basename(image_path))[0]
        os.remove(image_path)
        lines = [line for line in lines if line.strip() != filename]

    with open(id_filepath, "w") as f:
        f.write("\n".join(lines))
