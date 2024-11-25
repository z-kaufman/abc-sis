import csv
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from bs4 import BeautifulSoup

_log = logging.getLogger(__name__)

data_type = 'list'
MOUNTAIN_TIMEZONE = ZoneInfo("America/Denver")

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
        data = find_substring_and_context(soup.get_text(), 'PollutantsConcentration')

        if data is not None:
            data = data.split("✓")[0]
            data_as_list = data.split()
            data_as_list = [x.split("!")[0] for x in data_as_list[1:]]
            _log.debug(data_as_list)
        else:
            raise SystemExit("No text returned from website")
        return data_as_list
    elif data_type == 'raw':
        data = soup.get_text()
        return data
    else:
        raise SystemExit("Incorrect or no desired data type provided. Must be either 'raw' or 'list'.")

    # Extract data using Beautiful Soup methods
    # Example: Find all paragraph tags
    # tables = soup.find_all('table', class_='aqi-overview-detail__main-pollution-table')
    # data = soup.prettify()
    # text = soup.get_text()
    # pm_25 = soup.find_all('PollutantsConcentration')
    # print(pm_25)
    # raise SystemExit()
    # print(soup.prettify())

    # Process and store the extracted data
    # data = [p.text for p in paragraphs]
    # data = [table.text for table in tables]
    # print(data)

    # return data_as_list


def find_substring_and_context(long_string: str, substring: str, context_length: int = 100) -> str | None:
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


# def save_to_csv(data, filename):
#     with open(filename, 'w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerows(data)


# def save_to_json(data, filename):
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)


def save_to_txt(data, filename):
    with open(filename, 'w') as f:
        f.write(data)


def save_list_to_csv(formatted_data, output_file):
    # Write to CSV
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Mountain time", "Pollutant", "Concentration"])  # Write header
        writer.writerows(formatted_data)


def organize_for_csv(input_list):
    # Ensure the list has an even number of elements
    if len(input_list) % 2 != 0:
        input_list.append("")  # Add an empty string if odd number of elements

    # Pair the elements to make a 2-column list for writing to csv
    paired_data = list(zip(input_list[0::2], input_list[1::2]))

    # Format the datetime to include only up to the hour
    mountain_time = datetime.now(MOUNTAIN_TIMEZONE)
    formatted_datetime = mountain_time.strftime("%Y-%m-%d %H:00:00")

    # Adding the current datetime to each tuple
    formatted_data = [(formatted_datetime, x[0], x[1]) for x in paired_data]

    return formatted_data


# Call the scraping function
scraped_data = scrape_website(url, data_type)

formatted_data = organize_for_csv(scraped_data)

# After scraping
if data_type == 'raw':
    save_to_txt(scraped_data, f"test_text_{datetime.now()}.txt")
# save_to_csv(scraped_data, f"aqi_{datetime.now()}.csv")
# save_to_json(scraped_data, 'first_test.json')
# save_to_csv(scraped_data, 'string_test.txt')
elif data_type == 'list':
    save_list_to_csv(formatted_data, "aqi_data.csv")
