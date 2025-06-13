import requests


def is_valid_url(url: str) -> bool:
    """
    Checks if the url responds to a ping before downloading the data.
    """
    try:
        requests.head(url, timeout=3)
        return True
    except requests.ConnectionError:
        return False
