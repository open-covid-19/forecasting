import datetime
from pathlib import Path

import numpy as np
import pandas
from pandas import DataFrame
from scipy import optimize

import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

# Helper function used to filter out uninteresting dates
def get_outbreak_mask(data: DataFrame, threshold: int = 10):
    ''' Returns a mask for > N confirmed cases '''
    return data['Confirmed'] > threshold

# Define prediction model
def logistic_function(X: float, a: float, b: float, c: float):
    ''' a * e^(-b * e^(-cx)) '''
    return a * np.exp(-b * np.exp(-c * X))

def forward_indices(indices: list, window: int):
    ''' Adds `window` indices to a list of dates '''
    date_indices = [datetime.date.fromisoformat(date) for date in indices]
    for _ in range(window): date_indices.append(date_indices[-1] + datetime.timedelta(days=1))
    return [date.isoformat() for date in date_indices]

# Main work function for each subset of data
def forecast(data: pandas.Series, window: int):
    '''
    Perform a forecast of `window` days past the last day of `data`, including a model estimate of
    all days already existing in `data`.
    '''

    # Some of the parameter fittings result in overflow
    np.seterr(all='ignore')

    # Perform a simple fit of all available data up to this date
    X, y = list(range(len(data))), data.tolist()
    # Providing a reasonable initial guess is crucial for this model
    params, _ = optimize.curve_fit(logistic_function, X, y, maxfev=int(1E6), p0=[max(y), np.median(X), .1])

    # Append N new days to our indices
    date_indices = forward_indices(data.index, window)

    # Perform projection with the previously estimated parameters
    projected = [logistic_function(x, *params) for x in range(len(X) + window)]
    return pandas.Series(projected, index=date_indices, name='Projected')

def plot_estimate(fname: str, data: pandas.Series, estimate: pandas.Series = None):
    ax = data.plot(kind='bar', figsize=(16, 8), grid=True)
    if estimate is not None:
        ax.plot(data.index, estimate[data.index], color='red', label='Estimate')
    ax.legend()
    ax.get_figure().tight_layout()
    ax.get_figure().savefig(fname)
    plt.close(ax.get_figure())

def plot_forecast(fname: str, data: pandas.Series, estimate: pandas.Series):

    # Replace all the indices from data with zeroes in our projected data
    projected = estimate.copy()
    projected[data.index] = 0

    # Add new date indices to the original data and fill them with zeroes
    data = data.copy()
    for index in sorted(set(estimate.index) - set(data.index)):
        data.loc[index] = 0

    df = DataFrame({'Confirmed': data, 'Projected': projected})
    ax = df.plot(kind='bar', figsize=(16, 8), grid=True)
    ax.plot(estimate.index, estimate, color='red', label='Estimate')
    ax.legend()
    ax.get_figure().tight_layout()
    ax.get_figure().savefig(fname)
    plt.close(ax.get_figure())

def dataframe_to_json(data: DataFrame, path: Path, **kwargs):
    ''' Saves a DataFrame into a UTF-8 encoded JSON file '''
    with open(path, 'w', encoding='UTF-8') as file:
        data.to_json(file, force_ascii=False, **kwargs)

def dataframe_output(data: DataFrame, root: Path, name: str):
    '''
    This function performs the following steps:
    1. Sorts the dataset by date and country / region
    2. Outputs dataset as CSV and JSON to output/<name>.csv and output/<name>.json
    '''
    # Make sure the data has no index
    data = data.reset_index()

    # Infer pivot columns depending on whether this is country-level or region-level data
    pivot_columns = ['CountryCode', 'CountryName']
    if 'Region' in data.columns: pivot_columns = ['Region'] + pivot_columns

    # Chart columns are relative paths to image files
    chart_columns = ['ForecastChart']

    # Core columns are those that appear in all datasets
    core_columns = \
        ['ForecastDate', 'Date'] + pivot_columns + ['Estimated', 'Confirmed'] + chart_columns

    # Make sure the dataset is properly sorted
    data = data[core_columns].sort_values(['ForecastDate', pivot_columns[0]])

    # Make sure the core columns have the right data type
    data['ForecastDate'] = data['ForecastDate'].astype(str)
    data['Date'] = data['Date'].astype(str)
    data['Estimated'] = data['Estimated'].astype(float)
    data['Confirmed'] = data['Confirmed'].astype(float).astype('Int64')
    for pivot_column in pivot_columns:
        data[pivot_column] = data[pivot_column].astype(str)
    for chart_column in chart_columns:
        data[chart_column] = data[chart_column].astype(str)

    # Output dataset to CSV and JSON files
    data.to_csv(root / 'output' / ('%s.csv' % name), index=False)
    dataframe_to_json(data, root / 'output' / ('%s.json' % name), orient='records')
