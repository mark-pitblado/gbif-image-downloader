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
