# abc-sis

Repository for ABC-SIS project work

## Local installation/development

Clone the repository via git:

```terminal
git clone https://github.com/vtnate/abc-sis.git
```

- [Uv](https://docs.astral.sh/uv/) is used to manage the project & dependencies (and may be used to [manage Python](https://docs.astral.sh/uv/guides/install-python/) if you want). After cloning, ensure you have
  [uv installed](https://docs.astral.sh/uv/getting-started/installation/), then run `uv sync` to install the package and all development dependencies.
    - Some Windows developers have reported version conflicts using the default strategy. If this occurs, consider changing the [resolution strategy](https://docs.astral.sh/uv/concepts/resolution/#resolution-strategy) using `uv sync --resolution=lowest-direct`
- Activate [pre-commit](https://pre-commit.com/) (only required once, after cloning the repo) with: `uv run pre-commit install`. On your first commit it will install the pre-commit environments, then run pre-commit hooks at every commit.
- Before pushing changes to Github, run pre-commit on all files in the repo with `uv run pre-commit run -a` to highlight any typos/linting/formatting errors that will cause CI to fail.
- Pycharm users may need to add Ruff as a [3rd-party plugin](https://docs.astral.sh/ruff/editors/setup/#via-third-party-plugin) or install it as an [external tool](https://docs.astral.sh/ruff/editors/setup/#pycharm) to their IDE to ensure linting & formatting is consistent.

## AQI scraper Usage

There are 3 sources being scraped for air quality data:
1. IQAir
2. Air Utah
3. Air Quality Open Data

Air Utah and Air Quality Open Data have APIs, while IQAir uses a scraper.

There is a GitHub Actions workflow that runs the `scrape.py` script every hour for the IQAir website. It outputs an `aqi_data...` versioned csv file which is automatically updated in this repo by the Action.

The script can be run by hand with `uv run scrape.py`

The script scrapes the IQair website, reads the text, and extracts the Salt Lake City pollutant data to a csv file.
IQAir does have an [API available](https://www.iqair.com/air-quality-monitors/api) but they charge a subscription for the pollutant concentrations we are interested in.
Using the API is strongly preferred over this scraper, but is currently unfeasable due to the subscription cost for this research project.

An example of the output is:

|      Timestamp      | PM2.5 µg/m³ | PM10 µg/m³ | O₃ µg/m³ | NO₂ µg/m³ | SO₂ µg/m³ | CO µg/m³ |
| :-----------------: | :---------: | :--------: | :------: | :-------: | :-------: | :------: |
| 2024-11-27 08:00:00 |     6.8     |    5.0     |   37.0   |   39.5    |    0.5    |  229.0   |

Air Utah (air.utah.gov) uses an RSS feed for Salt Lake City. This is likely the most reliable source of PM-2.5 data because it's an actual PM-2.5 measurement and is more reliable than the IQAir scraper.
Air Quality Open Data's PM-2.5 number is actually the "Now Cast" (https://en.wikipedia.org/wiki/NowCast_(air_quality_index)), which is calculated based on the last 12 hours of PM2.5 concentrations, weighting recent concentrations more heavily. It is not really possible to back-calculate PM2.5 concentration from Now Cast values because there are so many inputs (12 hours' worth).
