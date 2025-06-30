import os
import glob


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
