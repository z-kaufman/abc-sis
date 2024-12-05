import csv
import logging
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup

_log = logging.getLogger(__name__)

data_type = 'list'
MOUNTAIN_TIMEZONE = ZoneInfo("America/Denver")
UNITS = "µg/m³"

url = "https://www.iqair.com/us/usa/utah/salt-lake-city"


def get_robots_txt(url):
    robots_url = f"{url}/robots.txt"
    headers = {'User-Agent': 'NREL research'}
    response = httpx.get(robots_url, headers=headers)
    if response.status_code == 404:  # noqa: PLR2004
        return None
    elif response.status_code == 200:  # noqa: PLR2004
        return response.text
    else:
        return SystemExit(response)


def scrape_website(url: str, data_type: str) -> list | str:
    # get_robots_txt(url)
    headers = {'User-Agent': 'NREL research'}
    # Send a GET request to the URL
    response = httpx.get(url, headers=headers)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    if data_type == 'list':
        data = find_substring_and_context(soup.get_text(), 'PM2.5Particulate')

        if data is not None:
            data = data.split(f" {UNITS}")
            # Remove any extra data beyond the last instance of the split
            del data[6:]

            # Function to extract metrics
            # This gives me the creeps. It's so vulnerable to any change of the IQAir website
            def extract_metric(string):
                # Find the position where the first lowercase letter appears after an uppercase sequence
                # regex written by Perplexity.ai
                match = re.search(r"([A-Z₃₂]+(?:\d*\.?\d*)?)([A-Z][a-z])", string)
                if match:
                    return match.group(1)
                return None

            # Extract metrics from data string using the function
            metrics_list = [extract_metric(item) for item in data]
            values_list = [float(re.search(r"([\d,.]+)$", item).group(1).replace(',', '')) for item in data]
        else:
            raise SystemExit("No text returned from website")
        return metrics_list, values_list
    elif data_type == 'raw':
        data = soup.get_text()
        return data
    else:
        raise SystemExit("Incorrect or no desired data type provided. Must be either 'raw' or 'list'.")


def find_substring_and_context(long_string: str, substring: str, context_length: int = 200) -> str | None:
    """This is suuuuuuuper hacky and brittle! However, IQAir has not let us use their API for research purposes,
    so we are scraping their website like this as a workaround.

    This function reads a string, finds a substring within it, and returns it and an arbitrary number of additional
    characters. The additional characters is the only way we're grabbing the data. There are no quality checks.
    If the source of the long string changes, this may return unintended strings.
    """
    # Find the starting index of the substring
    start_index = long_string.find(substring)

    # If the substring is not found, return None
    if start_index == -1:
        return None

    # Calculate the end index for the context
    end_index = start_index + len(substring) + context_length

    # Ensure the end index doesn't exceed the string length
    end_index = min(end_index, len(long_string))

    # Extract the substring and its context
    result = long_string[start_index:end_index]

    return result


def save_to_txt(data, filename):
    with open(filename, 'w') as f:
        f.write(data)


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
    metrics_list = [f"{x}{UNITS}" for x in metrics_list]
    metrics_list.insert(0, "Timestamp")

    return metrics_list, values_list


# After scraping
if data_type == 'raw':
    data = scrape_website(url, data_type)
    save_to_txt(data, f"test_text_{datetime.now(MOUNTAIN_TIMEZONE)}.txt")
elif data_type == 'list':
    # Call the scraping function
    metrics_list, values_list = scrape_website(url, data_type)
    formatted_metrics, formatted_values = organize_for_csv(metrics_list, values_list)
    save_list_to_csv(formatted_metrics, formatted_values, "aqi_data_v5.csv")
