# Open COVID-19 Forecasting
This repository contains forecasting data of the next 3 days for all countries
and regions which contain at least 10 days of data since reporting 10 confirmed
COVID-19 positive cases or more.

### Understand the data
The dataset used to perform the forecasting is the [Open COVID-19 Dataset][1],
which contains total confirmed positive cases and total fatal cases for all
reporting countries as well as subregions of USA and China.

The output of the forecasting model are the following datasets:
* [World](output/world.csv):
  - **ForecastDate**: ISO 8601 date (YYYY-MM-DD) of the last known datapoint at the time of forecast
  - **Date**: ISO 8601 date (YYYY-MM-DD) of the datapoint
  - **CountryCode**: 2-letter ISO 3166-1 code of the country
  - **CountryName**: American English name of the country
  - **Confirmed**: total number of cases confirmed after positive test
  - **Estimated**: total number of cases estimated from forecasting model
  - **ForecastChart**: relative path to an SVG file containing a chart of the estimates

* [USA](output/usa.csv):
  - **ForecastDate**: ISO 8601 date (YYYY-MM-DD) of the last known datapoint at the time of forecast
  - **Region**: 2-letter state code (e.g. CA, FL, NY)
  - **Date**: ISO 8601 date (YYYY-MM-DD) of the datapoint
  - **CountryCode**: 2-letter ISO 3166-1 code of the country
  - **CountryName**: American English name of the country
  - **Confirmed**: total number of cases confirmed after positive test
  - **Estimated**: total number of cases estimated from forecasting model
  - **ForecastChart**: relative path to an SVG file containing a chart of the estimates

Only the latest version of the datasets is kept, but the charts are prefixed by
forecast date and never deleted.

### Forecasting Model
The forecasting is done by fitting the data to a specialized logistic curve,
called [Gompertz function][2]. For a walkthrough of why this was chosen over
other potential models, see the [relevant analysis][3].

### Updating the data
To update the forecast with the latest data, run the following commands:
```sh
# Install dependencies
pip install -r requirements.txt
# Update world forecast
python input/forecast_world.py
# Update USA forecast
python input/forecast_usa.py
# Build map of all charts
python input/build_json.py
```

[1]: https://github.com/open-covid-19/data
[2]: https://en.wikipedia.org/wiki/Gompertz_function
[3]: https://github.com/open-covid-19/analysis/blob/master/logistic_modeling.ipynb