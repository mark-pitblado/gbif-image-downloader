"""
This module assembles graphs and statistics from API calls, keeping track of how many links were successful, and how many images have licenses.
"""

import matplotlib.pyplot as plt


def create_http_pie_chart(data: dict):
    """
    Creates a pie chart to visualize the percentage of each http code of image url requests. The input dictionary should have the request code as keys and the percentage as a value.
    """
    labels = data.keys()
    values = data.values()

    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return "{:.1f}%\n({v:d})".format(pct, v=val)

        return my_format

    plt.pie(x=values, labels=labels, autopct=autopct_format(values))
    plt.savefig("statistics/http-codes.png")


def image_license_described(data: dict) -> bool:
    """
    Determines whether an Audiovisual Media Description extension contains one or more of the following terms.
        1. rights
        2. UsageTerms
        3. Credit
    """
    try:
        if data[0]["license"] != "":
            return True
        return False
    except KeyError:
        try:
            if data[0]["rights"] != "":
                return True
            return False
        except KeyError:
            return False
