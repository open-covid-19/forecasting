import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize

import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

# Helper function used to filter out uninteresting dates
def get_outbreak_mask(data: pd.DataFrame, threshold: int = 10):
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
def forecast(data: pd.Series, window: int):
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
    return pd.Series(projected, index=date_indices, name='Projected')

def plot_estimate(fname: str, data: pd.Series, estimate: pd.Series):
    ax = data.plot(kind='bar', figsize=(16, 8), grid=True)
    ax.plot(data.index, estimate[data.index], color='red', label='Estimate')
    ax.legend()
    ax.get_figure().tight_layout()
    ax.get_figure().savefig(fname)
    plt.close(ax.get_figure())

def plot_forecast(fname: str, data: pd.Series, estimate: pd.Series):

    # Replace all the indices from data with zeroes in our projected data
    projected = estimate.copy()
    projected[data.index] = 0

    # Add new date indices to the original data and fill them with zeroes
    data = data.copy()
    for index in sorted(set(estimate.index) - set(data.index)):
        data.loc[index] = 0

    df = pd.DataFrame({'Confirmed': data, 'Projected': projected})
    ax = df.plot(kind='bar', figsize=(16, 8), grid=True)
    ax.plot(estimate.index, estimate, color='red', label='Estimate')
    ax.legend()
    ax.get_figure().tight_layout()
    ax.get_figure().savefig(fname)
    plt.close(ax.get_figure())
