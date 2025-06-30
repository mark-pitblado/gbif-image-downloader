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
    plt.pie(x=values, labels=labels, autopct="%.0f%%")
    plt.show()
