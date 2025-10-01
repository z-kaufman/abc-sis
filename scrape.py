import csv
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop, wait

# strftime didn't work with my whenever object :(
# from whenever import Instant

_log = logging.getLogger(__name__)

URL = "https://www.iqair.com/us/usa/utah/salt-lake-city"
UNITS = "µg/m³"
MOUNTAIN_TIMEZONE = ZoneInfo("America/Denver")
OUTPUT_FILE_NAME = "aqi_data_v7.csv"


def main():
    metrics_list, values_list = get_data(url=URL)
    formatted_metrics_list, formatted_values_list = organize_for_csv(metrics_list, values_list)
    save_list_to_csv(formatted_metrics_list, formatted_values_list, OUTPUT_FILE_NAME)


@retry(wait=wait.wait_fixed(3) + wait.wait_random(0, 2), stop=stop.stop_after_attempt(7))
def get_data(url):
    headers = {'User-Agent': 'NREL research test'}
    # Send a GET request to the URL
    response = httpx.get(url, headers=headers)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')


    # Use a web inspector to find the right table
    table = soup.find('table', title="Air pollutants")
    if not table:
        raise ValueError("Could not find the 'Air pollutants' table on the page.")

    rows = table.find_all('tr')

    metrics_list = []
    values_list = []
    for row in rows:
        metric = row.find(class_="lgsm:base-text font-body-s text-gray-900").text.strip()
        value = row.find(class_="font-body-m-medium text-gray-900").text.strip()

        if metric.startswith('O'):
            metric = metric[:2]
        elif metric.startswith('PM2.5'):
            metric = metric[:5]
        elif metric.startswith('PM10'):
            metric = metric[:4]
        elif metric.startswith(('NO', 'SO')):
            metric = metric[:3]
        elif metric.startswith('CO'):
            metric = metric[:2]

        print(f"Metric: {metric}, Value: {value}")

        if value:
            # _log.debug(value.text.strip())
            values_list.append(value)
            metrics_list.append(metric)

    return metrics_list, values_list


def organize_for_csv(metrics_list, values_list):
    # Format the datetime to include only up to the hour
    mountain_time = datetime.now(MOUNTAIN_TIMEZONE)
    formatted_datetime = str(mountain_time.strftime("%Y-%m-%d %H:00:00"))

    # Add datetime (to hour precision) at beginning of data list
    values_list.insert(0, formatted_datetime)

    # Add 0.0 for any entries that aren't provided by the website'
    num_desired_data_items = 7
    while len(values_list) < num_desired_data_items:
        values_list.append(0.0)

    # Format column headers
    metrics_list = [f"{x} {UNITS}" for x in metrics_list]
    metrics_list.insert(0, "Timestamp")

    return metrics_list, values_list


def save_list_to_csv(formatted_metrics, formatted_values, output_file):
    write_header = True
    if Path(output_file).exists():
        write_header = False

    # Write to CSV
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(formatted_metrics)  # Write header
        writer.writerow(formatted_values)


if __name__ == "__main__":
    main()
