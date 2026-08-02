# Linear Regression — STX40 Price Forecast

## Overview
This notebook (`Liner_Regression.ipynb`) is a standalone, single-cell script that fetches (or simulates) historical STX40 ETF price data and fits a simple linear regression model to forecast future prices. It appears to be an earlier/exploratory version of the regression workflow later incorporated into "Part A" of `assignment4.ipynb`.

## What it does
1. **Fetch data** — calls the Alpha Vantage `TIME_SERIES_DAILY` endpoint for STX40, trying multiple symbol formats (`STX40.JO`, `JSE:STX40`, `STX40`) with retry/backoff.
2. **Fallback simulation** — if no live data is returned, generates 1,000 days of synthetic price history using a seeded random walk (`numpy.random.seed(42)`), starting at a price of 5000.
3. **Data preparation** — converts the fetched/simulated data into a `pandas` DataFrame, parses OHLCV columns, sorts by date, and keeps the most recent 1,500 records.
4. **Regression** — fits `sklearn.linear_model.LinearRegression` on closing price vs. ordinal date.
5. **Visualization** — plots actual close price vs. the fitted regression line.
6. **Forecast** — prints the model's slope and intercept, and predicts the STX40 price 2 years from today.

## Requirements
- Python 3 with: `pandas`, `numpy`, `matplotlib`, `seaborn`, `requests`, `scikit-learn`, `IPython`

## How to Run
1. Open in Jupyter and run the single cell.
2. Console output logs each symbol attempt and whether real or simulated data was used.
3. A chart of actual vs. predicted price is displayed, followed by the printed regression coefficients and 2-year price forecast.

## Notes
- Uses a hardcoded, free-tier Alpha Vantage API key with tight rate limits — simulated data is a reliable fallback if calls fail.
- This is a minimal, exploratory script rather than a full report; for the complete written analysis (performance metrics, technical indicators, qualitative assessment, and investment recommendation), see `assignment4.ipynb`.
