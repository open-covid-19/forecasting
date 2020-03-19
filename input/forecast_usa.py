import os
import sys
import warnings
from pathlib import Path
from joblib import Parallel, delayed
from multiprocessing import cpu_count

import pandas as pd
from tqdm import tqdm

from utils import get_outbreak_mask, forecast, plot_estimate, plot_forecast

# Establish root of the project
ROOT = Path(os.path.dirname(__file__)) / '..'

# Parse parameters
predict_window = 3
DATAPOINT_COUNT_MIN = 10

# Read data from the open COVID-19 dataset
df = pd.read_csv('https://raw.githubusercontent.com/open-covid-19/data/master/output/usa.csv')
df['Confirmed'] = df['Confirmed'].astype(float)
df['Deaths'] = df['Deaths'].astype(float)
df = df.set_index('Date')

forecast_columns = [
    'ForecastDate',
    'Date',
    'Region',
    'Estimated',
    'Confirmed',
    'ForecastChart',
]
forecast_df = pd.DataFrame(columns=forecast_columns).set_index(['Region', 'Date'])

# Loop through all known regions
for key in tqdm(list(sorted(df['Region'].unique()))):

    # Filter dataset
    cols = ['Region', 'Confirmed']
    # Get data only for the selected country
    region = df[df['Region'] == key][cols]
    # Get data only after the outbreak begun
    region = region[get_outbreak_mask(region)]
    # Early exit: no outbreak found
    if not len(region): continue
    # Get a list of dates for existing data
    date_range = map(
        lambda datetime: datetime.date().isoformat(),
        pd.date_range(region.index[0], region.index[-1])
    )

    # Forecast date is equal to the date of the last known datapoint, unless manually supplied
    forecast_date = region.index[-1]
    region = region[region.index <= forecast_date]

    # Early exit: If there are less than DATAPOINT_COUNT_MIN datapoints
    if len(region) < DATAPOINT_COUNT_MIN: continue

    # Define the subfolder that will hold the output assets
    forecast_chart = ROOT / 'output' / 'charts' / ('%s_US_%s.svg' % (forecast_date, key))

    # Perform forecast
    forecast_data = forecast(region['Confirmed'], predict_window)

    # Output charts as SVG files
    plot_forecast(forecast_chart, region['Confirmed'], forecast_data)

    # Aggregate forecast data
    for idx in forecast_data.index:
        forecast_df.loc[(key, idx), 'ForecastDate'] = forecast_date
        forecast_df.loc[(key, idx), 'Estimated'] = '%.03f' % forecast_data[idx]
        forecast_df.loc[(key, idx), 'ForecastChart'] = forecast_chart.relative_to(ROOT / 'output')
    for idx in region['Confirmed'].index:
        forecast_df.loc[(key, idx), 'Confirmed'] = int(region.loc[idx, 'Confirmed'])

# Save output to CSV
forecast_df = forecast_df.reset_index().sort_values(['ForecastDate', 'Region'])
forecast_df[forecast_columns].to_csv(ROOT / 'output' / 'usa.csv', index=False)