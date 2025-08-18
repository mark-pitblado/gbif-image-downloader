# GBIF Image Downloader

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

## Configuration

All configuration is optional, as you will be prompted for the values the program needs when run. However, if you are going to run the tool repeatedly, it will save you time to configure the values.

Values are configured via an `.env` file, placed in the root of the directory. An example is provided below. If any value has spaces, it will need to be enclosed in quotations. If you do not wish to use a value, you can exclude it entirely from the file (in other words, none are required).

```env
GBIF_USERNAME=your-username
GBIF_PASSWORD=your-password
GBIF_NOTIFICATION_EMAIL=email@example.com
COLLECT_STATISTICS=False
APPROVED_PUBLISHERS=[]
```

| Variable | Usage |
| -------- | ----- |
| GBIF_USERNAME | Your gbif username. Required to make a download request. |
| GBIF_PASSWORD | Your gbif password. Required to make a download request. Note, if you include this value in the `.env` file, make sure to keep the `.env` safe. |
| GBIF_NOTIFICATION_EMAIL | When you finish running the tool, GBIF will send an email to this address with a DOI for the records of the images that you used. |
| COLLECT_STATISTICS | Most users will not want to enable this. This is intended for researchers who wish to see the percentage of valid links and license information.
| APPROVED_PUBLISHERS | If you wish to limit requests to approved publishers, put the publishers UUID in this list. |

## Usage

Run the following from the terminal. The program will ask for the scientific name that you would like to download images for, and the minimum number of images that you would like to request.

```bash
uv run main.py
```

## Warnings

1. This program calls the GBIF API and then downloads images based on the url's that data providers have associated with their records. This means that you will be calling and downloading data from url's that you will not know ahead of time. 
2. Images published to GBIF have a multitude of licenses. It is up to the user to ensure that they comply with any licenses or restrictions associated with the images they download.
