# Assignment 1 — Personal Financial / Retirement Plan (GM XIPU, 220123773)

## Overview
This Excel workbook (`GM_XIPU_-_220123773_-_Assignment_1.xlsx`) is a 41-year personal financial planning model (2025–2065), projecting income, expenses, savings, and investment growth from age 25 to retirement at 65. It also layers in the financial impact of major life events.

## Sheets

| Sheet | Purpose |
|---|---|
| **Introduction** | Title/overview page |
| **Assumptions** | Core input variables: start age (25), retirement age (65), start/end years (2025–2065), income (R200,000), expenses (R100,000), savings rate (20%), income growth (6%/yr), expense growth (5%/yr), investment return (7%/yr), inflation (5%/yr) |
| **Year Plan** | Year-by-year projection (2025–2065) of income, savings, cumulative investment balance, investment returns, and total savings, compounding annually at the assumed growth rates |
| **Inc VS Exp_Chart** | Chart visualizing income vs. expenses over time |
| **Life Events** | One-off and recurring life expenses layered onto the base plan: home renovation (2025, R50k once-off), new car (2027, R66k/yr for 5 years), lobola/traditional marriage payment (2030, R70k once-off), children (2031 onward, R36k/yr recurring) |
| **Updated Expenses** | Recalculates total expenses per year including the Life Events costs on top of the base expense projection |
| **Visualisation** | Supporting chart(s) for the updated expense/income picture |
| **Net Cash** | Year-by-year net cash flow (income minus updated total expenses), which turns negative in some years (e.g. 2030, due to the lobola payment) before recovering |
| **Net Chart** | Chart of net cash flow over time |
| **Conclusion** | Summary and closing commentary on the plan |

## Key Takeaways from the Model
- Base savings rate is 20% of income, growing income at 6%/year against 5%/year expense growth, compounded with a 7%/year investment return.
- Life events (renovation, car, lobola, children) materially affect the plan — most notably causing a **negative net cash year in 2030** from the lobola payment.
- By 2065 (age 65), the model projects total investments in the tens of millions of Rand, driven by compounding investment returns over the 41-year horizon.

## How to Use
1. Open in Excel (or Google Sheets/LibreOffice Calc).
2. Adjust inputs on the **Assumptions** sheet to explore different scenarios (growth rates, savings rate, retirement age, etc.).
3. Review **Year Plan**, **Updated Expenses**, and **Net Cash** to see how changes ripple through the projection.
4. Charts on **Inc VS Exp_Chart**, **Visualisation**, and **Net Chart** update automatically with the underlying data.

## Notes
- All figures are in South African Rand (ZAR).
- This is a deterministic, single-scenario model — see `GM_XIPU_-_220123773_-_ASS_2.xlsm` for the Monte Carlo (probabilistic) version of this analysis.
