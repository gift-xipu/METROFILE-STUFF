# Assignment 2 — Monte Carlo Retirement Simulation (GM XIPU, 220123773)

## Overview
This macro-enabled Excel workbook (`GM_XIPU_-_220123773_-_ASS_2.xlsm`) extends the deterministic financial plan from Assignment 1 into a **Monte Carlo simulation**, modeling uncertainty in income growth, expense growth, investment returns, and inflation over a 41-year working life (2025–2065), then running many randomized trials to assess the probability of reaching a retirement savings goal.

## Sheets

| Sheet | Purpose |
|---|---|
| **Introduction** | Title/overview page |
| **Initial Assumptions** | Base-case starting conditions: start age 25, retirement age 65, start year 2025, retirement year 2065, initial income R200,000, initial expenses R136,000, initial savings R64,000, initial investments R64,000 |
| **Monte Carlo Parameters** | Distribution parameters (mean, standard deviation, min, max) for the four random variables:<br>• Income Growth Rate — mean 6%, σ 2%, range 2–12%<br>• Expense Growth Rate — mean 5%, σ 1.2%, range 2–8%<br>• Investment Return — mean 7%, σ 4%, range −10% to 25%<br>• Inflation Rate — mean 5%, σ 1%, range 2–8% |
| **Simulations** | Sample of randomly drawn rates for a given trial (used to feed the single-simulation projection) |
| **Single Simulation** | One full 2025–2065 year-by-year projection (income, expenses, savings, investment balance, investment returns, total investment) using one draw of random rates — illustrates what a single simulated life-path looks like |
| **Results** | Output of ~200+ Monte Carlo trials (likely driven by a VBA macro, given the `.xlsm` format). For each run: the randomly drawn growth/return/inflation rates, final income/expenses/savings/investment return/investment value at retirement (age 65), and whether the **Retirement Goal of R5,000,000** was achieved (Yes/No) |
| **Chart** | Visualization of simulation outcomes (e.g. distribution of final investment values, or goal-achievement rate) |
| **Conculsion** *(sic)* | Summary and conclusions drawn from the simulation results |

## Key Takeaways
- The model runs many randomized 41-year trials (varying income growth, expense growth, investment returns, and inflation each run) to capture a *range* of possible retirement outcomes rather than a single deterministic forecast.
- The target is a **R5,000,000 retirement investment goal**; the "Goal Achieved?" column flags whether each trial's final investment balance clears that bar.
- Outcomes vary widely between trials — some produce final investment balances well over R2 million, while unlucky draws (e.g. negative investment returns or high expense growth) can produce negative net investment positions.

## Requirements
- Microsoft Excel with macros enabled (`.xlsm`) — the simulation trials are generated via VBA.

## How to Use
1. Open in Excel and **enable macros** when prompted.
2. Review/adjust the distribution parameters on **Monte Carlo Parameters**.
3. Re-run the simulation macro (if provided) to regenerate the **Results** table with a fresh batch of random trials.
4. Check the **Chart** and **Results** sheets to see the spread of outcomes and the proportion of trials meeting the R5,000,000 retirement goal.

## Notes
- All figures are in South African Rand (ZAR).
- Companion file: `GM_XIPU_-_220123773_-_Assignment_1.xlsx` contains the single-scenario (non-probabilistic) version of this financial plan.
