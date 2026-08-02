# Assignment 4 — STX40 ETF Investment Analysis

## Overview
This Jupyter notebook (`assignment4.ipynb`) is a two-part investment analysis assignment centered on the **Satrix 40 ETF (STX40)**, a South African equity index tracker. It combines quantitative analysis (price data, regression, performance/technical metrics) with a qualitative investment recommendation for a R100,000 investment.

## Structure

### Part A
- Fetches daily price data for STX40 from the Alpha Vantage API (`TIME_SERIES_DAILY`), trying several ticker formats (`STX40.JO`, `JSE:STX40`, `STX40`).
- Falls back to **simulated price data** (seeded random walk) if the API call fails or the key is rate-limited.
- Fits a `sklearn` **Linear Regression** model of closing price vs. date (ordinal) and plots actual vs. predicted price.
- Projects a price 2 years into the future using the fitted model.

### Part B — Satrix 40 ETF (STX40) Qualitative Analysis
1. **Data Collection** — re-fetches/generates the same daily price series and displays the most recent trading days (OHLCV).
2. **Performance Analysis** — computes:
   - Current price, 1-month and 1-year returns
   - 3-year and 5-year annualized returns
   - Annual volatility
   - Maximum drawdown
   - Sharpe ratio (using a 7% risk-free rate assumption)
3. **Visualizations & Interpretation**
   - Figure 1: Price history
   - Figure 2: Rolling 1-year returns
   - Figure 3: Historical drawdowns
   - Figure 4: Monthly returns heatmap
4. **Technical Analysis**
   - Figure 5: 14-day Relative Strength Index (RSI)
   - Figure 6: MACD (12, 26, 9)
5. **Qualitative Analysis**
   - Key strengths/advantages of STX40
   - Key challenges/disadvantages
   - Long-term strategic considerations for investors
6. **Investment Recommendation for R100,000**
   - Suggested allocation
   - Implementation strategy
   - Elements to monitor going forward
7. **Conclusion and Summary** — key findings and overall assessment

## Requirements
- Python 3, with: `pandas`, `numpy`, `matplotlib`, `seaborn`, `requests`, `scikit-learn`, `IPython`
- An Alpha Vantage API key (a demo/example key is hardcoded in the notebook — replace with your own for live data; the notebook auto-generates realistic simulated data if no live data is available, so it will still run without one)

## How to Run
1. Open the notebook in Jupyter or VS Code.
2. Run all cells top to bottom. If the Alpha Vantage API rate-limits or the symbol isn't found, the notebook automatically substitutes simulated daily price data so downstream analysis and charts still work.
3. Review the generated charts and tables inline, alongside the written interpretation/qualitative sections.

## Notes
- The hardcoded API key is a free-tier Alpha Vantage key with strict rate limits (5 calls/minute, 25/day); expect the simulated-data fallback to trigger often.
- All monetary figures are in South African Rand (ZAR).
