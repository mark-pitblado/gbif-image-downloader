import os
import glob


def read_integers_to_set(filename):
    with open(filename, "r") as file:
        return {int(line.strip()) for line in file}


def clean_excess_images(n_images: int):
    """
    Reduces the number of images in the output directory down to the number requested.
    """
    image_extensions = "*.jpg"
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join("output", ext)))
    # Sort images by modificaiton time (no real to do, or not do this, over any other method)
    image_files.sort(key=os.path.getmtime)
    # 3 is a magic number here, handles the license.json and the id.txt
    while len(image_files) > n_images + 3:
        oldest_image = image_files.pop(0)
        os.remove(oldest_image)
