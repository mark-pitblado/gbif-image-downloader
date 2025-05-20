# Bulk GBIF Image Downloader

This is a simple tool to download images from the [Global Biodiversity Information Facility (GBIF)](https://gbif.org) by scientific name. Only records that are labeled as Preserved Specimens will be downloaded, Human Observations are not included.

## Setup

Clone the repository

```bash
git clone https://github.com/mark-pitblado/gbif-image-downloader
cd gbif-image-downloader
```

Install the dependencies using [uv](https://docs.astral.sh/uv/). There are only three, `pygbif`, `requests` and `rich`

```bash
uv sync
``` 

Create the `/output` directory for downloaded images to go in.

```bash
mkdir output
```

## Usage

Run the following from the terminal. The program will ask for the scientific name that you would like to download images for, and the minimum number of images that you would like to request.

```bash
uv run main.py
```

## Warnings

1. This program calls the GBIF API and then downloads images based on the url's that data providers have associated with their records. This means that you will be calling and downloading data from url's that you will not know ahead of time. 
2. Images published to GBIF have a multitude of licenses. It is up to the user to ensure that they comply with any licenses or restrictions associated with the images they download.
